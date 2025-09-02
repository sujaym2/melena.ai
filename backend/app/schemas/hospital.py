from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class HospitalBase(BaseModel):
    """Base hospital schema"""
    name: str = Field(..., description="Hospital name")
    npi_number: Optional[str] = Field(None, description="National Provider Identifier")
    address: str = Field(..., description="Hospital address")
    city: str = Field(..., description="City")
    state: str = Field("IL", description="State (defaults to IL)")
    zip_code: str = Field(..., description="ZIP code")
    county: str = Field(..., description="County")
    phone: Optional[str] = Field(None, description="Phone number")
    website: Optional[str] = Field(None, description="Website URL")
    email: Optional[str] = Field(None, description="Email address")
    hospital_type: Optional[str] = Field(None, description="Type of hospital")
    ownership_type: Optional[str] = Field(None, description="Ownership type")
    bed_count: Optional[int] = Field(None, description="Number of beds")
    trauma_level: Optional[str] = Field(None, description="Trauma center level")
    illinois_region: Optional[str] = Field(None, description="Illinois region")
    medicaid_participant: bool = Field(True, description="Medicaid participant")
    medicare_participant: bool = Field(True, description="Medicare participant")

class HospitalCreate(HospitalBase):
    """Schema for creating a hospital"""
    pass

class HospitalUpdate(BaseModel):
    """Schema for updating a hospital"""
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    county: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    hospital_type: Optional[str] = None
    ownership_type: Optional[str] = None
    bed_count: Optional[int] = None
    trauma_level: Optional[str] = None
    illinois_region: Optional[str] = None
    medicaid_participant: Optional[bool] = None
    medicare_participant: Optional[bool] = None

class HospitalResponse(HospitalBase):
    """Schema for hospital response"""
    id: int
    transparency_file_url: Optional[str] = None
    last_data_update: Optional[datetime] = None
    data_quality_score: float = 0.0
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class HospitalProcedureBase(BaseModel):
    """Base hospital procedure schema"""
    cpt_code: str = Field(..., description="CPT code")
    hcpcs_code: Optional[str] = Field(None, description="HCPCS code")
    procedure_name: str = Field(..., description="Procedure name")
    procedure_description: Optional[str] = Field(None, description="Procedure description")
    cash_price: Optional[float] = Field(None, description="Cash price")
    negotiated_rate_min: Optional[float] = Field(None, description="Minimum negotiated rate")
    negotiated_rate_max: Optional[float] = Field(None, description="Maximum negotiated rate")
    negotiated_rate_median: Optional[float] = Field(None, description="Median negotiated rate")
    medicare_rate: Optional[float] = Field(None, description="Medicare rate")
    medicaid_rate: Optional[float] = Field(None, description="Medicaid rate")
    facility_fee: Optional[float] = Field(None, description="Facility fee")
    professional_fee: Optional[float] = Field(None, description="Professional fee")
    anesthesia_fee: Optional[float] = Field(None, description="Anesthesia fee")

class HospitalProcedureCreate(HospitalProcedureBase):
    """Schema for creating a hospital procedure"""
    hospital_id: int = Field(..., description="Hospital ID")

class HospitalProcedureUpdate(BaseModel):
    """Schema for updating a hospital procedure"""
    cpt_code: Optional[str] = None
    hcpcs_code: Optional[str] = None
    procedure_name: Optional[str] = None
    procedure_description: Optional[str] = None
    cash_price: Optional[float] = None
    negotiated_rate_min: Optional[float] = None
    negotiated_rate_max: Optional[float] = None
    negotiated_rate_median: Optional[float] = None
    medicare_rate: Optional[float] = None
    medicaid_rate: Optional[float] = None
    facility_fee: Optional[float] = None
    professional_fee: Optional[float] = None
    anesthesia_fee: Optional[float] = None

class HospitalProcedureResponse(HospitalProcedureBase):
    """Schema for hospital procedure response"""
    id: int
    hospital_id: int
    source_file: Optional[str] = None
    last_updated: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class HospitalInsuranceContractBase(BaseModel):
    """Base hospital insurance contract schema"""
    insurance_company: str = Field(..., description="Insurance company name")
    plan_name: Optional[str] = Field(None, description="Plan name")
    plan_type: Optional[str] = Field(None, description="Plan type")
    contract_start_date: Optional[datetime] = Field(None, description="Contract start date")
    contract_end_date: Optional[datetime] = Field(None, description="Contract end date")
    discount_percentage: Optional[float] = Field(None, description="Discount percentage")
    in_network: bool = Field(True, description="In network status")
    tier_level: Optional[str] = Field(None, description="Tier level")

class HospitalInsuranceContractCreate(HospitalInsuranceContractBase):
    """Schema for creating a hospital insurance contract"""
    hospital_id: int = Field(..., description="Hospital ID")

class HospitalInsuranceContractResponse(HospitalInsuranceContractBase):
    """Schema for hospital insurance contract response"""
    id: int
    hospital_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ProcedureComparison(BaseModel):
    """Schema for procedure comparison across hospitals"""
    cpt_code: str
    procedure_name: str
    hospitals: List[dict]  # List of hospital pricing info

class ProcedureSearchResponse(BaseModel):
    """Schema for procedure search response"""
    search_term: str
    total_procedures: int
    results: List[ProcedureComparison]

class IllinoisOverview(BaseModel):
    """Schema for Illinois healthcare overview"""
    total_hospitals: int
    total_procedures: int
    cities: List[str]
    hospital_types: List[str]
    regions: dict

class DataScrapingResponse(BaseModel):
    """Schema for data scraping response"""
    status: str
    message: str
    hospitals_processed: int
    total_procedures: int
