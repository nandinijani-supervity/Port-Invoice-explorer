# app/models/ap_docs.py
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from ..core.database import Base


class PurchaseOrder(Base):
    """Purchase Order model - represents the 'Truth Data' for POs"""

    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    po_number = Column(String(50), unique=True, nullable=False, index=True)
    vendor_name = Column(String(255), nullable=False, index=True)
    vendor_gstin = Column(String(15), nullable=True)  # GST Identification Number
    po_date = Column(Date, nullable=False)
    po_total_value = Column(Numeric(15, 2), nullable=False)  # Total PO amount
    currency = Column(String(3), default="INR", nullable=False)
    status = Column(String(50), default="Active", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    service_entry_sheets = relationship("ServiceEntrySheet", back_populates="purchase_order", cascade="all, delete-orphan")
    compliance_checklists = relationship("ComplianceChecklist", back_populates="purchase_order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<PurchaseOrder(po_number='{self.po_number}', vendor='{self.vendor_name}', total={self.po_total_value})>"


class ServiceEntrySheet(Base):
    """Service Entry Sheet model - represents the 'Truth Data' for SES"""

    __tablename__ = "service_entry_sheets"

    id = Column(Integer, primary_key=True, index=True)
    ses_number = Column(String(50), unique=True, nullable=False, index=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False, index=True)
    ses_date = Column(Date, nullable=False)
    ses_amount = Column(Numeric(15, 2), nullable=False)  # SES amount
    currency = Column(String(3), default="INR", nullable=False)
    status = Column(String(50), default="Active", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="service_entry_sheets")
    compliance_checklists = relationship("ComplianceChecklist", back_populates="service_entry_sheet", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ServiceEntrySheet(ses_number='{self.ses_number}', po_id={self.po_id}, amount={self.ses_amount})>"


class ComplianceChecklist(Base):
    """Compliance Checklist model - tracks deductions, hold status, and other compliance flags"""

    __tablename__ = "compliance_checklists"

    id = Column(Integer, primary_key=True, index=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False, index=True)
    ses_id = Column(Integer, ForeignKey("service_entry_sheets.id"), nullable=True, index=True)
    
    # Hold status - Rule 10: If "On Hold", validation fails
    hold_status = Column(String(50), default="Active", nullable=False)  # Values: "Active", "On Hold", "Released"
    
    # Deductions flag - Rule 9: If has_deductions=True, invoice must be Credit Note
    has_deductions = Column(Boolean, default=False, nullable=False)
    deduction_amount = Column(Numeric(15, 2), nullable=True)  # Amount of deductions if any
    deduction_reason = Column(Text, nullable=True)  # Reason for deductions
    
    # Additional compliance notes
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="compliance_checklists")
    service_entry_sheet = relationship("ServiceEntrySheet", back_populates="compliance_checklists")

    def __repr__(self):
        return f"<ComplianceChecklist(po_id={self.po_id}, ses_id={self.ses_id}, hold_status='{self.hold_status}', has_deductions={self.has_deductions})>"

