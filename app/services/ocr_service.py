# app/services/ocr_service.py
"""
Mock OCR Service for Invoice Data Extraction

This service simulates OCR extraction from PDF invoices.
In production, this would integrate with actual OCR services like:
- Tesseract OCR
- Google Cloud Vision API
- AWS Textract
- Azure Form Recognizer
"""

from datetime import date
from decimal import Decimal

from ..schemas.invoice import InvoiceExtraction


def mock_extract_invoice(file_content: bytes) -> InvoiceExtraction:
    """
    Mock OCR extraction function that returns hardcoded data
    matching the "Updater Services" invoice.

    Args:
        file_content: The PDF file content as bytes

    Returns:
        InvoiceExtraction: Extracted invoice data

    Note:
        This is a mock implementation. In production, this would:
        1. Parse the PDF file
        2. Extract text using OCR
        3. Use NLP/ML to identify fields
        4. Return structured data
    """
    # Hardcoded data matching the Updater Services invoice
    # Invoice No: 2533001202
    # Date: 2025-04-24
    # PO Number: 4802048544
    # Amount: 148061.00
    # Vendor: UPDATER SERVICES LTD
    # IRN/QR: Present

    return InvoiceExtraction(
        invoice_number="2533001202",
        invoice_date=date(2025, 4, 24),
        vendor_name="UPDATER SERVICES LTD",
        po_number="4802048544",
        total_amount=Decimal("148061.00"),
        tax_amount=Decimal("0.00"),  # Will be calculated based on tax rate
        irn_number="ABCD1234567890EFGH",  # Mock IRN
        qr_code_present=True,
        document_type="Tax Invoice",
        vendor_gstin="29AABCU9603R1ZX",  # Mock GSTIN
    )

