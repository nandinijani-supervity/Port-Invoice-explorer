# app/schemas/invoice.py
from datetime import date
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel


class LineItem(BaseModel):
    """Line item from invoice"""

    description: str
    quantity: Optional[Decimal] = None
    unit_price: Optional[Decimal] = None
    amount: Decimal
    tax_rate: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None

    class Config:
        json_encoders = {
            Decimal: str,
        }


class InvoiceExtraction(BaseModel):
    """Extracted data from invoice PDF via Gemini AI"""

    invoice_number: str
    invoice_date: date
    vendor_name: str
    po_number: str
    total_amount: Decimal
    tax_amount: Decimal
    irn_number: Optional[str] = None  # Invoice Reference Number
    qr_code_present: bool = False
    vendor_gstin: Optional[str] = None
    
    # Gemini-specific fields
    has_digital_signature: bool = False  # Detected by Gemini visual analysis
    is_tax_invoice: bool = True  # True if document title says "Tax Invoice"
    line_items: Optional[List[LineItem]] = None  # Detailed line items from invoice
    
    # Legacy field for backward compatibility (computed property)
    @property
    def document_type(self) -> str:
        """Derived document type from is_tax_invoice"""
        return "Tax Invoice" if self.is_tax_invoice else "Credit Note"

    class Config:
        json_encoders = {
            Decimal: str,
            date: lambda v: v.isoformat() if v else None,
        }


class ValidationResult(BaseModel):
    """Result of a single validation rule"""

    rule_id: int
    rule_name: str
    status: str  # "pass" or "fail"
    remarks: str

    class Config:
        json_encoders = {
            Decimal: str,
        }


class ValidationResponse(BaseModel):
    """Complete validation response with all results"""

    extraction_data: InvoiceExtraction
    linked_po_found: bool
    linked_ses_found: bool
    results: List[ValidationResult]
    overall_status: str  # "pass" or "fail" - fails if any rule fails
    report_id: Optional[str] = None  # ID for downloading the Excel report

    class Config:
        json_encoders = {
            Decimal: str,
            date: lambda v: v.isoformat() if v else None,
        }

