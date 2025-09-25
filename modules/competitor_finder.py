import os
import requests
from urllib.parse import urlparse, quote
import json
from bs4 import BeautifulSoup

class CompetitorFinder:
    def __init__(self):
        # We'll use DuckDuckGo (free, no API key needed!)
        self.search_method = os.environ.get('SEARCH_METHOD', 'duckduckgo')
        
    def find(self, brand_data):
        """Find top 5 competitors based on brand data"""
        try:
            competitors = []
            
            # Build search queries
            queries = self._build_search_queries(brand_data)
            
            # Search for competitors
            for query in queries[:2]:  # Limit searches to save time
                results = self._search_web(query, brand_data['url'])
                competitors.extend(results)
            
            # Deduplicate and limit to 5
            unique_competitors = self._deduplicate_competitors(competitors)
            
            # Analyze each competitor (basic analysis)
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
    
    def _search_web(self, query, exclude_url):
        """Search the web using free search APIs"""
        if self.search_method == 'duckduckgo':
            return self._search_duckduckgo(query, exclude_url)
        else:
            return self._get_mock_search_results(query)
    
    def _search_duckduckgo(self, query, exclude_url):
        """Use DuckDuckGo instant answer API (free, no key needed!)"""
        results = []
        
        try:
            # DuckDuckGo HTML search (since their API is limited)
            # We'll scrape the HTML results page
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # Use DuckDuckGo HTML search
            search_url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
            response = requests.get(search_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find search results
                for result in soup.select('.result__body')[:10]:  # Top 10 results
                    try:
                        # Get URL
                        link_elem = result.select_one('.result__url')
                        if not link_elem:
                            continue
                        
                        url = link_elem.get_text().strip()
                        if not url.startswith('http'):
                            url = 'https://' + url
                        
                        # Skip if it's the brand we're analyzing
                        if exclude_url and exclude_url in url:
                            continue
                        
                        # Get title and description
                        title_elem = result.select_one('.result__title')
                        desc_elem = result.select_one('.result__snippet')
                        
                        title = title_elem.get_text().strip() if title_elem else ''
                        description = desc_elem.get_text().strip() if desc_elem else ''
                        
                        results.append({
                            'url': url,
                            'title': title,
                            'description': description
                        })
                        
                    except Exception as e:
                        continue
                
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
            # Fallback to mock data
            return self._get_mock_search_results(query)
        
        return results[:5]  # Return top 5
    
    def _get_mock_search_results(self, query):
        """Return mock search results for testing"""
        # This would be replaced with actual search results
        mock_results = [
            {
                'url': 'https://competitor1.com',
                'title': 'Leading Brand in Space',
                'description': 'Top competitor offering similar products with focus on quality and innovation'
            },
            {
                'url': 'https://competitor2.com',
                'title': 'Alternative Solution Provider',
                'description': 'Another major player in the industry known for customer service'
            },
            {
                'url': 'https://competitor3.com',
                'title': 'Premium Option',
                'description': 'High-end solution for discerning customers'
            }
        ]
        return mock_results
    
    def _deduplicate_competitors(self, competitors):
        """Remove duplicate competitors by domain"""
        seen = set()
        unique = []
        
        for comp in competitors:
            try:
                domain = urlparse(comp['url']).netloc
                if domain and domain not in seen:
                    seen.add(domain)
                    unique.append(comp)
            except:
                continue
        
        return unique
    
    def _analyze_competitor(self, competitor):
        """Analyze a competitor website (basic analysis from search results)"""
        # In a full implementation, you could scrape their site
        # For now, we'll use the search result data
        return {
            'brand_name': competitor.get('title', 'Unknown').split(' - ')[0].split(' | ')[0],
            'url': competitor['url'],
            'usp': competitor.get('description', 'To be analyzed'),
            'funnel_type': 'Unknown',  # Would need to analyze their site
            'has_ads': True  # Assume they have ads (would check Meta library in production)
        }
    
    def _get_mock_competitors(self, brand_data):
        """Return mock competitors for testing"""
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