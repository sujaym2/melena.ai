import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import structlog
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models.hospital import Hospital
from app.models.hospital_scoring import (
    HospitalTransparencyScore, HospitalExcellenceRecognition, 
    HospitalPeerGroup, HospitalAccountabilityTier,
    HospitalSize, TransparencyCategory
)
from app.core.database import SessionLocal

logger = structlog.get_logger()

class HospitalScoringService:
    """Service for fair hospital transparency scoring and recognition"""
    
    def __init__(self):
        self.scoring_weights = {
            HospitalSize.SMALL: {
                'data_accessibility': 0.4,  # Higher weight - easier to achieve
                'data_completeness': 0.3,   # Lower weight - harder for small hospitals
                'data_accuracy': 0.2,
                'update_frequency': 0.1
            },
            HospitalSize.MEDIUM: {
                'data_accessibility': 0.3,
                'data_completeness': 0.3,
                'data_accuracy': 0.25,
                'update_frequency': 0.15
            },
            HospitalSize.LARGE: {
                'data_accessibility': 0.2,
                'data_completeness': 0.3,
                'data_accuracy': 0.3,
                'update_frequency': 0.2
            }
        }
    
    def calculate_hospital_size(self, bed_count: Optional[int]) -> HospitalSize:
        """Determine hospital size category based on bed count"""
        if not bed_count:
            return HospitalSize.SMALL  # Default to small if unknown
        
        if bed_count < 50:
            return HospitalSize.SMALL
        elif bed_count < 200:
            return HospitalSize.MEDIUM
        else:
            return HospitalSize.LARGE
    
    def calculate_transparency_scores(self, hospital: Hospital) -> Dict[str, float]:
        """Calculate transparency scores for a hospital"""
        try:
            # Get hospital size
            hospital_size = self.calculate_hospital_size(hospital.bed_count)
            
            # Calculate individual scores (0-100 scale)
            scores = {
                'data_accessibility': self._calculate_accessibility_score(hospital),
                'data_completeness': self._calculate_completeness_score(hospital),
                'data_accuracy': self._calculate_accuracy_score(hospital),
                'update_frequency': self._calculate_frequency_score(hospital)
            }
            
            # Apply size-adjusted weights
            weights = self.scoring_weights[hospital_size]
            weighted_scores = {
                'weighted_accessibility': scores['data_accessibility'] * weights['data_accessibility'],
                'weighted_completeness': scores['data_completeness'] * weights['data_completeness'],
                'weighted_accuracy': scores['data_accuracy'] * weights['data_accuracy'],
                'weighted_frequency': scores['update_frequency'] * weights['update_frequency']
            }
            
            # Calculate overall score
            overall_score = sum(weighted_scores.values())
            
            # Add contextual metrics
            scores.update(weighted_scores)
            scores['overall_transparency_score'] = overall_score
            scores['hospital_size'] = hospital_size
            scores['cost_per_bed_transparency'] = self._calculate_cost_per_bed(hospital, overall_score)
            scores['community_impact_score'] = self._calculate_community_impact(hospital)
            scores['patient_satisfaction_score'] = self._calculate_patient_satisfaction(hospital)
            
            return scores
            
        except Exception as e:
            logger.error(f"Error calculating transparency scores for hospital {hospital.id}: {e}")
            return {}
    
    def _calculate_accessibility_score(self, hospital: Hospital) -> float:
        """Calculate data accessibility score (0-100)"""
        score = 0
        
        # Check if transparency file URL exists and is accessible
        if hospital.transparency_file_url:
            score += 40
        
        # Check if data is in machine-readable format
        if hospital.transparency_file_url and any(ext in hospital.transparency_file_url.lower() 
                                                for ext in ['.csv', '.json', '.xml']):
            score += 30
        
        # Check if data is easily findable on website
        if hospital.website:
            score += 20
        
        # Check if data is updated recently
        if hospital.last_data_update and (datetime.now() - hospital.last_data_update).days < 30:
            score += 10
        
        return min(score, 100)
    
    def _calculate_completeness_score(self, hospital: Hospital) -> float:
        """Calculate data completeness score (0-100)"""
        score = 0
        
        # Check if hospital has procedure data
        if hospital.procedures:
            procedure_count = len(hospital.procedures)
            if procedure_count > 1000:
                score += 40
            elif procedure_count > 500:
                score += 30
            elif procedure_count > 100:
                score += 20
            else:
                score += 10
        
        # Check if data includes multiple price types
        if hospital.procedures:
            price_types = set()
            for proc in hospital.procedures:
                if proc.cash_price:
                    price_types.add('cash')
                if proc.negotiated_rate_min:
                    price_types.add('negotiated')
                if proc.medicare_rate:
                    price_types.add('medicare')
                if proc.medicaid_rate:
                    price_types.add('medicaid')
            
            score += min(len(price_types) * 15, 60)
        
        return min(score, 100)
    
    def _calculate_accuracy_score(self, hospital: Hospital) -> float:
        """Calculate data accuracy score (0-100)"""
        score = 0
        
        # Check data quality score
        if hospital.data_quality_score:
            score += hospital.data_quality_score * 0.6
        
        # Check if data is consistent
        if hospital.procedures:
            # Check for reasonable price ranges
            reasonable_prices = 0
            total_prices = 0
            
            for proc in hospital.procedures:
                if proc.cash_price and proc.medicare_rate:
                    if 0.5 <= proc.cash_price / proc.medicare_rate <= 10:  # Reasonable range
                        reasonable_prices += 1
                    total_prices += 1
            
            if total_prices > 0:
                score += (reasonable_prices / total_prices) * 40
        
        return min(score, 100)
    
    def _calculate_frequency_score(self, hospital: Hospital) -> float:
        """Calculate update frequency score (0-100)"""
        if not hospital.last_data_update:
            return 0
        
        days_since_update = (datetime.now() - hospital.last_data_update).days
        
        if days_since_update <= 7:
            return 100
        elif days_since_update <= 30:
            return 80
        elif days_since_update <= 90:
            return 60
        elif days_since_update <= 180:
            return 40
        else:
            return 20
    
    def _calculate_cost_per_bed(self, hospital: Hospital, transparency_score: float) -> float:
        """Calculate cost per bed for transparency compliance"""
        if not hospital.bed_count or hospital.bed_count == 0:
            return 0
        
        # Estimate transparency compliance cost (simplified)
        estimated_cost = transparency_score * 100  # $100 per point
        return estimated_cost / hospital.bed_count
    
    def _calculate_community_impact(self, hospital: Hospital) -> float:
        """Calculate community impact score (0-100)"""
        score = 0
        
        # Check if hospital participates in community programs
        if hospital.medicaid_participant:
            score += 25
        if hospital.medicare_participant:
            score += 25
        
        # Check if hospital is in rural area
        if hospital.illinois_region and 'rural' in hospital.illinois_region.lower():
            score += 20
        
        # Check if hospital is critical access
        if hospital.hospital_type and 'critical access' in hospital.hospital_type.lower():
            score += 30
        
        return min(score, 100)
    
    def _calculate_patient_satisfaction(self, hospital: Hospital) -> float:
        """Calculate patient satisfaction score (0-100)"""
        # This would typically come from patient satisfaction surveys
        # For now, use a simplified calculation based on hospital characteristics
        
        score = 50  # Base score
        
        # Adjust based on hospital size (smaller hospitals often have higher satisfaction)
        if hospital.bed_count:
            if hospital.bed_count < 50:
                score += 20
            elif hospital.bed_count < 200:
                score += 10
        
        # Adjust based on community focus
        if hospital.illinois_region and 'community' in hospital.illinois_region.lower():
            score += 15
        
        return min(score, 100)
    
    def create_peer_groups(self, db: Session) -> Dict[str, List[Hospital]]:
        """Create peer groups for fair hospital comparisons"""
        try:
            # Get all hospitals
            hospitals = db.query(Hospital).all()
            
            # Group by size
            peer_groups = {
                'Small Community Hospitals': [],
                'Medium Regional Hospitals': [],
                'Large Hospital Systems': []
            }
            
            for hospital in hospitals:
                size = self.calculate_hospital_size(hospital.bed_count)
                
                if size == HospitalSize.SMALL:
                    peer_groups['Small Community Hospitals'].append(hospital)
                elif size == HospitalSize.MEDIUM:
                    peer_groups['Medium Regional Hospitals'].append(hospital)
                else:
                    peer_groups['Large Hospital Systems'].append(hospital)
            
            # Calculate peer group metrics
            for group_name, group_hospitals in peer_groups.items():
                if group_hospitals:
                    self._calculate_peer_group_metrics(db, group_name, group_hospitals)
            
            return peer_groups
            
        except Exception as e:
            logger.error(f"Error creating peer groups: {e}")
            return {}
    
    def _calculate_peer_group_metrics(self, db: Session, group_name: str, hospitals: List[Hospital]):
        """Calculate metrics for a peer group"""
        try:
            transparency_scores = []
            bed_counts = []
            community_impacts = []
            cost_effectiveness = []
            
            for hospital in hospitals:
                # Get or calculate transparency score
                score = db.query(HospitalTransparencyScore).filter(
                    HospitalTransparencyScore.hospital_id == hospital.id
                ).first()
                
                if score:
                    transparency_scores.append(score.overall_transparency_score)
                    community_impacts.append(score.community_impact_score)
                    cost_effectiveness.append(score.cost_per_bed_transparency)
                
                if hospital.bed_count:
                    bed_counts.append(hospital.bed_count)
            
            if transparency_scores:
                # Calculate group statistics
                avg_transparency = np.mean(transparency_scores)
                median_transparency = np.median(transparency_scores)
                std_transparency = np.std(transparency_scores)
                
                avg_bed_count = np.mean(bed_counts) if bed_counts else 0
                avg_community_impact = np.mean(community_impacts) if community_impacts else 0
                avg_cost_effectiveness = np.mean(cost_effectiveness) if cost_effectiveness else 0
                
                # Update peer group records for each hospital
                for i, hospital in enumerate(hospitals):
                    peer_group = HospitalPeerGroup(
                        hospital_id=hospital.id,
                        peer_group_name=group_name,
                        peer_group_size=len(hospitals),
                        group_avg_transparency_score=avg_transparency,
                        group_median_transparency_score=median_transparency,
                        group_std_transparency_score=std_transparency,
                        rank_in_group=i + 1,  # Will be updated with actual ranking
                        percentile_in_group=0,  # Will be calculated
                        group_avg_bed_count=avg_bed_count,
                        group_avg_community_impact=avg_community_impact,
                        group_avg_cost_effectiveness=avg_cost_effectiveness
                    )
                    
                    db.add(peer_group)
                
                db.commit()
                logger.info(f"Created peer group metrics for {group_name} with {len(hospitals)} hospitals")
                
        except Exception as e:
            logger.error(f"Error calculating peer group metrics for {group_name}: {e}")
            db.rollback()
    
    def assign_accountability_tiers(self, db: Session) -> Dict[str, List[Hospital]]:
        """Assign accountability tiers based on hospital size and characteristics"""
        try:
            hospitals = db.query(Hospital).all()
            
            tiers = {
                'strict': [],      # Large hospitals - strict enforcement
                'supportive': [],  # Medium hospitals - supportive assistance
                'educational': []  # Small hospitals - educational support
            }
            
            for hospital in hospitals:
                size = self.calculate_hospital_size(hospital.bed_count)
                
                if size == HospitalSize.LARGE:
                    tier = 'strict'
                    enforcement_level = 'high'
                    compliance_timeline = 30
                    support_level = 'minimal'
                elif size == HospitalSize.MEDIUM:
                    tier = 'supportive'
                    enforcement_level = 'medium'
                    compliance_timeline = 60
                    support_level = 'partial'
                else:
                    tier = 'educational'
                    enforcement_level = 'low'
                    compliance_timeline = 90
                    support_level = 'full'
                
                # Create accountability tier record
                accountability_tier = HospitalAccountabilityTier(
                    hospital_id=hospital.id,
                    tier=tier,
                    enforcement_level=enforcement_level,
                    compliance_timeline_days=compliance_timeline,
                    support_level=support_level,
                    enforcement_actions=self._get_enforcement_actions(tier),
                    tier_reason=f"Assigned based on hospital size ({size.value}) and resources",
                    size_factor=True,
                    resource_factor=True,
                    community_factor=size == HospitalSize.SMALL
                )
                
                db.add(accountability_tier)
                tiers[tier].append(hospital)
            
            db.commit()
            logger.info(f"Assigned accountability tiers: {len(tiers['strict'])} strict, {len(tiers['supportive'])} supportive, {len(tiers['educational'])} educational")
            
            return tiers
            
        except Exception as e:
            logger.error(f"Error assigning accountability tiers: {e}")
            db.rollback()
            return {}
    
    def _get_enforcement_actions(self, tier: str) -> str:
        """Get available enforcement actions for a tier"""
        actions = {
            'strict': [
                'public_compliance_monitoring',
                'regulatory_complaint_filing',
                'media_pressure_campaigns',
                'legal_action_support'
            ],
            'supportive': [
                'compliance_assistance',
                'gradual_improvement_timelines',
                'partnership_opportunities',
                'positive_reinforcement'
            ],
            'educational': [
                'educational_resources',
                'flexible_compliance_timelines',
                'community_partnership_promotion',
                'achievement_celebration'
            ]
        }
        
        import json
        return json.dumps(actions.get(tier, []))
    
    def identify_excellence_candidates(self, db: Session) -> List[Dict]:
        """Identify hospitals for excellence recognition"""
        try:
            excellence_candidates = []
            
            # Get hospitals with high transparency scores
            high_scoring_hospitals = db.query(HospitalTransparencyScore).filter(
                HospitalTransparencyScore.overall_transparency_score >= 80
            ).all()
            
            for score in high_scoring_hospitals:
                hospital = score.hospital
                size = self.calculate_hospital_size(hospital.bed_count)
                
                # Determine excellence category
                if size == HospitalSize.SMALL:
                    if score.community_impact_score >= 70:
                        category = TransparencyCategory.SMALL_HOSPITAL_EXCELLENCE
                        title = "Small Hospital Transparency Leader"
                    else:
                        category = TransparencyCategory.COMMUNITY_FOCUS
                        title = "Community Healthcare Champion"
                elif size == HospitalSize.MEDIUM:
                    category = TransparencyCategory.RURAL_INNOVATION
                    title = "Regional Healthcare Innovation Leader"
                else:
                    category = TransparencyCategory.CRITICAL_ACCESS_EXCELLENCE
                    title = "Large Hospital Transparency Excellence"
                
                # Create excellence recognition
                recognition = HospitalExcellenceRecognition(
                    hospital_id=hospital.id,
                    category=category,
                    title=title,
                    description=f"Recognized for outstanding transparency practices and community impact",
                    transparency_score=score.overall_transparency_score,
                    community_impact_score=score.community_impact_score,
                    cost_effectiveness_score=score.cost_per_bed_transparency,
                    patient_satisfaction_score=score.patient_satisfaction_score,
                    is_featured=True,
                    is_spotlight=score.overall_transparency_score >= 90,
                    achievements=json.dumps([
                        f"Transparency Score: {score.overall_transparency_score:.1f}/100",
                        f"Community Impact: {score.community_impact_score:.1f}/100",
                        f"Cost Effectiveness: {score.cost_per_bed_transparency:.1f} per bed"
                    ]),
                    community_impact_details=f"Demonstrates exceptional commitment to community healthcare and transparency",
                    cost_optimization_details=f"Achieves high transparency compliance at {score.cost_per_bed_transparency:.1f} cost per bed"
                )
                
                db.add(recognition)
                excellence_candidates.append({
                    'hospital': hospital,
                    'recognition': recognition,
                    'category': category,
                    'title': title
                })
            
            db.commit()
            logger.info(f"Identified {len(excellence_candidates)} excellence candidates")
            
            return excellence_candidates
            
        except Exception as e:
            logger.error(f"Error identifying excellence candidates: {e}")
            db.rollback()
            return []
    
    def run_complete_scoring_analysis(self, db: Session) -> Dict:
        """Run complete scoring analysis for all hospitals"""
        try:
            logger.info("Starting complete hospital scoring analysis...")
            
            # Get all hospitals
            hospitals = db.query(Hospital).all()
            
            # Calculate transparency scores
            scoring_results = []
            for hospital in hospitals:
                scores = self.calculate_transparency_scores(hospital)
                if scores:
                    # Save transparency score
                    transparency_score = HospitalTransparencyScore(
                        hospital_id=hospital.id,
                        hospital_size=scores['hospital_size'],
                        data_accessibility_score=scores['data_accessibility'],
                        data_completeness_score=scores['data_completeness'],
                        data_accuracy_score=scores['data_accuracy'],
                        update_frequency_score=scores['update_frequency'],
                        weighted_accessibility=scores['weighted_accessibility'],
                        weighted_completeness=scores['weighted_completeness'],
                        weighted_accuracy=scores['weighted_accuracy'],
                        weighted_frequency=scores['weighted_frequency'],
                        overall_transparency_score=scores['overall_transparency_score'],
                        cost_per_bed_transparency=scores['cost_per_bed_transparency'],
                        community_impact_score=scores['community_impact_score'],
                        patient_satisfaction_score=scores['patient_satisfaction_score'],
                        scoring_methodology="v1.0"
                    )
                    
                    db.add(transparency_score)
                    scoring_results.append({
                        'hospital': hospital,
                        'scores': scores
                    })
            
            db.commit()
            
            # Create peer groups
            peer_groups = self.create_peer_groups(db)
            
            # Assign accountability tiers
            accountability_tiers = self.assign_accountability_tiers(db)
            
            # Identify excellence candidates
            excellence_candidates = self.identify_excellence_candidates(db)
            
            # Calculate summary statistics
            summary = {
                'total_hospitals': len(hospitals),
                'scoring_results': len(scoring_results),
                'peer_groups': {name: len(hospitals) for name, hospitals in peer_groups.items()},
                'accountability_tiers': {tier: len(hospitals) for tier, hospitals in accountability_tiers.items()},
                'excellence_candidates': len(excellence_candidates),
                'analysis_date': datetime.now()
            }
            
            logger.info(f"Complete scoring analysis finished: {summary}")
            
            return summary
            
        except Exception as e:
            logger.error(f"Error in complete scoring analysis: {e}")
            db.rollback()
            return {}

def run_hospital_scoring_analysis():
    """Run hospital scoring analysis"""
    db = SessionLocal()
    try:
        scoring_service = HospitalScoringService()
        results = scoring_service.run_complete_scoring_analysis(db)
        return results
    finally:
        db.close()

if __name__ == "__main__":
    run_hospital_scoring_analysis()
