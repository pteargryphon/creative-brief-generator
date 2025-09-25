import os
import requests
from urllib.parse import urlparse
import json

class CompetitorFinder:
    def __init__(self):
        self.serp_api_key = os.environ.get('SERP_API_KEY')
        # Can use ScraperAPI or SerpAPI for Google search results
        
    def find(self, brand_data):
        """Find top 5 competitors based on brand data"""
        try:
            competitors = []
            
            # Build search queries
            queries = self._build_search_queries(brand_data)
            
            # Search for competitors
            for query in queries[:2]:  # Limit searches to save API calls
                results = self._search_google(query, brand_data['url'])
                competitors.extend(results)
            
            # Deduplicate and limit to 5
            unique_competitors = self._deduplicate_competitors(competitors)
            
            # Analyze each competitor
            analyzed = []
            for comp in unique_competitors[:5]:
                analyzed.append(self._analyze_competitor(comp))
            
            return analyzed
            
        except Exception as e:
            print(f"Error finding competitors: {e}")
            # Return mock competitors for now
            return self._get_mock_competitors(brand_data)
    
    def _build_search_queries(self, brand_data):
        """Build search queries to find competitors"""
        queries = []
        
        # Query 1: Direct competitor search
        queries.append(f"{brand_data['niche']} brands like {brand_data['brand_name']}")
        
        # Query 2: Industry + keywords
        main_keyword = brand_data['keywords'][0] if brand_data['keywords'] else brand_data['niche']
        queries.append(f"best {main_keyword} {brand_data['industry']} companies")
        
        # Query 3: Alternative search
        queries.append(f"{brand_data['brand_name']} alternatives competitors")
        
        return queries
    
    def _search_google(self, query, exclude_url):
        """Search Google for competitors"""
        results = []
        
        # For MVP, return mock data
        # In production, use ScraperAPI or SerpAPI here
        if not self.serp_api_key:
            return self._get_mock_search_results(query)
        
        try:
            # ScraperAPI example (uncomment when API key is available)
            # url = "http://api.scraperapi.com"
            # params = {
            #     'api_key': self.serp_api_key,
            #     'url': f'https://www.google.com/search?q={query}',
            #     'render': 'false'
            # }
            # response = requests.get(url, params=params)
            # Parse response and extract competitor URLs
            pass
            
        except Exception as e:
            print(f"Search error: {e}")
            
        return results
    
    def _get_mock_search_results(self, query):
        """Return mock search results for testing"""
        # This would be replaced with actual search results
        mock_results = [
            {
                'url': 'https://competitor1.com',
                'title': 'Leading Brand in Space',
                'description': 'Top competitor offering similar products'
            },
            {
                'url': 'https://competitor2.com',
                'title': 'Alternative Solution Provider',
                'description': 'Another major player in the industry'
            }
        ]
        return mock_results
    
    def _deduplicate_competitors(self, competitors):
        """Remove duplicate competitors by domain"""
        seen = set()
        unique = []
        
        for comp in competitors:
            domain = urlparse(comp['url']).netloc
            if domain not in seen:
                seen.add(domain)
                unique.append(comp)
        
        return unique
    
    def _analyze_competitor(self, competitor):
        """Analyze a competitor website"""
        return {
            'brand_name': competitor.get('title', 'Unknown'),
            'url': competitor['url'],
            'usp': competitor.get('description', 'To be analyzed'),
            'funnel_type': 'Unknown',  # Would analyze in production
            'has_ads': True  # Would check Meta ads library
        }
    
    def _get_mock_competitors(self, brand_data):
        """Return mock competitors for testing"""
        # This provides sample data structure
        industry = brand_data.get('industry', 'general')
        niche = brand_data.get('niche', 'products')
        
        return [
            {
                'brand_name': f'Premium {niche.title()} Co',
                'url': 'https://example-competitor1.com',
                'usp': f'Leading provider of {niche} solutions with focus on quality',
                'funnel_type': 'lead_magnet',
                'has_ads': True
            },
            {
                'brand_name': f'{industry.title()} Direct',
                'url': 'https://example-competitor2.com',
                'usp': f'Direct-to-consumer {industry} brand with competitive pricing',
                'funnel_type': 'direct_purchase',
                'has_ads': True
            },
            {
                'brand_name': f'Quick {niche.title()}',
                'url': 'https://example-competitor3.com',
                'usp': f'Fast and affordable {niche} services',
                'funnel_type': 'quiz',
                'has_ads': False
            },
            {
                'brand_name': f'{niche.title()} Pro',
                'url': 'https://example-competitor4.com',
                'usp': f'Professional-grade {niche} for serious users',
                'funnel_type': 'free_trial',
                'has_ads': True
            },
            {
                'brand_name': f'The {niche.title()} Store',
                'url': 'https://example-competitor5.com',
                'usp': f'One-stop shop for all {niche} needs',
                'funnel_type': 'direct_purchase',
                'has_ads': True
            }
        ]