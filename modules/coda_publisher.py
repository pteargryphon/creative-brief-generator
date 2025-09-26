import os
import requests
import json
from datetime import datetime
from .error_logger import error_logger

class CodaPublisher:
    def __init__(self):
        self.api_token = os.environ.get('CODA_API_TOKEN')
        self.base_url = 'https://coda.io/apis/v1'
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        self.doc_id = os.environ.get('CODA_DOC_ID', 'TeddWcsh5U')  # Doc containing the table
        self.table_id = os.environ.get('CODA_TABLE_ID', 'grid-XSXEqW-PnP')  # The specific table ID
        
    def create_doc(self, brief):
        """Add a new row to the Coda table with the brief content"""
        try:
            if not self.api_token:
                print("Missing Coda API token")
                return self._get_mock_coda_url()
            
            if not self.doc_id or not self.table_id:
                print(f"Missing Coda config - Doc ID: {self.doc_id}, Table ID: {self.table_id}")
                return self._get_mock_coda_url()
            
            # Format the brief data for the table row
            row_data = self._format_brief_for_table(brief)
            
            # Add row to table
            success = self._add_table_row(row_data)
            
            if success:
                # Return link to the doc/table
                return f"https://coda.io/d/_d{self.doc_id}"
            else:
                return self._get_mock_coda_url()
            
        except Exception as e:
            print(f"Coda publishing error: {e}")
            return self._get_mock_coda_url()
    
    def _format_brief_for_table(self, brief):
        """Format the brief data to match table columns"""
        brand = brief.get('brand_overview', {})
        
        # Format competitors list
        competitors_text = '\n'.join([
            f"• {comp.get('brand_name', '')}: {comp.get('url', '')}"
            for comp in brief.get('competitors', [])[:5]
        ])
        
        # Format Meta advertisers
        meta_text = ''
        for advertiser in brief.get('meta_advertisers', [])[:3]:
            meta_text += f"\n{advertiser.get('advertiser_name', '')} ({advertiser.get('score', 0)} score)\n"
            for ad in advertiser.get('top_ads', [])[:2]:
                meta_text += f"  - {ad.get('headline', '')}\n"
        
        # Format Reddit pain points
        reddit_text = '\n'.join([
            f"• {problem.get('category', '')} ({problem.get('count', 0)}): {problem.get('example_quote', '')[:100]}..."
            for problem in brief.get('reddit_problems', [])[:5]
        ])
        
        # Format creative trends
        trends = brief.get('creative_trends', {})
        trends_text = f"Headlines: {', '.join(trends.get('headline_patterns', [])[:3])}\n"
        trends_text += f"CTAs: {', '.join(trends.get('cta_styles', [])[:3])}"
        
        # Format opportunities
        opportunities_text = '\n'.join([
            f"{i+1}. {opp.get('title', '')}: {opp.get('description', '')[:100]}..."
            for i, opp in enumerate(brief.get('opportunities', [])[:3])
        ])
        
        # Format ad concepts
        concepts_text = ''
        for i, concept in enumerate(brief.get('ad_concepts', [])[:3], 1):
            concepts_text += f"\n{i}. {concept.get('headline', '')}\n"
            concepts_text += f"   Hook: {concept.get('hook_type', '')}\n"
            concepts_text += f"   CTA: {concept.get('cta', '')}\n"
        
        # Create the row data matching your table columns
        row_data = {
            'Brand Name': brand.get('brand_name', ''),
            'Website': brand.get('website', ''),
            'Industry': brand.get('industry', ''),
            'Niche': brand.get('niche', ''),
            'USP': ', '.join(brand.get('usp', [])),
            'Funnel Type': brand.get('funnel_type', ''),
            'Keywords': ', '.join(brand.get('keywords', [])),
            'Top Competitors': competitors_text,
            'Meta Advertisers': meta_text,
            'Reddit Pain Points': reddit_text,
            'Creative Trends': trends_text,
            'Opportunities': opportunities_text,
            'Ad Concepts': concepts_text,
            'Generated Date': datetime.now().strftime('%Y-%m-%d'),
            'Status': 'Complete',
            'Debug_Errors': error_logger.get_error_summary(),
            'API_Status': error_logger.check_api_status()
        }
        
        return row_data
    
    def _add_table_row(self, row_data):
        """Add a row to the Coda table"""
        try:
            # Coda API endpoint for adding rows
            url = f"{self.base_url}/docs/{self.doc_id}/tables/{self.table_id}/rows"
            
            # Format for Coda API - cells array with column/value pairs
            cells = []
            for column, value in row_data.items():
                cells.append({
                    'column': column,
                    'value': value
                })
            
            payload = {
                'rows': [{
                    'cells': cells
                }]
            }
            
            response = requests.post(url, json=payload, headers=self.headers)
            
            if response.status_code in [200, 201, 202]:
                print("Successfully added row to Coda table")
                return True
            else:
                print(f"Error adding row: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Error adding row to table: {e}")
            return False
    
    def _get_mock_coda_url(self):
        """Return mock Coda URL for testing"""
        mock_id = f"mock_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        return f"https://coda.io/d/Creative-Brief_{mock_id}"