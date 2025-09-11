from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Hospital(Base):
    """Hospital information model"""
    __tablename__ = "hospitals"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    npi_number = Column(String(20), unique=True, index=True)  # National Provider Identifier
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False, index=True)
    state = Column(String(2), nullable=False, default="IL")
    zip_code = Column(String(10), nullable=False)
    county = Column(String(100), nullable=False)
    
    # Contact Information
    phone = Column(String(20))
    website = Column(String(255))
    email = Column(String(255))
    
    # Hospital Details
    hospital_type = Column(String(100))  # Acute Care, Critical Access, etc.
    ownership_type = Column(String(100))  # Non-profit, For-profit, Government
    bed_count = Column(Integer)
    trauma_level = Column(String(20))  # Level I, II, III, IV, V
    
    # Illinois Specific
    illinois_region = Column(String(100))  # Chicago Metro, Central, Southern, etc.
    medicaid_participant = Column(Boolean, default=True)
    medicare_participant = Column(Boolean, default=True)
    
    # Data Quality
    transparency_file_url = Column(String(500))
    last_data_update = Column(DateTime(timezone=True), server_default=func.now())
    data_quality_score = Column(Float, default=0.0)  # 0-100 score
    
    # Relationships
    procedures = relationship("HospitalProcedure", back_populates="hospital")
    insurance_contracts = relationship("HospitalInsuranceContract", back_populates="hospital")
    transparency_scores = relationship("HospitalTransparencyScore", back_populates="hospital")
    excellence_recognition = relationship("HospitalExcellenceRecognition", back_populates="hospital")
    peer_groups = relationship("HospitalPeerGroup", back_populates="hospital")
    accountability_tiers = relationship("HospitalAccountabilityTier", back_populates="hospital")
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Hospital(name='{self.name}', city='{self.city}')>"

class HospitalProcedure(Base):
    """Hospital procedure pricing model"""
    __tablename__ = "hospital_procedures"
    
    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False)
    
    # Procedure Information
    cpt_code = Column(String(10), nullable=False, index=True)  # Current Procedural Terminology
    hcpcs_code = Column(String(10), index=True)  # Healthcare Common Procedure Coding System
    procedure_name = Column(String(500), nullable=False)
    procedure_description = Column(Text)
    
    # Pricing Information
    cash_price = Column(Float)
    negotiated_rate_min = Column(Float)
    negotiated_rate_max = Column(Float)
    negotiated_rate_median = Column(Float)
    
    # Insurance Specific Pricing
    medicare_rate = Column(Float)
    medicaid_rate = Column(Float)
    
    # Additional Costs
    facility_fee = Column(Float)
    professional_fee = Column(Float)
    anesthesia_fee = Column(Float)
    
    # Data Source
    source_file = Column(String(255))
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    hospital = relationship("Hospital", back_populates="procedures")
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<HospitalProcedure(hospital='{self.hospital.name}', procedure='{self.procedure_name}')>"

class HospitalInsuranceContract(Base):
    """Hospital insurance contract information"""
    __tablename__ = "hospital_insurance_contracts"
    
    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False)
    
    # Insurance Information
    insurance_company = Column(String(255), nullable=False)
    plan_name = Column(String(255))
    plan_type = Column(String(100))  # PPO, HMO, EPO, etc.
    
    # Contract Details
    contract_start_date = Column(DateTime(timezone=True))
    contract_end_date = Column(DateTime(timezone=True))
    discount_percentage = Column(Float)
    
    # Network Status
    in_network = Column(Boolean, default=True)
    tier_level = Column(String(50))  # Tier 1, Tier 2, etc.
    
    # Relationships
    hospital = relationship("Hospital", back_populates="insurance_contracts")
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<HospitalInsuranceContract(hospital='{self.hospital.name}', insurance='{self.insurance_company}')>"
