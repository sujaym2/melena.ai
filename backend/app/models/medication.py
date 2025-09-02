from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base

class MedicationType(enum.Enum):
    """Medication type enumeration"""
    GENERIC = "generic"
    BRAND_NAME = "brand_name"
    OVER_THE_COUNTER = "otc"
    PRESCRIPTION_ONLY = "prescription"

class PharmacyType(enum.Enum):
    """Pharmacy type enumeration"""
    CHAIN = "chain"
    INDEPENDENT = "independent"
    MAIL_ORDER = "mail_order"
    HOSPITAL = "hospital"
    GROCERY_STORE = "grocery_store"

class Medication(Base):
    """Medication information model"""
    __tablename__ = "medications"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Medication Information
    generic_name = Column(String(255), nullable=False, index=True)
    brand_name = Column(String(255), index=True)
    medication_type = Column(Enum(MedicationType), default=MedicationType.PRESCRIPTION_ONLY)
    
    # Drug Classification
    ndc_code = Column(String(20), unique=True, index=True)  # National Drug Code
    rxnorm_code = Column(String(20), index=True)  # RxNorm identifier
    fda_approval_date = Column(DateTime(timezone=True))
    
    # Dosage Forms
    dosage_form = Column(String(100))  # Tablet, Capsule, Liquid, etc.
    strength = Column(String(100))  # 10mg, 500mg, etc.
    quantity = Column(String(100))  # 30 tablets, 100ml, etc.
    
    # Therapeutic Information
    therapeutic_class = Column(String(255))
    indication = Column(Text)
    contraindications = Column(Text)
    
    # Illinois Specific
    illinois_medicaid_coverage = Column(Boolean, default=False)
    illinois_medicare_coverage = Column(Boolean, default=False)
    
    # Relationships
    prices = relationship("MedicationPrice", back_populates="medication")
    alternatives = relationship("MedicationAlternative", back_populates="medication")
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Medication(generic='{self.generic_name}', brand='{self.brand_name}')>"

class Pharmacy(Base):
    """Pharmacy information model"""
    __tablename__ = "pharmacies"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Pharmacy Information
    name = Column(String(255), nullable=False, index=True)
    pharmacy_type = Column(Enum(PharmacyType), default=PharmacyType.CHAIN)
    chain_name = Column(String(255))  # CVS, Walgreens, etc.
    
    # Location Information
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False, index=True)
    state = Column(String(2), nullable=False, default="IL")
    zip_code = Column(String(10), nullable=False)
    county = Column(String(100))
    
    # Contact Information
    phone = Column(String(20))
    website = Column(String(255))
    hours_of_operation = Column(Text)
    
    # Illinois Specific
    illinois_license_number = Column(String(50))
    illinois_medicaid_provider = Column(Boolean, default=False)
    illinois_medicare_provider = Column(Boolean, default=False)
    
    # Services
    offers_generics = Column(Boolean, default=True)
    offers_compounding = Column(Boolean, default=False)
    offers_immunizations = Column(Boolean, default=False)
    
    # Relationships
    prices = relationship("MedicationPrice", back_populates="pharmacy")
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Pharmacy(name='{self.name}', city='{self.city}')>"

class MedicationPrice(Base):
    """Medication pricing model"""
    __tablename__ = "medication_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Relationships
    medication_id = Column(Integer, ForeignKey("medications.id"), nullable=False)
    pharmacy_id = Column(Integer, ForeignKey("pharmacies.id"), nullable=False)
    
    # Pricing Information
    cash_price = Column(Float, nullable=False)
    insurance_price = Column(Float)
    discount_program_price = Column(Float)
    
    # Insurance Details
    insurance_company = Column(String(255))
    plan_name = Column(String(255))
    copay = Column(Float)
    deductible_applied = Column(Float)
    
    # Discount Programs
    goodrx_price = Column(Float)
    singlecare_price = Column(Float)
    rxsaver_price = Column(Float)
    
    # Availability
    in_stock = Column(Boolean, default=True)
    quantity_available = Column(String(100))
    
    # Data Source
    source = Column(String(100))  # API, Web Scraping, Manual Entry
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    medication = relationship("Medication", back_populates="prices")
    pharmacy = relationship("Pharmacy", back_populates="prices")
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<MedicationPrice(medication='{self.medication.generic_name}', pharmacy='{self.pharmacy.name}', price='${self.cash_price}')>"

class MedicationAlternative(Base):
    """Medication alternative model for cost optimization"""
    __tablename__ = "medication_alternatives"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Relationships
    medication_id = Column(Integer, ForeignKey("medications.id"), nullable=False)
    alternative_medication_id = Column(Integer, ForeignKey("medications.id"), nullable=False)
    
    # Alternative Information
    alternative_type = Column(String(100))  # Generic, Therapeutic, Dosage
    similarity_score = Column(Float)  # 0-100 similarity score
    cost_savings_percentage = Column(Float)
    
    # Clinical Information
    clinical_equivalence = Column(Boolean)
    requires_prescriber_approval = Column(Boolean)
    notes = Column(Text)
    
    # AI Analysis
    ai_recommendation_score = Column(Float)  # 0-100 recommendation score
    ai_reasoning = Column(Text)
    
    # Relationships
    medication = relationship("Medication", back_populates="alternatives")
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<MedicationAlternative(medication='{self.medication.generic_name}', alternative='{self.alternative_medication.generic_name}')>"

class PrescriptionDiscountProgram(Base):
    """Prescription discount program model"""
    __tablename__ = "prescription_discount_programs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Program Information
    program_name = Column(String(255), nullable=False, index=True)
    program_type = Column(String(100))  # Manufacturer, Pharmacy, Independent
    website = Column(String(255))
    
    # Program Details
    annual_fee = Column(Float, default=0.0)
    discount_percentage = Column(Float)
    max_discount_amount = Column(Float)
    eligibility_requirements = Column(Text)
    
    # Illinois Specific
    available_in_illinois = Column(Boolean, default=True)
    illinois_restrictions = Column(Text)
    
    # Coverage
    covered_medications = Column(Text)
    excluded_medications = Column(Text)
    
    # Relationships
    prices = relationship("MedicationPrice", back_populates="discount_program")
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<PrescriptionDiscountProgram(name='{self.program_name}', discount='{self.discount_percentage}%')>"
