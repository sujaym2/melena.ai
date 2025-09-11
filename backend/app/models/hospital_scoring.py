from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base

class HospitalSize(enum.Enum):
    """Hospital size categories"""
    SMALL = "small"  # <50 beds
    MEDIUM = "medium"  # 50-200 beds
    LARGE = "large"  # 200+ beds

class TransparencyCategory(enum.Enum):
    """Transparency excellence categories"""
    SMALL_HOSPITAL_EXCELLENCE = "small_hospital_excellence"
    RURAL_INNOVATION = "rural_innovation"
    COMMUNITY_FOCUS = "community_focus"
    CRITICAL_ACCESS_EXCELLENCE = "critical_access_excellence"
    COMMUNITY_PARTNERSHIP = "community_partnership"

class HospitalTransparencyScore(Base):
    """Hospital transparency scoring model"""
    __tablename__ = "hospital_transparency_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False)
    
    # Size-adjusted scoring weights
    hospital_size = Column(Enum(HospitalSize), nullable=False)
    
    # Transparency metrics (0-100 scale)
    data_accessibility_score = Column(Float, nullable=False)  # How easy to find data
    data_completeness_score = Column(Float, nullable=False)   # How complete the data is
    data_accuracy_score = Column(Float, nullable=False)       # How accurate the data is
    update_frequency_score = Column(Float, nullable=False)    # How often data is updated
    
    # Size-adjusted weighted scores
    weighted_accessibility = Column(Float, nullable=False)
    weighted_completeness = Column(Float, nullable=False)
    weighted_accuracy = Column(Float, nullable=False)
    weighted_frequency = Column(Float, nullable=False)
    
    # Overall scores
    overall_transparency_score = Column(Float, nullable=False)  # 0-100
    peer_group_rank = Column(Integer)  # Rank within peer group
    peer_group_percentile = Column(Float)  # Percentile within peer group
    
    # Contextual metrics
    cost_per_bed_transparency = Column(Float)  # Cost efficiency of transparency
    community_impact_score = Column(Float)     # Community service impact
    patient_satisfaction_score = Column(Float) # Patient satisfaction relative to size
    
    # Scoring metadata
    scoring_methodology = Column(String(100))  # Version of scoring algorithm
    last_calculated = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    hospital = relationship("Hospital", back_populates="transparency_scores")
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<HospitalTransparencyScore(hospital='{self.hospital.name}', score='{self.overall_transparency_score}')>"

class HospitalExcellenceRecognition(Base):
    """Hospital excellence recognition model"""
    __tablename__ = "hospital_excellence_recognition"
    
    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False)
    
    # Recognition details
    category = Column(Enum(TransparencyCategory), nullable=False)
    title = Column(String(255), nullable=False)  # e.g., "Small Hospital Transparency Leader"
    description = Column(Text)
    
    # Recognition metrics
    transparency_score = Column(Float, nullable=False)
    community_impact_score = Column(Float, nullable=False)
    cost_effectiveness_score = Column(Float, nullable=False)
    patient_satisfaction_score = Column(Float, nullable=False)
    
    # Recognition status
    is_featured = Column(Boolean, default=False)  # Featured on homepage
    is_spotlight = Column(Boolean, default=False)  # In spotlight section
    is_active = Column(Boolean, default=True)  # Currently active recognition
    
    # Recognition period
    recognition_start_date = Column(DateTime(timezone=True), server_default=func.now())
    recognition_end_date = Column(DateTime(timezone=True))
    
    # Recognition details
    achievements = Column(Text)  # JSON string of achievements
    community_impact_details = Column(Text)  # Details of community impact
    cost_optimization_details = Column(Text)  # Cost optimization achievements
    
    # Relationships
    hospital = relationship("Hospital", back_populates="excellence_recognition")
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<HospitalExcellenceRecognition(hospital='{self.hospital.name}', category='{self.category.value}')>"

class HospitalPeerGroup(Base):
    """Hospital peer group model for fair comparisons"""
    __tablename__ = "hospital_peer_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False)
    
    # Peer group classification
    peer_group_name = Column(String(100), nullable=False)  # e.g., "Small Community Hospitals"
    peer_group_size = Column(Integer, nullable=False)  # Number of hospitals in group
    
    # Peer group metrics
    group_avg_transparency_score = Column(Float, nullable=False)
    group_median_transparency_score = Column(Float, nullable=False)
    group_std_transparency_score = Column(Float, nullable=False)
    
    # Hospital's position in peer group
    rank_in_group = Column(Integer, nullable=False)
    percentile_in_group = Column(Float, nullable=False)
    
    # Peer group context
    group_avg_bed_count = Column(Float, nullable=False)
    group_avg_community_impact = Column(Float, nullable=False)
    group_avg_cost_effectiveness = Column(Float, nullable=False)
    
    # Comparison metrics
    transparency_vs_peers = Column(Float)  # How much above/below peer average
    cost_effectiveness_vs_peers = Column(Float)
    community_impact_vs_peers = Column(Float)
    
    # Peer group metadata
    group_calculation_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    hospital = relationship("Hospital", back_populates="peer_groups")
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<HospitalPeerGroup(hospital='{self.hospital.name}', group='{self.peer_group_name}')>"

class HospitalAccountabilityTier(Base):
    """Hospital accountability tier model for tiered enforcement"""
    __tablename__ = "hospital_accountability_tiers"
    
    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False)
    
    # Accountability tier
    tier = Column(String(50), nullable=False)  # "strict", "supportive", "educational"
    enforcement_level = Column(String(50), nullable=False)  # "high", "medium", "low"
    
    # Tier-specific metrics
    compliance_timeline_days = Column(Integer, nullable=False)  # Days to achieve compliance
    support_level = Column(String(50), nullable=False)  # "full", "partial", "minimal"
    enforcement_actions = Column(Text)  # JSON string of available actions
    
    # Tier justification
    tier_reason = Column(Text)  # Why this hospital is in this tier
    size_factor = Column(Boolean, default=False)  # Size was a factor in tier assignment
    resource_factor = Column(Boolean, default=False)  # Resources were a factor
    community_factor = Column(Boolean, default=False)  # Community impact was a factor
    
    # Tier effectiveness
    compliance_rate = Column(Float)  # Rate of compliance with tier requirements
    improvement_rate = Column(Float)  # Rate of improvement over time
    support_utilization = Column(Float)  # How much support is being used
    
    # Tier metadata
    tier_assignment_date = Column(DateTime(timezone=True), server_default=func.now())
    tier_review_date = Column(DateTime(timezone=True))  # When to review tier assignment
    
    # Relationships
    hospital = relationship("Hospital", back_populates="accountability_tiers")
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<HospitalAccountabilityTier(hospital='{self.hospital.name}', tier='{self.tier}')>"
