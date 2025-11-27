# app/services/ai_extraction.py
"""
Real AI Service for Invoice Data Extraction using Google Gemini

This service uses Google Gemini 1.5 Flash to extract structured data
from invoice PDFs, including visual analysis for digital signatures and QR codes.
"""

import json
import logging
import os
from datetime import date
from decimal import Decimal
from typing import Optional

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from pydantic import ValidationError

from ..schemas.invoice import InvoiceExtraction, LineItem

# Logger
log = logging.getLogger(__name__)

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_OCR_MODEL = os.getenv("GEMINI_OCR_MODEL", "gemini-2.5-flash")

if not GEMINI_API_KEY:
    log.warning(
        "GEMINI_API_KEY not found in environment. Gemini extraction will fail."
    )

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def analyze_invoice_with_gemini(file_bytes: bytes) -> InvoiceExtraction:
    """
    Extract structured data from invoice PDF using Google Gemini 1.5 Flash.

    Args:
        file_bytes: The PDF file content as bytes

    Returns:
        InvoiceExtraction: Extracted invoice data

    Raises:
        ValueError: If API key is missing or extraction fails
        ValidationError: If Gemini output doesn't match expected schema
    """
    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY environment variable is not set. "
            "Please add it to your .env file."
        )

    try:
        # Initialize Gemini model (using configured model, default: gemini-2.5-flash)
        model = genai.GenerativeModel(GEMINI_OCR_MODEL)

        # Prepare the prompt
        prompt = """You are an AP Compliance Officer. Analyze this invoice PDF and extract the following information as a JSON object.

CRITICAL REQUIREMENTS:
1. Look for "Digitally Signed by" text or visual signature indicators - set has_digital_signature to true if found
2. Check if the document title/header says "Tax Invoice" - set is_tax_invoice accordingly
3. Look for IRN (Invoice Reference Number) and QR code - extract IRN if present, set qr_code_present to true if QR code is visible
4. Extract all line items with quantities, prices, and tax information

Return ONLY a valid JSON object matching this exact structure:
{
  "invoice_number": "string",
  "invoice_date": "YYYY-MM-DD",
  "vendor_name": "string",
  "po_number": "string",
  "total_amount": number,
  "tax_amount": number,
  "irn_number": "string or null",
  "qr_code_present": boolean,
  "vendor_gstin": "string or null",
  "has_digital_signature": boolean,
  "is_tax_invoice": boolean,
  "line_items": [
    {
      "description": "string",
      "quantity": number or null,
      "unit_price": number or null,
      "amount": number,
      "tax_rate": number or null,
      "tax_amount": number or null
    }
  ]
}

IMPORTANT:
- Extract dates in YYYY-MM-DD format
- Extract amounts as numbers (not strings)
- If a field is not found, use null for optional fields
- For has_digital_signature: Check for "Digitally Signed by" text or visual signature marks
- For is_tax_invoice: Check if document title/header contains "Tax Invoice" (not "Credit Note")
- For qr_code_present: Check if a QR code is visually present on the document
- Extract line_items array with all invoice line items if available

Return ONLY the JSON object, no additional text or markdown formatting."""

        # Upload PDF and generate content
        log.info("Sending PDF to Gemini for analysis...")
        
        # Use Gemini's file upload capability
        # Gemini 1.5 Flash supports direct PDF upload
        # Format: [text_prompt, {"mime_type": "application/pdf", "data": bytes}]
        response = model.generate_content(
            [
                prompt,
                {
                    "mime_type": "application/pdf",
                    "data": file_bytes
                }
            ]
        )

        # Extract JSON from response
        response_text = response.text.strip()
        
        # Clean up response (remove markdown code blocks if present)
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()

        log.info(f"Gemini response received: {len(response_text)} characters")

        # Parse JSON
        try:
            extracted_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            log.error(f"Failed to parse JSON from Gemini response: {e}")
            log.error(f"Response text: {response_text[:500]}")
            raise ValueError(f"Failed to parse JSON from Gemini response: {e}")

        # Convert to Pydantic model
        # Handle date conversion
        if "invoice_date" in extracted_data and isinstance(
            extracted_data["invoice_date"], str
        ):
            extracted_data["invoice_date"] = date.fromisoformat(
                extracted_data["invoice_date"]
            )

        # Convert amounts to Decimal
        for amount_field in ["total_amount", "tax_amount"]:
            if amount_field in extracted_data:
                extracted_data[amount_field] = Decimal(
                    str(extracted_data[amount_field])
                )

        # Convert line items amounts to Decimal
        if "line_items" in extracted_data and extracted_data["line_items"]:
            for item in extracted_data["line_items"]:
                for field in ["quantity", "unit_price", "amount", "tax_rate", "tax_amount"]:
                    if field in item and item[field] is not None:
                        item[field] = Decimal(str(item[field]))

        # Create LineItem objects
        line_items = None
        if "line_items" in extracted_data and extracted_data["line_items"]:
            line_items = [LineItem(**item) for item in extracted_data["line_items"]]

        # Create InvoiceExtraction object
        invoice_data = InvoiceExtraction(
            invoice_number=extracted_data.get("invoice_number", ""),
            invoice_date=extracted_data.get("invoice_date"),
            vendor_name=extracted_data.get("vendor_name", ""),
            po_number=extracted_data.get("po_number", ""),
            total_amount=extracted_data.get("total_amount", Decimal("0")),
            tax_amount=extracted_data.get("tax_amount", Decimal("0")),
            irn_number=extracted_data.get("irn_number"),
            qr_code_present=extracted_data.get("qr_code_present", False),
            vendor_gstin=extracted_data.get("vendor_gstin"),
            has_digital_signature=extracted_data.get("has_digital_signature", False),
            is_tax_invoice=extracted_data.get("is_tax_invoice", True),
            line_items=line_items,
        )

        log.info(
            f"Successfully extracted invoice data: {invoice_data.invoice_number} "
            f"(PO: {invoice_data.po_number}, Amount: {invoice_data.total_amount})"
        )

        return invoice_data

    except ValidationError as e:
        log.error(f"Validation error creating InvoiceExtraction: {e}")
        raise ValueError(f"Invalid data structure from Gemini: {e}")
    except (google_exceptions.InvalidArgument, google_exceptions.Unauthenticated, google_exceptions.PermissionDenied) as e:
        error_msg = str(e)
        if "API key" in error_msg or "API_KEY" in error_msg or "expired" in error_msg.lower() or "invalid" in error_msg.lower():
            log.error(f"Gemini API key error: {e}")
            raise ValueError(
                "Gemini API key is invalid or expired. Please check your GEMINI_API_KEY in the .env file. "
                "Get a new API key from https://aistudio.google.com/"
            )
        elif isinstance(e, google_exceptions.PermissionDenied):
            log.error(f"Gemini API permission denied: {e}")
            raise ValueError(
                "Gemini API permission denied. Please check your GEMINI_API_KEY has the necessary permissions. "
                "Get a new API key from https://aistudio.google.com/"
            )
        else:
            log.error(f"Gemini API error: {e}")
            raise ValueError(f"Gemini API error: {str(e)}")
    except Exception as e:
        log.error(f"Error extracting invoice with Gemini: {e}", exc_info=True)
        # Check if it's an API key related error in the message
        error_str = str(e).lower()
        if "api key" in error_str or "api_key" in error_str or "expired" in error_str:
            raise ValueError(
                "Gemini API key is invalid or expired. Please check your GEMINI_API_KEY in the .env file. "
                "Get a new API key from https://aistudio.google.com/"
            )
        raise ValueError(f"Failed to extract invoice data: {str(e)}")

