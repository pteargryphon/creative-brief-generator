import os
import requests
import json
from datetime import datetime

class CodaPublisher:
    def __init__(self):
        self.api_token = os.environ.get('CODA_API_TOKEN')
        self.base_url = 'https://coda.io/apis/v1'
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        self.template_doc_id = os.environ.get('CODA_DOC_TEMPLATE_ID', '')
        
    def create_doc(self, brief):
        """Create a new Coda doc with the brief content"""
        try:
            if not self.api_token:
                # Return mock URL if no API token
                return self._get_mock_coda_url()
            
            # Step 1: Create new doc from template or blank
            doc_id = self._create_new_doc(brief['brand_overview']['brand_name'])
            
            # Step 2: Create pages/sections
            self._setup_doc_structure(doc_id)
            
            # Step 3: Populate each section
            self._populate_brand_overview(doc_id, brief['brand_overview'])
            self._populate_competitors(doc_id, brief['competitors'])
            self._populate_meta_advertisers(doc_id, brief['meta_advertisers'])
            self._populate_reddit_problems(doc_id, brief['reddit_problems'])
            self._populate_creative_trends(doc_id, brief['creative_trends'])
            self._populate_opportunities(doc_id, brief['opportunities'])
            self._populate_ad_concepts(doc_id, brief['ad_concepts'])
            
            # Step 4: Get shareable link
            doc_url = self._get_doc_url(doc_id)
            
            return doc_url
            
        except Exception as e:
            print(f"Coda publishing error: {e}")
            return self._get_mock_coda_url()
    
    def _create_new_doc(self, brand_name):
        """Create a new Coda document"""
        try:
            # If we have a template, copy it
            if self.template_doc_id:
                url = f"{self.base_url}/docs"
                payload = {
                    'name': f"Creative Brief - {brand_name} - {datetime.now().strftime('%Y-%m-%d')}",
                    'sourceDoc': self.template_doc_id
                }
            else:
                # Create blank doc
                url = f"{self.base_url}/docs"
                payload = {
                    'name': f"Creative Brief - {brand_name} - {datetime.now().strftime('%Y-%m-%d')}",
                    'folder': 'root'
                }
            
            response = requests.post(url, json=payload, headers=self.headers)
            
            if response.status_code in [200, 201]:
                return response.json()['id']
            else:
                print(f"Error creating doc: {response.text}")
                raise Exception("Failed to create Coda doc")
                
        except Exception as e:
            print(f"Doc creation error: {e}")
            raise
    
    def _setup_doc_structure(self, doc_id):
        """Set up the document structure with pages"""
        # This would create pages/sections if starting from blank doc
        # If using template, structure already exists
        pass
    
    def _populate_brand_overview(self, doc_id, data):
        """Populate brand overview section"""
        try:
            # Find or create the brand overview table
            table_id = self._get_or_create_table(doc_id, 'Brand Overview')
            
            # Add rows with brand data
            rows = [
                ['Website', data.get('website', '')],
                ['Industry', data.get('industry', '')],
                ['Niche', data.get('niche', '')],
                ['USP', ', '.join(data.get('usp', []))],
                ['Funnel Type', data.get('funnel_type', '')],
                ['Keywords', ', '.join(data.get('keywords', []))]
            ]
            
            for row in rows:
                self._add_row_to_table(doc_id, table_id, row)
                
        except Exception as e:
            print(f"Error populating brand overview: {e}")
    
    def _populate_competitors(self, doc_id, competitors):
        """Populate competitors table"""
        try:
            table_id = self._get_or_create_table(doc_id, 'Competitors')
            
            for comp in competitors:
                row = [
                    comp.get('brand_name', ''),
                    comp.get('url', ''),
                    comp.get('usp', ''),
                    comp.get('funnel_type', ''),
                    'Yes' if comp.get('has_ads') else 'No'
                ]
                self._add_row_to_table(doc_id, table_id, row)
                
        except Exception as e:
            print(f"Error populating competitors: {e}")
    
    def _populate_meta_advertisers(self, doc_id, advertisers):
        """Populate Meta advertisers section"""
        try:
            # This would be more complex, creating cards or subsections for each advertiser
            # For now, simplified version
            for advertiser in advertisers:
                section_content = f"""
**Advertiser:** {advertiser.get('advertiser_name', '')}
**Domain:** {advertiser.get('domain', '')}
**Score:** {advertiser.get('score', 0)}
**Funnel:** {advertiser.get('funnel_url', '')}

**Top Ads:**
"""
                for ad in advertiser.get('top_ads', [])[:3]:
                    section_content += f"""
- **{ad.get('headline', '')}**
  {ad.get('body_copy', '')}
  CTA: {ad.get('cta', '')} | Running for: {ad.get('days_running', 0)} days
"""
                
                self._add_text_section(doc_id, f"Meta Advertiser - {advertiser.get('advertiser_name', '')}", section_content)
                
        except Exception as e:
            print(f"Error populating meta advertisers: {e}")
    
    def _populate_reddit_problems(self, doc_id, problems):
        """Populate Reddit problems table"""
        try:
            table_id = self._get_or_create_table(doc_id, 'Reddit Pain Points')
            
            for problem in problems:
                row = [
                    problem.get('category', ''),
                    str(problem.get('count', 0)),
                    problem.get('example_quote', '')
                ]
                self._add_row_to_table(doc_id, table_id, row)
                
        except Exception as e:
            print(f"Error populating Reddit problems: {e}")
    
    def _populate_creative_trends(self, doc_id, trends):
        """Populate creative trends section"""
        try:
            content = f"""
**Headline Patterns:**
{self._format_bullet_list(trends.get('headline_patterns', []))}

**Visual Themes:**
{self._format_bullet_list(trends.get('visual_themes', []))}

**CTA Styles:**
{self._format_bullet_list(trends.get('cta_styles', []))}

**Hook Types:**
{self._format_bullet_list(trends.get('hook_types', []))}
"""
            self._add_text_section(doc_id, 'Creative Trends', content)
            
        except Exception as e:
            print(f"Error populating trends: {e}")
    
    def _populate_opportunities(self, doc_id, opportunities):
        """Populate opportunities section"""
        try:
            content = ""
            for i, opp in enumerate(opportunities, 1):
                content += f"""
**Opportunity {i}: {opp.get('title', '')}**
Type: {opp.get('type', '').title()}
{opp.get('description', '')}

*How to implement:* {opp.get('implementation', '')}

"""
            self._add_text_section(doc_id, 'Strategic Opportunities', content)
            
        except Exception as e:
            print(f"Error populating opportunities: {e}")
    
    def _populate_ad_concepts(self, doc_id, concepts):
        """Populate ad concepts section"""
        try:
            for i, concept in enumerate(concepts, 1):
                content = f"""
**Hook Type:** {concept.get('hook_type', '').title()}
**Headline:** "{concept.get('headline', '')}"

**Body Copy:**
{concept.get('body_copy', '')}

**CTA:** {concept.get('cta', '')}

**Visual Direction:**
{concept.get('visual_direction', '')}

**Why It Works:**
{concept.get('rationale', '')}

**Pain Point Addressed:**
{concept.get('pain_point_addressed', '')}
"""
                self._add_text_section(doc_id, f"Ad Concept {i}", content)
                
        except Exception as e:
            print(f"Error populating concepts: {e}")
    
    def _get_or_create_table(self, doc_id, table_name):
        """Get existing table or create new one"""
        # Simplified - in reality would check if table exists first
        url = f"{self.base_url}/docs/{doc_id}/tables"
        payload = {'name': table_name}
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            if response.status_code in [200, 201]:
                return response.json()['id']
        except:
            pass
        
        # Return mock ID for now
        return f"table_{table_name.lower().replace(' ', '_')}"
    
    def _add_row_to_table(self, doc_id, table_id, row_data):
        """Add a row to a Coda table"""
        url = f"{self.base_url}/docs/{doc_id}/tables/{table_id}/rows"
        payload = {'cells': row_data}
        
        try:
            requests.post(url, json=payload, headers=self.headers)
        except Exception as e:
            print(f"Error adding row: {e}")
    
    def _add_text_section(self, doc_id, title, content):
        """Add a text section to the document"""
        # This would add a new section with formatted text
        # Implementation depends on Coda API capabilities
        pass
    
    def _format_bullet_list(self, items):
        """Format items as bullet list"""
        return '\n'.join([f"• {item}" for item in items])
    
    def _get_doc_url(self, doc_id):
        """Get the shareable URL for the document"""
        try:
            url = f"{self.base_url}/docs/{doc_id}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                doc_data = response.json()
                return doc_data.get('browserLink', f"https://coda.io/d/{doc_id}")
                
        except Exception as e:
            print(f"Error getting doc URL: {e}")
        
        return f"https://coda.io/d/{doc_id}"
    
    def _get_mock_coda_url(self):
        """Return mock Coda URL for testing"""
        mock_id = f"mock_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        return f"https://coda.io/d/Creative-Brief_{mock_id}"