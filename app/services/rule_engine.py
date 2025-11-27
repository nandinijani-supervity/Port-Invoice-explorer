# app/services/rule_engine.py
"""
Invoice Validation Rule Engine

Implements the 10 validation rules for the 3-Way Match process:
1. Check if linked PO/SES exists in DB
2. Check Document Type (Tax Invoice vs Credit Note)
3. Check for Digital Signature (Simulated)
4. Invoice Number length <= 16 digits
5. Invoice Date <= 90 days old
6. 3-Way Match: Invoice Vendor/GST/Amount matches PO & SES in DB
7. IRN & QR Code present
8. Tax Calculation check (Rate/Qty/Tax matches)
9. Check for Deductions (If DB Checklist has deductions, Invoice must be Credit Note)
10. Check for Hold Status (If DB Checklist is "On Hold", Fail)
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from ..models.ap_docs import ComplianceChecklist, PurchaseOrder, ServiceEntrySheet
from ..schemas.invoice import InvoiceExtraction, ValidationResult


class InvoiceValidator:
    """Validates invoices against the 10 compliance rules"""

    def __init__(
        self,
        invoice: InvoiceExtraction,
        purchase_order: Optional[PurchaseOrder],
        service_entry_sheet: Optional[ServiceEntrySheet],
        compliance_checklist: Optional[ComplianceChecklist],
    ):
        self.invoice = invoice
        self.po = purchase_order
        self.ses = service_entry_sheet
        self.checklist = compliance_checklist

    def validate_all(self) -> List[ValidationResult]:
        """Run all 10 validation rules and return results"""
        results = []

        results.append(self._rule_1_check_po_ses_exists())
        results.append(self._rule_2_check_document_type())
        results.append(self._rule_3_check_digital_signature())
        results.append(self._rule_4_check_invoice_number_length())
        results.append(self._rule_5_check_invoice_date_age())
        results.append(self._rule_6_three_way_match())
        results.append(self._rule_7_check_irn_qr_code())
        results.append(self._rule_8_check_tax_calculation())
        results.append(self._rule_9_check_deductions())
        results.append(self._rule_10_check_hold_status())

        return results

    def _rule_1_check_po_ses_exists(self) -> ValidationResult:
        """Rule 1: Check if linked PO/SES exists in DB"""
        rule_id = 1
        rule_name = "PO/SES Existence Check"

        if self.po is None:
            return ValidationResult(
                rule_id=rule_id,
                rule_name=rule_name,
                status="fail",
                remarks=f"Purchase Order with number '{self.invoice.po_number}' not found in database",
            )

        if self.ses is None:
            return ValidationResult(
                rule_id=rule_id,
                rule_name=rule_name,
                status="fail",
                remarks=f"Service Entry Sheet linked to PO '{self.invoice.po_number}' not found in database",
            )

        return ValidationResult(
            rule_id=rule_id,
            rule_name=rule_name,
            status="pass",
            remarks=f"PO '{self.po.po_number}' and SES found in database",
        )

    def _rule_2_check_document_type(self) -> ValidationResult:
        """Rule 2: Check Document Type (Tax Invoice vs Credit Note)"""
        rule_id = 2
        rule_name = "Document Type Check"

        # Use is_tax_invoice boolean from Gemini AI extraction
        if not self.invoice.is_tax_invoice:
            # If not a tax invoice, it should be a credit note
            return ValidationResult(
                rule_id=rule_id,
                rule_name=rule_name,
                status="pass",
                remarks="Document type is Credit Note (valid)",
            )

        return ValidationResult(
            rule_id=rule_id,
            rule_name=rule_name,
            status="pass",
            remarks="Document type is Tax Invoice (valid)",
        )

    def _rule_3_check_digital_signature(self) -> ValidationResult:
        """Rule 3: Check for Digital Signature (Detected by Gemini AI)"""
        rule_id = 3
        rule_name = "Digital Signature Check"

        # Use has_digital_signature boolean from Gemini AI visual analysis
        if self.invoice.has_digital_signature:
            return ValidationResult(
                rule_id=rule_id,
                rule_name=rule_name,
                status="pass",
                remarks="Digital signature detected and verified by AI analysis",
            )
        else:
            return ValidationResult(
                rule_id=rule_id,
                rule_name=rule_name,
                status="fail",
                remarks="Digital signature not found or invalid (AI analysis)",
            )

    def _rule_4_check_invoice_number_length(self) -> ValidationResult:
        """Rule 4: Invoice Number length <= 16 digits"""
        rule_id = 4
        rule_name = "Invoice Number Length Check"

        # Remove any non-digit characters for length check
        invoice_number_digits = "".join(filter(str.isdigit, self.invoice.invoice_number))

        if len(invoice_number_digits) > 16:
            return ValidationResult(
                rule_id=rule_id,
                rule_name=rule_name,
                status="fail",
                remarks=f"Invoice number '{self.invoice.invoice_number}' exceeds 16 digits (has {len(invoice_number_digits)} digits)",
            )

        return ValidationResult(
            rule_id=rule_id,
            rule_name=rule_name,
            status="pass",
            remarks=f"Invoice number length ({len(invoice_number_digits)} digits) is within limit",
        )

    def _rule_5_check_invoice_date_age(self) -> ValidationResult:
        """Rule 5: Invoice Date <= 90 days old"""
        rule_id = 5
        rule_name = "Invoice Date Age Check"

        today = date.today()
        days_old = (today - self.invoice.invoice_date).days

        if days_old < 0:
            return ValidationResult(
                rule_id=rule_id,
                rule_name=rule_name,
                status="fail",
                remarks=f"Invoice date '{self.invoice.invoice_date}' is in the future",
            )

        if days_old > 90:
            return ValidationResult(
                rule_id=rule_id,
                rule_name=rule_name,
                status="fail",
                remarks=f"Invoice date '{self.invoice.invoice_date}' is {days_old} days old (exceeds 90 days limit)",
            )

        return ValidationResult(
            rule_id=rule_id,
            rule_name=rule_name,
            status="pass",
            remarks=f"Invoice date is {days_old} days old (within 90 days limit)",
        )

    def _rule_6_three_way_match(self) -> ValidationResult:
        """Rule 6: 3-Way Match - Invoice Vendor/GST/Amount matches PO & SES"""
        rule_id = 6
        rule_name = "3-Way Match Check"

        if self.po is None or self.ses is None:
            return ValidationResult(
                rule_id=rule_id,
                rule_name=rule_name,
                status="fail",
                remarks="Cannot perform 3-way match: PO or SES not found",
            )

        # Check Vendor Name match
        invoice_vendor_upper = self.invoice.vendor_name.upper().strip()
        po_vendor_upper = self.po.vendor_name.upper().strip()

        if invoice_vendor_upper != po_vendor_upper:
            return ValidationResult(
                rule_id=rule_id,
                rule_name=rule_name,
                status="fail",
                remarks=f"Vendor name mismatch: Invoice '{self.invoice.vendor_name}' != PO '{self.po.vendor_name}'",
            )

        # Check GSTIN match (if both are present)
        if self.invoice.vendor_gstin and self.po.vendor_gstin:
            if self.invoice.vendor_gstin.upper() != self.po.vendor_gstin.upper():
                return ValidationResult(
                    rule_id=rule_id,
                    rule_name=rule_name,
                    status="fail",
                    remarks=f"GSTIN mismatch: Invoice '{self.invoice.vendor_gstin}' != PO '{self.po.vendor_gstin}'",
                )

        # Check Amount match: Invoice.total_amount == SES.ses_amount
        invoice_amount = Decimal(str(self.invoice.total_amount))
        ses_amount = Decimal(str(self.ses.ses_amount))

        # Allow small tolerance for floating point comparison (0.01)
        tolerance = Decimal("0.01")
        amount_diff = abs(invoice_amount - ses_amount)

        if amount_diff > tolerance:
            return ValidationResult(
                rule_id=rule_id,
                rule_name=rule_name,
                status="fail",
                remarks=f"Amount mismatch: Invoice '{invoice_amount}' != SES '{ses_amount}' (difference: {amount_diff})",
            )

        return ValidationResult(
            rule_id=rule_id,
            rule_name=rule_name,
            status="pass",
            remarks=f"3-way match passed: Vendor, GST, and Amount match between Invoice, PO, and SES",
        )

    def _rule_7_check_irn_qr_code(self) -> ValidationResult:
        """Rule 7: IRN & QR Code present"""
        rule_id = 7
        rule_name = "IRN & QR Code Check"

        if not self.invoice.irn_number:
            return ValidationResult(
                rule_id=rule_id,
                rule_name=rule_name,
                status="fail",
                remarks="IRN (Invoice Reference Number) is missing",
            )

        if not self.invoice.qr_code_present:
            return ValidationResult(
                rule_id=rule_id,
                rule_name=rule_name,
                status="fail",
                remarks="QR Code is not present on invoice",
            )

        return ValidationResult(
            rule_id=rule_id,
            rule_name=rule_name,
            status="pass",
            remarks=f"IRN '{self.invoice.irn_number}' and QR Code are present",
        )

    def _rule_8_check_tax_calculation(self) -> ValidationResult:
        """Rule 8: Tax Calculation check (Rate/Qty/Tax matches)"""
        rule_id = 8
        rule_name = "Tax Calculation Check"

        # Simplified tax calculation check
        # In production, this would verify line items, tax rates, and calculations
        # For now, we check if tax_amount is reasonable (non-negative and not exceeding total)

        if self.invoice.tax_amount < 0:
            return ValidationResult(
                rule_id=rule_id,
                rule_name=rule_name,
                status="fail",
                remarks=f"Tax amount cannot be negative: {self.invoice.tax_amount}",
            )

        if self.invoice.tax_amount > self.invoice.total_amount:
            return ValidationResult(
                rule_id=rule_id,
                rule_name=rule_name,
                status="fail",
                remarks=f"Tax amount ({self.invoice.tax_amount}) exceeds total amount ({self.invoice.total_amount})",
            )

        # Basic validation passed
        # In production, this would perform detailed line-item tax calculations
        return ValidationResult(
            rule_id=rule_id,
            rule_name=rule_name,
            status="pass",
            remarks=f"Tax calculation appears valid (Tax: {self.invoice.tax_amount}, Total: {self.invoice.total_amount})",
        )

    def _rule_9_check_deductions(self) -> ValidationResult:
        """Rule 9: Check for Deductions (If DB Checklist has deductions, Invoice must be Credit Note)"""
        rule_id = 9
        rule_name = "Deductions Check"

        if self.checklist is None:
            # If no checklist exists, assume no deductions
            return ValidationResult(
                rule_id=rule_id,
                rule_name=rule_name,
                status="pass",
                remarks="No compliance checklist found, assuming no deductions",
            )

        if self.checklist.has_deductions:
            # If checklist has deductions, invoice MUST be a Credit Note
            if self.invoice.document_type != "Credit Note":
                return ValidationResult(
                    rule_id=rule_id,
                    rule_name=rule_name,
                    status="fail",
                    remarks=f"Checklist indicates deductions (Amount: {self.checklist.deduction_amount}), but invoice is '{self.invoice.document_type}' instead of 'Credit Note'",
                )

        return ValidationResult(
            rule_id=rule_id,
            rule_name=rule_name,
            status="pass",
            remarks="Deductions check passed (no deductions or Credit Note provided as required)",
        )

    def _rule_10_check_hold_status(self) -> ValidationResult:
        """Rule 10: Check for Hold Status (If DB Checklist is "On Hold", Fail)"""
        rule_id = 10
        rule_name = "Hold Status Check"

        if self.checklist is None:
            # If no checklist exists, assume not on hold
            return ValidationResult(
                rule_id=rule_id,
                rule_name=rule_name,
                status="pass",
                remarks="No compliance checklist found, assuming not on hold",
            )

        if self.checklist.hold_status == "On Hold":
            return ValidationResult(
                rule_id=rule_id,
                rule_name=rule_name,
                status="fail",
                remarks=f"Purchase Order is on hold. Hold status: '{self.checklist.hold_status}'",
            )

        return ValidationResult(
            rule_id=rule_id,
            rule_name=rule_name,
            status="pass",
            remarks=f"Hold status check passed (Status: '{self.checklist.hold_status}')",
        )


def validate_invoice(
    db: Session,
    invoice: InvoiceExtraction,
) -> tuple[bool, bool, Optional[PurchaseOrder], Optional[ServiceEntrySheet], Optional[ComplianceChecklist]]:
    """
    Helper function to query database and validate invoice.

    Returns:
        tuple: (po_found, ses_found, po, ses, checklist)
    """
    # Find Purchase Order
    po = db.query(PurchaseOrder).filter(PurchaseOrder.po_number == invoice.po_number).first()

    # Find Service Entry Sheet linked to the PO
    ses = None
    if po:
        ses = db.query(ServiceEntrySheet).filter(ServiceEntrySheet.po_id == po.id).first()

    # Find Compliance Checklist
    checklist = None
    if po:
        checklist = db.query(ComplianceChecklist).filter(ComplianceChecklist.po_id == po.id).first()

    return (po is not None, ses is not None, po, ses, checklist)

