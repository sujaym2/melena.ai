from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import structlog

from app.core.database import get_db
from app.models.hospital import Hospital
from app.models.hospital_scoring import (
    HospitalTransparencyScore, HospitalExcellenceRecognition, 
    HospitalPeerGroup, HospitalAccountabilityTier,
    TransparencyCategory, HospitalSize
)
from app.services.hospital_scoring import HospitalScoringService
from app.schemas.hospital_excellence import (
    HospitalExcellenceResponse, PeerGroupComparison, 
    AccountabilityTierResponse, TransparencyScoreResponse
)

router = APIRouter()
logger = structlog.get_logger()

@router.get("/excellence/featured", response_model=List[HospitalExcellenceResponse])
async def get_featured_hospitals(
    category: Optional[TransparencyCategory] = Query(None, description="Filter by excellence category"),
    limit: int = Query(10, description="Number of hospitals to return"),
    db: Session = Depends(get_db)
):
    """Get featured hospitals for excellence recognition"""
    try:
        query = db.query(HospitalExcellenceRecognition).filter(
            HospitalExcellenceRecognition.is_featured == True,
            HospitalExcellenceRecognition.is_active == True
        )
        
        if category:
            query = query.filter(HospitalExcellenceRecognition.category == category)
        
        recognitions = query.limit(limit).all()
        
        logger.info(f"Retrieved {len(recognitions)} featured hospitals")
        return recognitions
        
    except Exception as e:
        logger.error(f"Error retrieving featured hospitals: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/excellence/spotlight", response_model=List[HospitalExcellenceResponse])
async def get_spotlight_hospitals(
    limit: int = Query(5, description="Number of spotlight hospitals to return"),
    db: Session = Depends(get_db)
):
    """Get hospitals in the spotlight section"""
    try:
        recognitions = db.query(HospitalExcellenceRecognition).filter(
            HospitalExcellenceRecognition.is_spotlight == True,
            HospitalExcellenceRecognition.is_active == True
        ).limit(limit).all()
        
        logger.info(f"Retrieved {len(recognitions)} spotlight hospitals")
        return recognitions
        
    except Exception as e:
        logger.error(f"Error retrieving spotlight hospitals: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/excellence/categories")
async def get_excellence_categories(db: Session = Depends(get_db)):
    """Get all excellence categories with counts"""
    try:
        categories = {}
        
        for category in TransparencyCategory:
            count = db.query(HospitalExcellenceRecognition).filter(
                HospitalExcellenceRecognition.category == category,
                HospitalExcellenceRecognition.is_active == True
            ).count()
            
            categories[category.value] = {
                'name': category.value.replace('_', ' ').title(),
                'count': count,
                'description': _get_category_description(category)
            }
        
        return categories
        
    except Exception as e:
        logger.error(f"Error retrieving excellence categories: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/excellence/{hospital_id}", response_model=HospitalExcellenceResponse)
async def get_hospital_excellence(
    hospital_id: int,
    db: Session = Depends(get_db)
):
    """Get excellence recognition for a specific hospital"""
    try:
        recognition = db.query(HospitalExcellenceRecognition).filter(
            HospitalExcellenceRecognition.hospital_id == hospital_id,
            HospitalExcellenceRecognition.is_active == True
        ).first()
        
        if not recognition:
            raise HTTPException(status_code=404, detail="No excellence recognition found for this hospital")
        
        return recognition
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving hospital excellence for {hospital_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/peer-groups", response_model=List[PeerGroupComparison])
async def get_peer_groups(
    group_name: Optional[str] = Query(None, description="Filter by peer group name"),
    db: Session = Depends(get_db)
):
    """Get hospital peer groups for fair comparisons"""
    try:
        query = db.query(HospitalPeerGroup)
        
        if group_name:
            query = query.filter(HospitalPeerGroup.peer_group_name == group_name)
        
        peer_groups = query.all()
        
        # Group by peer group name
        grouped_results = {}
        for pg in peer_groups:
            if pg.peer_group_name not in grouped_results:
                grouped_results[pg.peer_group_name] = {
                    'group_name': pg.peer_group_name,
                    'group_size': pg.peer_group_size,
                    'group_avg_transparency_score': pg.group_avg_transparency_score,
                    'group_median_transparency_score': pg.group_median_transparency_score,
                    'group_std_transparency_score': pg.group_std_transparency_score,
                    'group_avg_bed_count': pg.group_avg_bed_count,
                    'group_avg_community_impact': pg.group_avg_community_impact,
                    'group_avg_cost_effectiveness': pg.group_avg_cost_effectiveness,
                    'hospitals': []
                }
            
            grouped_results[pg.peer_group_name]['hospitals'].append({
                'hospital_id': pg.hospital_id,
                'hospital_name': pg.hospital.name,
                'rank_in_group': pg.rank_in_group,
                'percentile_in_group': pg.percentile_in_group,
                'transparency_vs_peers': pg.transparency_vs_peers,
                'cost_effectiveness_vs_peers': pg.cost_effectiveness_vs_peers,
                'community_impact_vs_peers': pg.community_impact_vs_peers
            })
        
        # Convert to list and sort hospitals within each group
        result = []
        for group_data in grouped_results.values():
            group_data['hospitals'].sort(key=lambda x: x['rank_in_group'])
            result.append(group_data)
        
        logger.info(f"Retrieved {len(result)} peer groups")
        return result
        
    except Exception as e:
        logger.error(f"Error retrieving peer groups: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/peer-groups/{hospital_id}", response_model=PeerGroupComparison)
async def get_hospital_peer_group(
    hospital_id: int,
    db: Session = Depends(get_db)
):
    """Get peer group information for a specific hospital"""
    try:
        peer_group = db.query(HospitalPeerGroup).filter(
            HospitalPeerGroup.hospital_id == hospital_id
        ).first()
        
        if not peer_group:
            raise HTTPException(status_code=404, detail="No peer group found for this hospital")
        
        # Get all hospitals in the same peer group
        group_hospitals = db.query(HospitalPeerGroup).filter(
            HospitalPeerGroup.peer_group_name == peer_group.peer_group_name
        ).all()
        
        result = {
            'group_name': peer_group.peer_group_name,
            'group_size': peer_group.peer_group_size,
            'group_avg_transparency_score': peer_group.group_avg_transparency_score,
            'group_median_transparency_score': peer_group.group_median_transparency_score,
            'group_std_transparency_score': peer_group.group_std_transparency_score,
            'group_avg_bed_count': peer_group.group_avg_bed_count,
            'group_avg_community_impact': peer_group.group_avg_community_impact,
            'group_avg_cost_effectiveness': peer_group.group_avg_cost_effectiveness,
            'hospitals': []
        }
        
        for pg in group_hospitals:
            result['hospitals'].append({
                'hospital_id': pg.hospital_id,
                'hospital_name': pg.hospital.name,
                'rank_in_group': pg.rank_in_group,
                'percentile_in_group': pg.percentile_in_group,
                'transparency_vs_peers': pg.transparency_vs_peers,
                'cost_effectiveness_vs_peers': pg.cost_effectiveness_vs_peers,
                'community_impact_vs_peers': pg.community_impact_vs_peers
            })
        
        # Sort hospitals by rank
        result['hospitals'].sort(key=lambda x: x['rank_in_group'])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving peer group for hospital {hospital_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/accountability-tiers", response_model=List[AccountabilityTierResponse])
async def get_accountability_tiers(
    tier: Optional[str] = Query(None, description="Filter by accountability tier"),
    db: Session = Depends(get_db)
):
    """Get hospital accountability tiers"""
    try:
        query = db.query(HospitalAccountabilityTier)
        
        if tier:
            query = query.filter(HospitalAccountabilityTier.tier == tier)
        
        tiers = query.all()
        
        logger.info(f"Retrieved {len(tiers)} accountability tiers")
        return tiers
        
    except Exception as e:
        logger.error(f"Error retrieving accountability tiers: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/transparency-scores", response_model=List[TransparencyScoreResponse])
async def get_transparency_scores(
    hospital_size: Optional[HospitalSize] = Query(None, description="Filter by hospital size"),
    min_score: Optional[float] = Query(None, description="Minimum transparency score"),
    max_score: Optional[float] = Query(None, description="Maximum transparency score"),
    limit: int = Query(50, description="Number of results to return"),
    db: Session = Depends(get_db)
):
    """Get hospital transparency scores with filtering"""
    try:
        query = db.query(HospitalTransparencyScore)
        
        if hospital_size:
            query = query.filter(HospitalTransparencyScore.hospital_size == hospital_size)
        
        if min_score is not None:
            query = query.filter(HospitalTransparencyScore.overall_transparency_score >= min_score)
        
        if max_score is not None:
            query = query.filter(HospitalTransparencyScore.overall_transparency_score <= max_score)
        
        scores = query.limit(limit).all()
        
        logger.info(f"Retrieved {len(scores)} transparency scores")
        return scores
        
    except Exception as e:
        logger.error(f"Error retrieving transparency scores: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/scoring/run-analysis")
async def run_scoring_analysis(db: Session = Depends(get_db)):
    """Run complete hospital scoring analysis"""
    try:
        logger.info("Starting hospital scoring analysis...")
        
        scoring_service = HospitalScoringService()
        results = scoring_service.run_complete_scoring_analysis(db)
        
        return {
            'status': 'success',
            'message': 'Hospital scoring analysis completed successfully',
            'results': results
        }
        
    except Exception as e:
        logger.error(f"Error running scoring analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Scoring analysis failed: {str(e)}")

@router.get("/small-hospitals/excellence")
async def get_small_hospital_excellence(
    limit: int = Query(10, description="Number of small hospitals to return"),
    db: Session = Depends(get_db)
):
    """Get small hospitals demonstrating excellence"""
    try:
        # Get small hospitals with high transparency scores
        small_hospitals = db.query(HospitalTransparencyScore).join(Hospital).filter(
            HospitalTransparencyScore.hospital_size == HospitalSize.SMALL,
            HospitalTransparencyScore.overall_transparency_score >= 70
        ).limit(limit).all()
        
        results = []
        for score in small_hospitals:
            hospital = score.hospital
            
            # Check if hospital has excellence recognition
            recognition = db.query(HospitalExcellenceRecognition).filter(
                HospitalExcellenceRecognition.hospital_id == hospital.id,
                HospitalExcellenceRecognition.is_active == True
            ).first()
            
            results.append({
                'hospital': {
                    'id': hospital.id,
                    'name': hospital.name,
                    'city': hospital.city,
                    'bed_count': hospital.bed_count,
                    'hospital_type': hospital.hospital_type
                },
                'transparency_score': score.overall_transparency_score,
                'community_impact_score': score.community_impact_score,
                'cost_effectiveness': score.cost_per_bed_transparency,
                'excellence_recognition': recognition.title if recognition else None,
                'is_featured': recognition.is_featured if recognition else False,
                'is_spotlight': recognition.is_spotlight if recognition else False
            })
        
        # Sort by transparency score
        results.sort(key=lambda x: x['transparency_score'], reverse=True)
        
        logger.info(f"Retrieved {len(results)} small hospital excellence examples")
        return {
            'small_hospitals': results,
            'total_count': len(results),
            'description': 'Small hospitals demonstrating excellence in transparency and community impact'
        }
        
    except Exception as e:
        logger.error(f"Error retrieving small hospital excellence: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/rural-hospitals/heroes")
async def get_rural_hospital_heroes(
    limit: int = Query(10, description="Number of rural hospitals to return"),
    db: Session = Depends(get_db)
):
    """Get rural hospitals demonstrating heroism in healthcare"""
    try:
        # Get rural hospitals with high community impact
        rural_hospitals = db.query(HospitalTransparencyScore).join(Hospital).filter(
            HospitalTransparencyScore.hospital_size == HospitalSize.SMALL,
            HospitalTransparencyScore.community_impact_score >= 60,
            Hospital.city.ilike('%rural%') | Hospital.illinois_region.ilike('%rural%')
        ).limit(limit).all()
        
        results = []
        for score in rural_hospitals:
            hospital = score.hospital
            
            results.append({
                'hospital': {
                    'id': hospital.id,
                    'name': hospital.name,
                    'city': hospital.city,
                    'county': hospital.county,
                    'bed_count': hospital.bed_count,
                    'hospital_type': hospital.hospital_type
                },
                'transparency_score': score.overall_transparency_score,
                'community_impact_score': score.community_impact_score,
                'cost_effectiveness': score.cost_per_bed_transparency,
                'rural_hero_qualities': [
                    'Essential community healthcare provider',
                    'High community impact score',
                    'Cost-effective transparency practices',
                    'Rural healthcare access champion'
                ]
            })
        
        # Sort by community impact score
        results.sort(key=lambda x: x['community_impact_score'], reverse=True)
        
        logger.info(f"Retrieved {len(results)} rural hospital heroes")
        return {
            'rural_heroes': results,
            'total_count': len(results),
            'description': 'Rural hospitals demonstrating heroism in community healthcare'
        }
        
    except Exception as e:
        logger.error(f"Error retrieving rural hospital heroes: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

def _get_category_description(category: TransparencyCategory) -> str:
    """Get description for excellence category"""
    descriptions = {
        TransparencyCategory.SMALL_HOSPITAL_EXCELLENCE: "Small hospitals demonstrating outstanding transparency practices",
        TransparencyCategory.RURAL_INNOVATION: "Rural hospitals showing innovation in healthcare delivery",
        TransparencyCategory.COMMUNITY_FOCUS: "Hospitals with exceptional community focus and impact",
        TransparencyCategory.CRITICAL_ACCESS_EXCELLENCE: "Critical access hospitals providing essential community services",
        TransparencyCategory.COMMUNITY_PARTNERSHIP: "Hospitals with outstanding community partnerships"
    }
    return descriptions.get(category, "Excellence in healthcare transparency and community impact")
