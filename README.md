# Melena.ai - Healthcare Transparency & Cost Optimization

## Mission
Empowering patients with transparent healthcare pricing and cost optimization through AI-powered data aggregation, insurance navigation, and medication cost analysis.

## Initial Market: Illinois (Chicago Metro Area)
Starting with Chicago-area hospitals to validate models and expand statewide.

## Core Services

### 1. Hospital Price Transparency
- Aggregate and normalize hospital pricing data
- Patient-friendly cost comparison interfaces
- Procedure-specific pricing breakdowns
- Insurance vs. cash price comparisons
- **Fair hospital scoring with size-adjusted metrics**
- **Hospital accountability and compliance monitoring**

### 2. Insurance Navigation & Appeals
- AI-powered claim analysis
- Overcharge detection algorithms
- Automated appeal letter generation
- Claims tracking and optimization

### 3. Primary Care Support
- Triage assistance and risk assessment
- Preventive care recommendations
- Administrative workflow optimization

### 4. Medication Cost Optimization
- Real-time pharmacy price comparison
- Generic alternative identification
- Prescription discount program matching
- Cost-saving recommendations

### 5. Hospital Excellence Recognition
- **Small Hospital Excellence Awards**
- **Rural Healthcare Hero Recognition**
- **Community Impact Assessment**
- **Peer Group Comparisons**
- **Tiered Accountability System**

## Technical Stack

### Backend
- **Python/FastAPI** - API development
- **PostgreSQL** - Primary database
- **Redis** - Caching and session management
- **Celery** - Background task processing

### AI/ML
- **TensorFlow/PyTorch** - Machine learning models
- **Pandas/NumPy** - Data processing
- **Scikit-learn** - Statistical modeling
- **NLTK/spaCy** - Natural language processing

### Frontend
- **React/TypeScript** - Web application
- **Next.js** - Server-side rendering
- **Tailwind CSS** - Styling
- **Chart.js** - Data visualization

### Infrastructure
- **Docker** - Containerization
- **AWS/GCP** - Cloud hosting
- **Terraform** - Infrastructure as code
- **GitHub Actions** - CI/CD

## Data Sources

### Illinois Healthcare Data
- Illinois Department of Public Health
- Illinois Hospital Association
- Chicago Department of Public Health
- Individual hospital transparency files

### External APIs
- CMS Hospital Compare API
- GoodRx API (medication pricing)
- Insurance company APIs
- Pharmacy benefit manager data

## Project Structure

```
melena.ai/
├── backend/                 # FastAPI backend
├── frontend/                # React frontend
├── ml/                     # Machine learning models
├── data/                   # Data processing pipelines
├── infrastructure/          # Terraform and deployment
├── docs/                   # Documentation
└── scripts/                # Utility scripts
```

## Getting Started

1. **Setup Development Environment**
   ```bash
   git clone <repository>
   cd melena.ai
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Database Setup**
   ```bash
   docker-compose up -d postgres redis
   python scripts/setup_db.py
   ```

3. **Run Development Servers**
   ```bash
   # Backend
   cd backend && uvicorn main:app --reload
   
   # Frontend
   cd frontend && npm run dev
   ```

## Illinois Hospital Targets

### Chicago Metro Area (Phase 1)
- Northwestern Memorial Hospital
- Rush University Medical Center
- University of Chicago Medical Center
- Advocate Christ Medical Center
- Loyola University Medical Center
- Swedish Covenant Hospital
- Presence Saint Joseph Hospital
- Mercy Hospital & Medical Center

### Illinois Expansion (Phase 2)
- OSF Healthcare (Peoria, Rockford)
- Carle Foundation Hospital (Urbana)
- Memorial Health System (Springfield)
- Southern Illinois Healthcare (Carbondale)

## Regulatory Compliance

- **HIPAA** - Patient data protection
- **Illinois Biometric Information Privacy Act**
- **Healthcare Cost Transparency Act (2021)**
- **Illinois Consumer Health Information Act**

## Key Features

### Fair Hospital Scoring System
- **Size-adjusted metrics** for fair comparison across hospital sizes
- **Peer group analysis** for appropriate benchmarking
- **Transparency compliance scoring** with contextual factors
- **Community impact assessment** for rural and small hospitals

### Hospital Excellence Recognition
- **Small Hospital Excellence Awards** - Recognizing outstanding transparency in small hospitals
- **Rural Healthcare Heroes** - Celebrating essential community healthcare providers
- **Community Partnership Awards** - Highlighting local healthcare collaboration
- **Transparency Champions** - Showcasing best practices across all hospital sizes

### Tiered Accountability System
- **Strict Enforcement** - For large hospital systems (200+ beds)
- **Supportive Assistance** - For medium hospitals (50-200 beds)
- **Educational Support** - For small hospitals (<50 beds)
- **Flexible compliance timelines** based on hospital resources and size

## Next Steps

1. **Data Collection Pipeline** - Build scrapers for hospital pricing files
2. **Data Normalization** - Create standardized data models
3. **ML Model Development** - Price prediction and anomaly detection
4. **UI/UX Design** - Patient-friendly interfaces
5. **Pilot Testing** - Partner with 2-3 Chicago hospitals
6. **Regulatory Review** - Legal compliance verification
7. **Hospital Excellence Program** - Launch recognition and accountability systems

