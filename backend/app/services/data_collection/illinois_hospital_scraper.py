import asyncio
import aiohttp
import pandas as pd
import structlog
from typing import List, Dict, Optional
from datetime import datetime
import re
from urllib.parse import urljoin, urlparse
import os

from app.core.config import settings
from app.models.hospital import Hospital, HospitalProcedure
from app.core.database import SessionLocal

logger = structlog.get_logger()

class IllinoisHospitalScraper:
    """Scraper for Illinois hospital pricing transparency data"""
    
    def __init__(self):
        self.session = None
        self.hospitals = settings.CHICAGO_HOSPITALS
        self.base_urls = {
            "northwestern": "https://www.nm.org",
            "rush": "https://www.rush.edu",
            "uchicago": "https://www.uchicagomedicine.org",
            "advocate": "https://www.advocatehealth.com",
            "loyola": "https://www.loyolamedicine.org",
            "swedish": "https://www.swedishcovenant.org",
            "presence": "https://presencehealth.org",
            "mercy": "https://www.mercy-chicago.org"
        }
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def scrape_all_hospitals(self) -> Dict[str, List[Dict]]:
        """Scrape pricing data from all target hospitals"""
        results = {}
        
        for hospital_name in self.hospitals:
            try:
                logger.info(f"Scraping data for {hospital_name}")
                hospital_data = await self.scrape_hospital(hospital_name)
                if hospital_data:
                    results[hospital_name] = hospital_data
                    logger.info(f"Successfully scraped {len(hospital_data)} procedures from {hospital_name}")
                else:
                    logger.warning(f"No data found for {hospital_name}")
                    
            except Exception as e:
                logger.error(f"Error scraping {hospital_name}: {e}")
                continue
                
        return results
    
    async def scrape_hospital(self, hospital_name: str) -> Optional[List[Dict]]:
        """Scrape pricing data from a specific hospital"""
        hospital_key = self._get_hospital_key(hospital_name)
        
        if not hospital_key or hospital_key not in self.base_urls:
            logger.warning(f"Unknown hospital: {hospital_name}")
            return None
            
        base_url = self.base_urls[hospital_key]
        
        try:
            # Find pricing transparency page
            transparency_url = await self._find_transparency_page(base_url, hospital_name)
            if not transparency_url:
                logger.warning(f"Could not find transparency page for {hospital_name}")
                return None
            
            # Scrape pricing data
            pricing_data = await self._scrape_pricing_data(transparency_url, hospital_name)
            return pricing_data
            
        except Exception as e:
            logger.error(f"Error scraping {hospital_name}: {e}")
            return None
    
    async def _find_transparency_page(self, base_url: str, hospital_name: str) -> Optional[str]:
        """Find the pricing transparency page for a hospital"""
        try:
            async with self.session.get(base_url) as response:
                if response.status != 200:
                    return None
                    
                html = await response.text()
                
                # Look for common transparency page patterns
                transparency_patterns = [
                    r'href=["\']([^"\']*[pP]rice[^"\']*)["\']',
                    r'href=["\']([^"\']*[tT]ransparency[^"\']*)["\']',
                    r'href=["\']([^"\']*[cC]ost[^"\']*)["\']',
                    r'href=["\']([^"\']*[pP]ricing[^"\']*)["\']'
                ]
                
                for pattern in transparency_patterns:
                    matches = re.findall(pattern, html, re.IGNORECASE)
                    for match in matches:
                        full_url = urljoin(base_url, match)
                        if await self._is_transparency_page(full_url):
                            return full_url
                            
                # Try common transparency URLs
                common_paths = [
                    "/price-transparency",
                    "/pricing",
                    "/cost-estimator",
                    "/transparency",
                    "/financial-assistance/pricing"
                ]
                
                for path in common_paths:
                    test_url = urljoin(base_url, path)
                    if await self._is_transparency_page(test_url):
                        return test_url
                        
        except Exception as e:
            logger.error(f"Error finding transparency page for {hospital_name}: {e}")
            
        return None
    
    async def _is_transparency_page(self, url: str) -> bool:
        """Check if a URL is a pricing transparency page"""
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    return False
                    
                html = await response.text().lower()
                
                # Look for transparency indicators
                transparency_indicators = [
                    "price transparency",
                    "standard charges",
                    "machine readable",
                    "cms requirements",
                    "hospital price transparency",
                    "cost estimator"
                ]
                
                return any(indicator in html for indicator in transparency_indicators)
                
        except Exception:
            return False
    
    async def _scrape_pricing_data(self, transparency_url: str, hospital_name: str) -> List[Dict]:
        """Scrape pricing data from a transparency page"""
        try:
            async with self.session.get(transparency_url) as response:
                if response.status != 200:
                    return []
                    
                html = await response.text()
                
                # Look for downloadable files
                file_links = self._extract_file_links(html, transparency_url)
                
                pricing_data = []
                
                for file_url in file_links:
                    try:
                        file_data = await self._download_and_parse_file(file_url, hospital_name)
                        if file_data:
                            pricing_data.extend(file_data)
                    except Exception as e:
                        logger.error(f"Error processing file {file_url}: {e}")
                        continue
                
                return pricing_data
                
        except Exception as e:
            logger.error(f"Error scraping pricing data from {transparency_url}: {e}")
            return []
    
    def _extract_file_links(self, html: str, base_url: str) -> List[str]:
        """Extract links to pricing data files"""
        file_patterns = [
            r'href=["\']([^"\']*\.csv)["\']',
            r'href=["\']([^"\']*\.xlsx?)["\']',
            r'href=["\']([^"\']*\.json)["\']',
            r'href=["\']([^"\']*[dD]ownload[^"\']*)["\']'
        ]
        
        file_links = []
        for pattern in file_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                full_url = urljoin(base_url, match)
                if self._is_pricing_file(full_url):
                    file_links.append(full_url)
        
        return file_links
    
    def _is_pricing_file(self, url: str) -> bool:
        """Check if a URL points to a pricing data file"""
        filename = urlparse(url).path.lower()
        pricing_indicators = [
            "price", "pricing", "charges", "cost", "transparency",
            "standard", "machine", "readable", "cms"
        ]
        
        return any(indicator in filename for indicator in pricing_indicators)
    
    async def _download_and_parse_file(self, file_url: str, hospital_name: str) -> List[Dict]:
        """Download and parse a pricing data file"""
        try:
            async with self.session.get(file_url) as response:
                if response.status != 200:
                    return []
                
                content = await response.read()
                file_extension = self._get_file_extension(file_url)
                
                if file_extension == ".csv":
                    return self._parse_csv_file(content, hospital_name)
                elif file_extension in [".xlsx", ".xls"]:
                    return self._parse_excel_file(content, hospital_name)
                elif file_extension == ".json":
                    return self._parse_json_file(content, hospital_name)
                else:
                    logger.warning(f"Unsupported file type: {file_extension}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error downloading file {file_url}: {e}")
            return []
    
    def _get_file_extension(self, url: str) -> str:
        """Get file extension from URL"""
        path = urlparse(url).path
        return os.path.splitext(path)[1].lower()
    
    def _parse_csv_file(self, content: bytes, hospital_name: str) -> List[Dict]:
        """Parse CSV pricing data"""
        try:
            df = pd.read_csv(pd.io.common.BytesIO(content))
            return self._standardize_dataframe(df, hospital_name)
        except Exception as e:
            logger.error(f"Error parsing CSV file: {e}")
            return []
    
    def _parse_excel_file(self, content: bytes, hospital_name: str) -> List[Dict]:
        """Parse Excel pricing data"""
        try:
            df = pd.read_excel(pd.io.common.BytesIO(content))
            return self._standardize_dataframe(df, hospital_name)
        except Exception as e:
            logger.error(f"Error parsing Excel file: {e}")
            return []
    
    def _parse_json_file(self, content: bytes, hospital_name: str) -> List[Dict]:
        """Parse JSON pricing data"""
        try:
            import json
            data = json.loads(content.decode('utf-8'))
            # Convert JSON to DataFrame for standardization
            df = pd.json_normalize(data)
            return self._standardize_dataframe(df, hospital_name)
        except Exception as e:
            logger.error(f"Error parsing JSON file: {e}")
            return []
    
    def _standardize_dataframe(self, df: pd.DataFrame, hospital_name: str) -> List[Dict]:
        """Standardize pricing data from various formats"""
        standardized_data = []
        
        # Common column name mappings
        column_mappings = {
            'cpt_code': ['cpt', 'cpt_code', 'procedure_code', 'code'],
            'procedure_name': ['procedure', 'description', 'service', 'procedure_name'],
            'cash_price': ['cash_price', 'self_pay', 'uninsured', 'gross_charge'],
            'negotiated_rate': ['negotiated_rate', 'insurance_rate', 'allowed_amount'],
            'medicare_rate': ['medicare', 'medicare_rate', 'cms_rate'],
            'medicaid_rate': ['medicaid', 'medicaid_rate']
        }
        
        # Find actual column names
        actual_columns = {}
        for standard_name, possible_names in column_mappings.items():
            for col in df.columns:
                if any(name.lower() in col.lower() for name in possible_names):
                    actual_columns[standard_name] = col
                    break
        
        # Process each row
        for _, row in df.iterrows():
            try:
                procedure_data = {
                    'hospital_name': hospital_name,
                    'cpt_code': str(row.get(actual_columns.get('cpt_code', ''), '')),
                    'procedure_name': str(row.get(actual_columns.get('procedure_name', ''), '')),
                    'cash_price': self._extract_price(row.get(actual_columns.get('cash_price', ''), '')),
                    'negotiated_rate': self._extract_price(row.get(actual_columns.get('negotiated_rate', ''), '')),
                    'medicare_rate': self._extract_price(row.get(actual_columns.get('medicare_rate', ''), '')),
                    'medicaid_rate': self._extract_price(row.get(actual_columns.get('medicaid_rate', ''), '')),
                    'source_file': hospital_name,
                    'last_updated': datetime.now()
                }
                
                # Only add if we have meaningful data
                if procedure_data['procedure_name'] and procedure_data['cpt_code']:
                    standardized_data.append(procedure_data)
                    
            except Exception as e:
                logger.error(f"Error processing row: {e}")
                continue
        
        return standardized_data
    
    def _extract_price(self, price_value) -> Optional[float]:
        """Extract numeric price from various formats"""
        if pd.isna(price_value) or price_value == '':
            return None
            
        try:
            # Remove common non-numeric characters
            price_str = str(price_value).replace('$', '').replace(',', '').strip()
            
            # Extract first number found
            price_match = re.search(r'[\d,]+\.?\d*', price_str)
            if price_match:
                return float(price_match.group().replace(',', ''))
                
        except Exception:
            pass
            
        return None
    
    def _get_hospital_key(self, hospital_name: str) -> Optional[str]:
        """Get hospital key from full name"""
        hospital_name_lower = hospital_name.lower()
        
        if 'northwestern' in hospital_name_lower:
            return 'northwestern'
        elif 'rush' in hospital_name_lower:
            return 'rush'
        elif 'chicago' in hospital_name_lower and 'university' in hospital_name_lower:
            return 'uchicago'
        elif 'advocate' in hospital_name_lower:
            return 'advocate'
        elif 'loyola' in hospital_name_lower:
            return 'loyola'
        elif 'swedish' in hospital_name_lower:
            return 'swedish'
        elif 'presence' in hospital_name_lower:
            return 'presence'
        elif 'mercy' in hospital_name_lower:
            return 'mercy'
        
        return None

async def main():
    """Main function to run the scraper"""
    async with IllinoisHospitalScraper() as scraper:
        results = await scraper.scrape_all_hospitals()
        
        # Save results to database
        db = SessionLocal()
        try:
            for hospital_name, procedures in results.items():
                logger.info(f"Processing {len(procedures)} procedures for {hospital_name}")
                
                # Here you would save to database
                # For now, just log the results
                for procedure in procedures[:5]:  # Log first 5 procedures
                    logger.info(f"Procedure: {procedure['procedure_name']}, Price: ${procedure['cash_price']}")
                    
        finally:
            db.close()

if __name__ == "__main__":
    asyncio.run(main())
