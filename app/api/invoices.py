# app/api/invoices.py
"""
Invoice Validation API Endpoints

Handles invoice upload, OCR extraction, validation, and report generation.
"""

import logging
import os
from pathlib import Path
from typing import Dict

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..schemas.invoice import ValidationResponse
from ..services.ai_extraction import analyze_invoice_with_gemini
from ..services.rule_engine import InvoiceValidator, validate_invoice
from ..utils.report_generator import generate_excel_report

# Logger
log = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/invoices", tags=["Invoices"])

# In-memory store for report file paths (in production, use Redis or database)
# Key: report_id, Value: file_path
report_store: Dict[str, str] = {}


@router.post("/validate", response_model=ValidationResponse)
async def validate_invoice_endpoint(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Validate an uploaded invoice PDF.

    Steps:
    1. Extract data from PDF using Google Gemini AI
    2. Query database for matching PO/SES
    3. Run all 10 validation rules
    4. Generate Excel report
    5. Return validation results

    Args:
        file: Uploaded PDF file
        db: Database session

    Returns:
        ValidationResponse: Complete validation results
    """
    try:
        # Validate file type
        if not file.filename.endswith(".pdf"):
            raise HTTPException(
                status_code=400, detail="Invalid file type. Only PDF files are allowed."
            )

        # Read file content
        file_content = await file.read()

        if len(file_content) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        log.info(f"Processing invoice file: {file.filename} ({len(file_content)} bytes)")

        # Step 1: Extract data from invoice using Google Gemini AI
        try:
            extraction_data = analyze_invoice_with_gemini(file_content)
            log.info(f"Extracted invoice data: {extraction_data.invoice_number}")
        except ValueError as e:
            log.error(f"Gemini extraction failed: {e}")
            error_message = str(e)
            # If the error already contains helpful instructions, use it as-is
            if "GEMINI_API_KEY" in error_message or "aistudio.google.com" in error_message:
                raise HTTPException(
                    status_code=500,
                    detail=error_message,
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to extract invoice data: {error_message}. Please ensure GEMINI_API_KEY is set correctly in your .env file.",
                )

        # Step 2: Query database for matching PO/SES
        po_found, ses_found, po, ses, checklist = validate_invoice(db, extraction_data)

        log.info(
            f"Database lookup - PO found: {po_found}, SES found: {ses_found}, "
            f"PO: {po.po_number if po else None}, SES: {ses.ses_number if ses else None}"
        )

        # Step 3: Run validation rules
        validator = InvoiceValidator(extraction_data, po, ses, checklist)
        results = validator.validate_all()

        # Determine overall status (fail if any rule fails)
        overall_status = "pass" if all(r.status.lower() == "pass" for r in results) else "fail"

        log.info(f"Validation complete - Overall status: {overall_status}")

        # Step 4: Generate Excel report
        report_path = generate_excel_report(
            extraction_data, results, overall_status, po_found, ses_found
        )

        # Store report path with a simple ID (invoice number + timestamp)
        import time

        report_id = f"{extraction_data.invoice_number}_{int(time.time())}"
        report_store[report_id] = report_path

        log.info(f"Report generated: {report_path} (ID: {report_id})")

        # Step 5: Return validation response
        response = ValidationResponse(
            extraction_data=extraction_data,
            linked_po_found=po_found,
            linked_ses_found=ses_found,
            results=results,
            overall_status=overall_status,
            report_id=report_id,
        )

        return response

    except HTTPException:
        raise
    except (ConnectionError, OperationalError) as e:
        # Handle database connection errors with helpful message
        error_msg = str(e)
        log.error(f"Database connection error: {error_msg}", exc_info=True)
        
        # Provide specific guidance based on error type
        if "Connection refused" in error_msg or "could not connect" in error_msg.lower():
            detail_msg = (
                "Cannot connect to PostgreSQL database. Please ensure PostgreSQL is running.\n\n"
                "To start PostgreSQL using Docker:\n"
                "  docker-compose up -d postgres\n\n"
                "Or if using local PostgreSQL:\n"
                "  sudo systemctl start postgresql  # Linux\n"
                "  brew services start postgresql   # macOS\n\n"
                "Verify your DATABASE_URL in .env is correct."
            )
        else:
            detail_msg = (
                f"Database connection failed: {error_msg}\n\n"
                "Please check:\n"
                "  1. PostgreSQL is running\n"
                "  2. DATABASE_URL in .env is correct\n"
                "  3. Database credentials are valid"
            )
        
        raise HTTPException(status_code=503, detail=detail_msg)
    except Exception as e:
        log.error(f"Error processing invoice: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing invoice: {str(e)}")


@router.get("/report/{report_id}")
async def get_report(report_id: str):
    """
    Download the Excel validation report.

    Args:
        report_id: The report ID returned from /validate endpoint

    Returns:
        FileResponse: Excel file download
    """
    if report_id not in report_store:
        raise HTTPException(status_code=404, detail="Report not found")

    report_path = report_store[report_id]

    # Check if file still exists
    if not os.path.exists(report_path):
        # Clean up stale entry
        del report_store[report_id]
        raise HTTPException(status_code=404, detail="Report file no longer available")

    return FileResponse(
        report_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=f"invoice_validation_report_{report_id}.xlsx",
    )

