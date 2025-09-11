from fastapi import APIRouter
from app.api.v1.endpoints import hospitals, procedures, insurance, medications, analytics, hospital_excellence

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(hospitals.router, prefix="/hospitals", tags=["hospitals"])
api_router.include_router(procedures.router, prefix="/procedures", tags=["procedures"])
api_router.include_router(insurance.router, prefix="/insurance", tags=["insurance"])
api_router.include_router(medications.router, prefix="/medications", tags=["medications"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(hospital_excellence.router, prefix="/hospital-excellence", tags=["hospital-excellence"])
