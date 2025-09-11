from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class TransparencyCategory(str, Enum):
    """Transparency excellence categories"""
    SMALL_HOSPITAL_EXCELLENCE = "small_hospital_excellence"
    RURAL_INNOVATION = "rural_innovation"
    COMMUNITY_FOCUS = "community_focus"
    CRITICAL_ACCESS_EXCELLENCE = "critical_access_excellence"
    COMMUNITY_PARTNERSHIP = "community_partnership"

class HospitalSize(str, Enum):
    """Hospital size categories"""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"

class HospitalExcellenceBase(BaseModel):
    """Base hospital excellence schema"""
    category: TransparencyCategory
    title: str = Field(..., description="Excellence recognition title")
    description: Optional[str] = Field(None, description="Recognition description")
    transparency_score: float = Field(..., ge=0, le=100, description="Transparency score")
    community_impact_score: float = Field(..., ge=0, le=100, description="Community impact score")
    cost_effectiveness_score: float = Field(..., description="Cost effectiveness score")
    patient_satisfaction_score: float = Field(..., ge=0, le=100, description="Patient satisfaction score")
    is_featured: bool = Field(False, description="Is featured on homepage")
    is_spotlight: bool = Field(False, description="Is in spotlight section")
    is_active: bool = Field(True, description="Is currently active recognition")
    achievements: Optional[str] = Field(None, description="JSON string of achievements")
    community_impact_details: Optional[str] = Field(None, description="Community impact details")
    cost_optimization_details: Optional[str] = Field(None, description="Cost optimization details")

class HospitalExcellenceResponse(HospitalExcellenceBase):
    """Hospital excellence response schema"""
    id: int
    hospital_id: int
    recognition_start_date: datetime
    recognition_end_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class TransparencyScoreBase(BaseModel):
    """Base transparency score schema"""
    hospital_size: HospitalSize
    data_accessibility_score: float = Field(..., ge=0, le=100)
    data_completeness_score: float = Field(..., ge=0, le=100)
    data_accuracy_score: float = Field(..., ge=0, le=100)
    update_frequency_score: float = Field(..., ge=0, le=100)
    weighted_accessibility: float = Field(..., ge=0, le=100)
    weighted_completeness: float = Field(..., ge=0, le=100)
    weighted_accuracy: float = Field(..., ge=0, le=100)
    weighted_frequency: float = Field(..., ge=0, le=100)
    overall_transparency_score: float = Field(..., ge=0, le=100)
    peer_group_rank: Optional[int] = None
    peer_group_percentile: Optional[float] = None
    cost_per_bed_transparency: Optional[float] = None
    community_impact_score: Optional[float] = None
    patient_satisfaction_score: Optional[float] = None

class TransparencyScoreResponse(TransparencyScoreBase):
    """Transparency score response schema"""
    id: int
    hospital_id: int
    scoring_methodology: str
    last_calculated: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class PeerGroupHospital(BaseModel):
    """Peer group hospital schema"""
    hospital_id: int
    hospital_name: str
    rank_in_group: int
    percentile_in_group: float
    transparency_vs_peers: Optional[float] = None
    cost_effectiveness_vs_peers: Optional[float] = None
    community_impact_vs_peers: Optional[float] = None

class PeerGroupComparison(BaseModel):
    """Peer group comparison schema"""
    group_name: str
    group_size: int
    group_avg_transparency_score: float
    group_median_transparency_score: float
    group_std_transparency_score: float
    group_avg_bed_count: float
    group_avg_community_impact: float
    group_avg_cost_effectiveness: float
    hospitals: List[PeerGroupHospital]

class AccountabilityTierBase(BaseModel):
    """Base accountability tier schema"""
    tier: str = Field(..., description="Accountability tier (strict, supportive, educational)")
    enforcement_level: str = Field(..., description="Enforcement level (high, medium, low)")
    compliance_timeline_days: int = Field(..., description="Days to achieve compliance")
    support_level: str = Field(..., description="Support level (full, partial, minimal)")
    enforcement_actions: Optional[str] = Field(None, description="JSON string of enforcement actions")
    tier_reason: Optional[str] = Field(None, description="Reason for tier assignment")
    size_factor: bool = Field(False, description="Size was a factor in tier assignment")
    resource_factor: bool = Field(False, description="Resources were a factor")
    community_factor: bool = Field(False, description="Community impact was a factor")
    compliance_rate: Optional[float] = None
    improvement_rate: Optional[float] = None
    support_utilization: Optional[float] = None

class AccountabilityTierResponse(AccountabilityTierBase):
    """Accountability tier response schema"""
    id: int
    hospital_id: int
    tier_assignment_date: datetime
    tier_review_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class SmallHospitalExcellence(BaseModel):
    """Small hospital excellence schema"""
    hospital: Dict[str, any]
    transparency_score: float
    community_impact_score: float
    cost_effectiveness: float
    excellence_recognition: Optional[str] = None
    is_featured: bool = False
    is_spotlight: bool = False

class RuralHospitalHero(BaseModel):
    """Rural hospital hero schema"""
    hospital: Dict[str, any]
    transparency_score: float
    community_impact_score: float
    cost_effectiveness: float
    rural_hero_qualities: List[str]

class ExcellenceCategoryInfo(BaseModel):
    """Excellence category information schema"""
    name: str
    count: int
    description: str

class ScoringAnalysisResult(BaseModel):
    """Scoring analysis result schema"""
    status: str
    message: str
    results: Dict[str, any]

class HospitalExcellenceCreate(BaseModel):
    """Schema for creating hospital excellence recognition"""
    hospital_id: int
    category: TransparencyCategory
    title: str
    description: Optional[str] = None
    transparency_score: float = Field(..., ge=0, le=100)
    community_impact_score: float = Field(..., ge=0, le=100)
    cost_effectiveness_score: float
    patient_satisfaction_score: float = Field(..., ge=0, le=100)
    is_featured: bool = False
    is_spotlight: bool = False
    achievements: Optional[List[str]] = None
    community_impact_details: Optional[str] = None
    cost_optimization_details: Optional[str] = None

class HospitalExcellenceUpdate(BaseModel):
    """Schema for updating hospital excellence recognition"""
    category: Optional[TransparencyCategory] = None
    title: Optional[str] = None
    description: Optional[str] = None
    transparency_score: Optional[float] = Field(None, ge=0, le=100)
    community_impact_score: Optional[float] = Field(None, ge=0, le=100)
    cost_effectiveness_score: Optional[float] = None
    patient_satisfaction_score: Optional[float] = Field(None, ge=0, le=100)
    is_featured: Optional[bool] = None
    is_spotlight: Optional[bool] = None
    is_active: Optional[bool] = None
    achievements: Optional[List[str]] = None
    community_impact_details: Optional[str] = None
    cost_optimization_details: Optional[str] = None
    recognition_end_date: Optional[datetime] = None
