# app/utils/report_generator.py
"""
Excel Report Generator for Invoice Validation Results

Generates downloadable Excel reports containing validation results.
"""

import tempfile
import uuid
from pathlib import Path
from typing import List

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from ..schemas.invoice import InvoiceExtraction, ValidationResult


def generate_excel_report(
    extraction_data: InvoiceExtraction,
    results: List[ValidationResult],
    overall_status: str,
    po_found: bool,
    ses_found: bool,
) -> str:
    """
    Generate an Excel report for invoice validation results.

    Args:
        extraction_data: The extracted invoice data
        results: List of validation rule results
        overall_status: Overall validation status ("pass" or "fail")
        po_found: Whether PO was found in database
        ses_found: Whether SES was found in database

    Returns:
        str: Path to the generated Excel file
    """
    # Create a temporary file
    temp_dir = Path(tempfile.gettempdir())
    report_id = str(uuid.uuid4())
    file_path = temp_dir / f"invoice_validation_report_{report_id}.xlsx"

    # Create workbook and worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Validation Report"

    # Define styles
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=12)
    pass_fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
    fail_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
    title_font = Font(bold=True, size=14)
    bold_font = Font(bold=True)

    # Title
    ws.merge_cells("A1:D1")
    ws["A1"] = "Invoice Validation Report"
    ws["A1"].font = title_font
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 30

    # Invoice Information Section
    row = 3
    ws[f"A{row}"] = "Invoice Information"
    ws[f"A{row}"].font = bold_font
    row += 1

    invoice_info = [
        ("Invoice Number", extraction_data.invoice_number),
        ("Invoice Date", extraction_data.invoice_date.strftime("%Y-%m-%d")),
        ("Vendor Name", extraction_data.vendor_name),
        ("PO Number", extraction_data.po_number),
        ("Total Amount", f"{extraction_data.total_amount:,.2f}"),
        ("Tax Amount", f"{extraction_data.tax_amount:,.2f}"),
        ("Document Type", extraction_data.document_type),
        ("IRN Number", extraction_data.irn_number or "N/A"),
        ("QR Code Present", "Yes" if extraction_data.qr_code_present else "No"),
        ("Vendor GSTIN", extraction_data.vendor_gstin or "N/A"),
    ]

    for label, value in invoice_info:
        ws[f"A{row}"] = label
        ws[f"B{row}"] = value
        ws[f"A{row}"].font = bold_font
        row += 1

    # Database Status Section
    row += 1
    ws[f"A{row}"] = "Database Status"
    ws[f"A{row}"].font = bold_font
    row += 1

    ws[f"A{row}"] = "PO Found"
    ws[f"B{row}"] = "Yes" if po_found else "No"
    ws[f"A{row}"].font = bold_font
    row += 1

    ws[f"A{row}"] = "SES Found"
    ws[f"B{row}"] = "Yes" if ses_found else "No"
    ws[f"A{row}"].font = bold_font
    row += 1

    # Overall Status
    row += 1
    ws[f"A{row}"] = "Overall Status"
    ws[f"A{row}"].font = bold_font
    ws[f"B{row}"] = overall_status.upper()
    ws[f"B{row}"].font = bold_font
    if overall_status.lower() == "pass":
        ws[f"B{row}"].fill = pass_fill
    else:
        ws[f"B{row}"].fill = fail_fill
    row += 2

    # Validation Results Section
    ws[f"A{row}"] = "Validation Results"
    ws[f"A{row}"].font = bold_font
    row += 1

    # Headers for validation results table
    headers = ["Rule ID", "Rule Name", "Status", "Remarks"]
    for col_idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=row, column=col_idx)
        cell.value = header
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    row += 1

    # Validation results rows
    for result in results:
        ws[f"A{row}"] = result.rule_id
        ws[f"B{row}"] = result.rule_name
        ws[f"C{row}"] = result.status.upper()
        ws[f"D{row}"] = result.remarks

        # Apply status-based formatting
        if result.status.lower() == "pass":
            ws[f"C{row}"].fill = pass_fill
        else:
            ws[f"C{row}"].fill = fail_fill

        # Wrap text in remarks column
        ws[f"D{row}"].alignment = Alignment(wrap_text=True, vertical="top")

        row += 1

    # Auto-adjust column widths
    ws.column_dimensions["A"].width = 12
    ws.column_dimensions["B"].width = 30
    ws.column_dimensions["C"].width = 12
    ws.column_dimensions["D"].width = 60

    # Save workbook
    wb.save(file_path)

    return str(file_path)

