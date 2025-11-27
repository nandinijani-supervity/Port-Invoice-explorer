# scripts/seed_ap_data.py
"""
Seed script for Accounts Payable data (Purchase Orders, Service Entry Sheets, Compliance Checklists)

This script populates the database with reference data extracted from:
- samples/4802048544.pdf (PO)
- samples/1020578016.pdf (SES)
- samples/checklist.pdf (Compliance Checklist)

Reference Data:
- PO Number: 4802048544
- SES Number: 1020578016
- Vendor: UPDATER SERVICES LTD
- Invoice Amount: 148,061.00
- PO Total Value: 4,333,777.35
"""
import os
import sys
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker

# Load .env file before importing database
project_root = Path(__file__).parent.parent
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(dotenv_path=env_file)
else:
    load_dotenv()

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine
from app.models.ap_docs import ComplianceChecklist, PurchaseOrder, ServiceEntrySheet

# Create a new session for this script
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()


def seed_ap_data():
    """Populates the database with Accounts Payable reference data."""
    try:
        print("Seeding Accounts Payable data...")

        # Check if data already exists
        existing_po = db.query(PurchaseOrder).filter(
            PurchaseOrder.po_number == "4802048544"
        ).first()

        if existing_po:
            print("AP data already exists, skipping seeding.")
            return

        # Create Purchase Order
        print("Creating Purchase Order...")
        po = PurchaseOrder(
            po_number="4802048544",
            vendor_name="UPDATER SERVICES LTD",
            vendor_gstin="29AABCU9603R1ZX",  # Example GSTIN format
            po_date=date(2024, 1, 15),  # Example date
            po_total_value=Decimal("4333777.35"),
            currency="INR",
            status="Active",
        )
        db.add(po)
        db.flush()  # Flush to get the PO ID

        # Create Service Entry Sheet
        print("Creating Service Entry Sheet...")
        ses = ServiceEntrySheet(
            ses_number="1020578016",
            po_id=po.id,
            ses_date=date(2024, 2, 1),  # Example date (after PO date)
            ses_amount=Decimal("148061.00"),  # Invoice amount from reference
            currency="INR",
            status="Active",
        )
        db.add(ses)
        db.flush()  # Flush to get the SES ID

        # Create Compliance Checklist
        print("Creating Compliance Checklist...")
        checklist = ComplianceChecklist(
            po_id=po.id,
            ses_id=ses.id,
            hold_status="Active",  # Not on hold - will pass Rule 10
            has_deductions=False,  # No deductions - will pass Rule 9
            deduction_amount=None,
            deduction_reason=None,
            notes="Reference data for Invoice Command Center validation testing",
        )
        db.add(checklist)

        # Commit all changes
        db.commit()
        print("✅ AP data seeding complete.")
        print(f"   - Created PO: {po.po_number} ({po.vendor_name})")
        print(f"   - Created SES: {ses.ses_number} (Amount: {ses.ses_amount})")
        print(f"   - Created Checklist: PO {po.po_number} / SES {ses.ses_number}")

    except Exception as e:
        print(f"❌ An error occurred during AP data seeding: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("--- Starting AP Data Seeding ---")
    seed_ap_data()

