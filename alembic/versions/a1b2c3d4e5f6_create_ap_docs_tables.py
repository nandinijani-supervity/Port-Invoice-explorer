"""Create AP docs tables (PurchaseOrder, ServiceEntrySheet, ComplianceChecklist)

Revision ID: create_ap_docs
Revises: 78594ac01b8d
Create Date: 2025-01-XX XX:XX:XX.XXXXXX

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "78594ac01b8d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create purchase_orders table
    op.create_table(
        "purchase_orders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("po_number", sa.String(length=50), nullable=False),
        sa.Column("vendor_name", sa.String(length=255), nullable=False),
        sa.Column("vendor_gstin", sa.String(length=15), nullable=True),
        sa.Column("po_date", sa.Date(), nullable=False),
        sa.Column("po_total_value", sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_purchase_orders_id"), "purchase_orders", ["id"], unique=False)
    op.create_index(op.f("ix_purchase_orders_po_number"), "purchase_orders", ["po_number"], unique=True)
    op.create_index(op.f("ix_purchase_orders_vendor_name"), "purchase_orders", ["vendor_name"], unique=False)

    # Create service_entry_sheets table
    op.create_table(
        "service_entry_sheets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ses_number", sa.String(length=50), nullable=False),
        sa.Column("po_id", sa.Integer(), nullable=False),
        sa.Column("ses_date", sa.Date(), nullable=False),
        sa.Column("ses_amount", sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["po_id"], ["purchase_orders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_service_entry_sheets_id"), "service_entry_sheets", ["id"], unique=False)
    op.create_index(op.f("ix_service_entry_sheets_po_id"), "service_entry_sheets", ["po_id"], unique=False)
    op.create_index(op.f("ix_service_entry_sheets_ses_number"), "service_entry_sheets", ["ses_number"], unique=True)

    # Create compliance_checklists table
    op.create_table(
        "compliance_checklists",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("po_id", sa.Integer(), nullable=False),
        sa.Column("ses_id", sa.Integer(), nullable=True),
        sa.Column("hold_status", sa.String(length=50), nullable=False),
        sa.Column("has_deductions", sa.Boolean(), nullable=False),
        sa.Column("deduction_amount", sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column("deduction_reason", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["po_id"], ["purchase_orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["ses_id"], ["service_entry_sheets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_compliance_checklists_id"), "compliance_checklists", ["id"], unique=False)
    op.create_index(op.f("ix_compliance_checklists_po_id"), "compliance_checklists", ["po_id"], unique=False)
    op.create_index(op.f("ix_compliance_checklists_ses_id"), "compliance_checklists", ["ses_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_compliance_checklists_ses_id"), table_name="compliance_checklists")
    op.drop_index(op.f("ix_compliance_checklists_po_id"), table_name="compliance_checklists")
    op.drop_index(op.f("ix_compliance_checklists_id"), table_name="compliance_checklists")
    op.drop_table("compliance_checklists")
    
    op.drop_index(op.f("ix_service_entry_sheets_ses_number"), table_name="service_entry_sheets")
    op.drop_index(op.f("ix_service_entry_sheets_po_id"), table_name="service_entry_sheets")
    op.drop_index(op.f("ix_service_entry_sheets_id"), table_name="service_entry_sheets")
    op.drop_table("service_entry_sheets")
    
    op.drop_index(op.f("ix_purchase_orders_vendor_name"), table_name="purchase_orders")
    op.drop_index(op.f("ix_purchase_orders_po_number"), table_name="purchase_orders")
    op.drop_index(op.f("ix_purchase_orders_id"), table_name="purchase_orders")
    op.drop_table("purchase_orders")

