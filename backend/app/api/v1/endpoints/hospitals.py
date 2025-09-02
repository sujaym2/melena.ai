from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import structlog

from app.core.database import get_db
from app.models.hospital import Hospital, HospitalProcedure
from app.schemas.hospital import HospitalCreate, HospitalResponse, HospitalProcedureResponse
from app.services.data_collection.illinois_hospital_scraper import IllinoisHospitalScraper

router = APIRouter()
logger = structlog.get_logger()

@router.get("/", response_model=List[HospitalResponse])
async def get_hospitals(
    city: Optional[str] = Query(None, description="Filter by city"),
    state: Optional[str] = Query("IL", description="Filter by state"),
    hospital_type: Optional[str] = Query(None, description="Filter by hospital type"),
    db: Session = Depends(get_db)
):
    """Get all hospitals with optional filtering"""
    try:
        query = db.query(Hospital)
        
        if city:
            query = query.filter(Hospital.city.ilike(f"%{city}%"))
        if state:
            query = query.filter(Hospital.state == state)
        if hospital_type:
            query = query.filter(Hospital.hospital_type == hospital_type)
        
        hospitals = query.all()
        logger.info(f"Retrieved {len(hospitals)} hospitals")
        return hospitals
        
    except Exception as e:
        logger.error(f"Error retrieving hospitals: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{hospital_id}", response_model=HospitalResponse)
async def get_hospital(hospital_id: int, db: Session = Depends(get_db)):
    """Get a specific hospital by ID"""
    try:
        hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
        if not hospital:
            raise HTTPException(status_code=404, detail="Hospital not found")
        
        return hospital
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving hospital {hospital_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{hospital_id}/procedures", response_model=List[HospitalProcedureResponse])
async def get_hospital_procedures(
    hospital_id: int,
    cpt_code: Optional[str] = Query(None, description="Filter by CPT code"),
    procedure_name: Optional[str] = Query(None, description="Filter by procedure name"),
    db: Session = Depends(get_db)
):
    """Get all procedures for a specific hospital"""
    try:
        # Verify hospital exists
        hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
        if not hospital:
            raise HTTPException(status_code=404, detail="Hospital not found")
        
        query = db.query(HospitalProcedure).filter(HospitalProcedure.hospital_id == hospital_id)
        
        if cpt_code:
            query = query.filter(HospitalProcedure.cpt_code == cpt_code)
        if procedure_name:
            query = query.filter(HospitalProcedure.procedure_name.ilike(f"%{procedure_name}%"))
        
        procedures = query.all()
        logger.info(f"Retrieved {len(procedures)} procedures for hospital {hospital_id}")
        return procedures
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving procedures for hospital {hospital_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/", response_model=HospitalResponse)
async def create_hospital(hospital: HospitalCreate, db: Session = Depends(get_db)):
    """Create a new hospital"""
    try:
        db_hospital = Hospital(**hospital.dict())
        db.add(db_hospital)
        db.commit()
        db.refresh(db_hospital)
        
        logger.info(f"Created hospital: {db_hospital.name}")
        return db_hospital
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating hospital: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/search/procedures")
async def search_procedures(
    procedure_name: str = Query(..., description="Procedure name to search for"),
    city: Optional[str] = Query(None, description="Filter by city"),
    max_price: Optional[float] = Query(None, description="Maximum price filter"),
    db: Session = Depends(get_db)
):
    """Search for procedures across hospitals with pricing comparison"""
    try:
        query = db.query(HospitalProcedure).join(Hospital)
        
        if procedure_name:
            query = query.filter(HospitalProcedure.procedure_name.ilike(f"%{procedure_name}%"))
        if city:
            query = query.filter(Hospital.city.ilike(f"%{city}%"))
        if max_price:
            query = query.filter(HospitalProcedure.cash_price <= max_price)
        
        procedures = query.all()
        
        # Group by procedure for comparison
        procedure_groups = {}
        for proc in procedures:
            key = (proc.cpt_code, proc.procedure_name)
            if key not in procedure_groups:
                procedure_groups[key] = []
            procedure_groups[key].append(proc)
        
        # Format results for comparison
        comparison_results = []
        for (cpt_code, proc_name), hospital_procs in procedure_groups.items():
            comparison = {
                'cpt_code': cpt_code,
                'procedure_name': proc_name,
                'hospitals': []
            }
            
            for proc in hospital_procs:
                hospital_info = {
                    'hospital_name': proc.hospital.name,
                    'city': proc.hospital.city,
                    'cash_price': proc.cash_price,
                    'negotiated_rate_min': proc.negotiated_rate_min,
                    'negotiated_rate_max': proc.negotiated_rate_max,
                    'medicare_rate': proc.medicare_rate,
                    'medicaid_rate': proc.medicaid_rate
                }
                comparison['hospitals'].append(hospital_info)
            
            # Sort by cash price
            comparison['hospitals'].sort(key=lambda x: x['cash_price'] or float('inf'))
            comparison_results.append(comparison)
        
        logger.info(f"Found {len(comparison_results)} procedures matching search criteria")
        return {
            'search_term': procedure_name,
            'total_procedures': len(comparison_results),
            'results': comparison_results
        }
        
    except Exception as e:
        logger.error(f"Error searching procedures: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/scrape-data")
async def scrape_hospital_data(db: Session = Depends(get_db)):
    """Trigger data scraping for Illinois hospitals"""
    try:
        logger.info("Starting hospital data scraping...")
        
        # Run scraper
        async with IllinoisHospitalScraper() as scraper:
            results = await scraper.scrape_all_hospitals()
        
        # Process results and save to database
        total_procedures = 0
        for hospital_name, procedures in results.items():
            logger.info(f"Processing {len(procedures)} procedures for {hospital_name}")
            total_procedures += len(procedures)
            
            # Here you would save the scraped data to the database
            # For now, just log the results
        
        logger.info(f"Data scraping completed. Total procedures found: {total_procedures}")
        
        return {
            'status': 'success',
            'message': f'Data scraping completed. Found {total_procedures} procedures.',
            'hospitals_processed': len(results),
            'total_procedures': total_procedures
        }
        
    except Exception as e:
        logger.error(f"Error during data scraping: {e}")
        raise HTTPException(status_code=500, detail=f"Data scraping failed: {str(e)}")

@router.get("/illinois/overview")
async def get_illinois_overview(db: Session = Depends(get_db)):
    """Get overview of Illinois healthcare data"""
    try:
        # Get Illinois hospitals
        illinois_hospitals = db.query(Hospital).filter(Hospital.state == "IL").all()
        
        # Get procedure counts
        total_procedures = db.query(HospitalProcedure).join(Hospital).filter(Hospital.state == "IL").count()
        
        # Get cities with hospitals
        cities = db.query(Hospital.city).filter(Hospital.state == "IL").distinct().all()
        cities = [city[0] for city in cities]
        
        # Get hospital types
        hospital_types = db.query(Hospital.hospital_type).filter(Hospital.state == "IL").distinct().all()
        hospital_types = [ht[0] for ht in hospital_types if ht[0]]
        
        overview = {
            'total_hospitals': len(illinois_hospitals),
            'total_procedures': total_procedures,
            'cities': cities,
            'hospital_types': hospital_types,
            'regions': {
                'chicago_metro': len([h for h in illinois_hospitals if 'chicago' in h.city.lower()]),
                'central_illinois': len([h for h in illinois_hospitals if any(city in h.city.lower() for city in ['peoria', 'springfield', 'bloomington'])]),
                'southern_illinois': len([h for h in illinois_hospitals if any(city in h.city.lower() for city in ['carbondale', 'edwardsville', 'belleville'])])
            }
        }
        
        return overview
        
    except Exception as e:
        logger.error(f"Error getting Illinois overview: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
