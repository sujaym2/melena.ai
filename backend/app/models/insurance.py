from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base

class ClaimStatus(enum.Enum):
    """Claim status enumeration"""
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    APPROVED = "approved"
    DENIED = "denied"
    PARTIALLY_APPROVED = "partially_approved"
    APPEALED = "appealed"
    APPEAL_APPROVED = "appeal_approved"
    APPEAL_DENIED = "appeal_denied"

class AppealStatus(enum.Enum):
    """Appeal status enumeration"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"

class InsuranceClaim(Base):
    """Insurance claim model"""
    __tablename__ = "insurance_claims"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Claim Information
    claim_number = Column(String(100), unique=True, nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    insurance_company_id = Column(Integer, ForeignKey("insurance_companies.id"), nullable=False)
    
    # Service Details
    service_date = Column(DateTime(timezone=True), nullable=False)
    procedure_code = Column(String(10), nullable=False)  # CPT/HCPCS
    procedure_description = Column(String(500))
    diagnosis_codes = Column(Text)  # ICD-10 codes
    
    # Financial Information
    billed_amount = Column(Float, nullable=False)
    allowed_amount = Column(Float)
    paid_amount = Column(Float)
    patient_responsibility = Column(Float)
    deductible_applied = Column(Float)
    coinsurance_applied = Column(Float)
    copay_applied = Column(Float)
    
    # Claim Status
    status = Column(Enum(ClaimStatus), default=ClaimStatus.SUBMITTED)
    denial_reason = Column(Text)
    denial_code = Column(String(50))
    
    # Timestamps
    submitted_date = Column(DateTime(timezone=True), server_default=func.now())
    processed_date = Column(DateTime(timezone=True))
    
    # Relationships
    patient = relationship("Patient", back_populates="claims")
    provider = relationship("Provider", back_populates="claims")
    insurance_company = relationship("InsuranceCompany", back_populates="claims")
    appeals = relationship("ClaimAppeal", back_populates="claim")
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<InsuranceClaim(claim_number='{self.claim_number}', status='{self.status.value}')>"

class ClaimAppeal(Base):
    """Claim appeal model"""
    __tablename__ = "insurance_claim_appeals"
    
    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("insurance_claims.id"), nullable=False)
    
    # Appeal Information
    appeal_number = Column(String(100), unique=True, nullable=False)
    appeal_type = Column(String(100))  # Internal, External, Independent Review
    appeal_level = Column(String(50))  # First, Second, Third level
    
    # Appeal Details
    reason_for_appeal = Column(Text, nullable=False)
    supporting_documentation = Column(Text)
    appeal_letter_content = Column(Text)
    
    # Status and Timeline
    status = Column(Enum(AppealStatus), default=AppealStatus.NOT_STARTED)
    submitted_date = Column(DateTime(timezone=True))
    deadline_date = Column(DateTime(timezone=True))
    decision_date = Column(DateTime(timezone=True))
    
    # Decision
    decision = Column(String(100))  # Approved, Denied, Partially Approved
    decision_reason = Column(Text)
    decision_amount = Column(Float)
    
    # AI Analysis
    ai_confidence_score = Column(Float)  # 0-100 confidence in appeal success
    ai_recommendations = Column(Text)
    
    # Relationships
    claim = relationship("InsuranceClaim", back_populates="appeals")
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<ClaimAppeal(appeal_number='{self.appeal_number}', status='{self.status.value}')>"

class InsuranceCompany(Base):
    """Insurance company model"""
    __tablename__ = "insurance_companies"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Company Information
    name = Column(String(255), nullable=False, index=True)
    naic_code = Column(String(10), unique=True, index=True)  # National Association of Insurance Commissioners
    ein = Column(String(20))  # Employer Identification Number
    
    # Contact Information
    address = Column(Text)
    phone = Column(String(20))
    website = Column(String(255))
    customer_service_email = Column(String(255))
    
    # Illinois Specific
    illinois_license_number = Column(String(50))
    illinois_rating = Column(String(10))  # A, B, C, D, F
    
    # Network Information
    network_coverage_illinois = Column(Boolean, default=True)
    network_coverage_chicago = Column(Boolean, default=True)
    
    # Relationships
    claims = relationship("InsuranceClaim", back_populates="insurance_company")
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<InsuranceCompany(name='{self.name}', naic_code='{self.naic_code}')>"

class Provider(Base):
    """Healthcare provider model"""
    __tablename__ = "providers"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Provider Information
    npi_number = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    provider_type = Column(String(100))  # Physician, Hospital, Clinic, etc.
    specialty = Column(String(100))
    
    # Contact Information
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(2))
    zip_code = Column(String(10))
    phone = Column(String(20))
    
    # Illinois Specific
    illinois_license_number = Column(String(50))
    illinois_medicaid_provider = Column(Boolean, default=False)
    illinois_medicare_provider = Column(Boolean, default=False)
    
    # Relationships
    claims = relationship("InsuranceClaim", back_populates="provider")
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Provider(name='{self.name}', npi='{self.npi_number}')>"

class Patient(Base):
    """Patient model (anonymized for privacy)"""
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Anonymized Information
    patient_hash = Column(String(64), unique=True, nullable=False, index=True)
    age_group = Column(String(20))  # 18-25, 26-35, etc.
    gender = Column(String(10))
    zip_code = Column(String(10))
    
    # Insurance Information
    primary_insurance_id = Column(Integer, ForeignKey("insurance_companies.id"))
    secondary_insurance_id = Column(Integer, ForeignKey("insurance_companies.id"))
    
    # Relationships
    claims = relationship("InsuranceClaim", back_populates="patient")
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Patient(hash='{self.patient_hash[:8]}...', age_group='{self.age_group}')>"
