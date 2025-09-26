import os
import requests
from urllib.parse import urlparse, quote
import json
from bs4 import BeautifulSoup
from .openai_helper import get_openai_client

class CompetitorFinder:
    def __init__(self):
        # We'll use DuckDuckGo (free, no API key needed!)
        self.search_method = os.environ.get('SEARCH_METHOD', 'duckduckgo')
        self.client = get_openai_client()
        
    def find(self, brand_data):
        """Find top 5 competitors based on brand data"""
        try:
            # Step 1: Search the web for competitor information
            search_results = []
            queries = self._build_search_queries(brand_data)

            for query in queries[:2]:  # Limit searches to save time
                results = self._search_web(query, brand_data['url'])
                search_results.extend(results)

            # Step 2: Use AI to analyze search results and extract actual competitor companies
            competitors = self._extract_competitors_from_search_results(brand_data, search_results)

            if competitors:
                return competitors[:5]

            # Fallback if AI extraction fails
            return self._get_mock_competitors(brand_data)

        except Exception as e:
            print(f"Error finding competitors: {e}")
            return self._get_mock_competitors(brand_data)
    
    def _build_search_queries(self, brand_data):
        """Build search queries to find competitors"""
        queries = []

        # Query 1: Direct competitor search
        queries.append(f"{brand_data['brand_name']} competitors alternatives")

        # Query 2: Industry + keywords + vs (to find comparison articles)
        main_keyword = brand_data['keywords'][0] if brand_data['keywords'] else brand_data['niche']
        queries.append(f"{brand_data['brand_name']} vs {main_keyword}")

        # Query 3: Top companies in the niche
        queries.append(f"top {brand_data['niche']} companies brands {brand_data['industry']}")

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
        # Extract the actual company name and URL from search results
        title = competitor.get('title', '')
        url = competitor.get('url', '')
        description = competitor.get('description', '')

        # Try to extract the actual company domain from the URL
        # Skip if this is an article/blog/review site
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()

        # Filter out common article/review sites
        article_sites = ['medium.com', 'forbes.com', 'techcrunch.com', 'wikipedia.org',
                        'reddit.com', 'quora.com', 'youtube.com', 'facebook.com',
                        'twitter.com', 'linkedin.com', 'instagram.com', 'pinterest.com',
                        'trustpilot.com', 'g2.com', 'capterra.com', 'producthunt.com']

        if any(site in domain for site in article_sites):
            # This is an article about competitors, try to extract company names from title/description
            return self._extract_competitor_from_article(title, description)

        # Clean up the brand name from the title
        brand_name = title.split(' - ')[0].split(' | ')[0].split(':')[0].strip()

        # Remove common suffixes
        for suffix in [' Reviews', ' Review', ' Alternative', ' Alternatives', ' Competitor', ' vs']:
            if brand_name.endswith(suffix):
                brand_name = brand_name[:-len(suffix)].strip()

        return {
            'brand_name': brand_name or parsed_url.netloc.replace('www.', '').split('.')[0].title(),
            'url': f"https://{parsed_url.netloc}" if parsed_url.scheme else url,
            'usp': description[:150] if description else 'Leading solution in the industry',
            'funnel_type': 'direct_purchase',  # Default assumption
            'has_ads': True  # Assume they have ads
        }
    
    def _extract_competitors_from_search_results(self, brand_data, search_results):
        """Use AI to analyze search results and extract actual competitor companies"""
        try:
            # Compile search results into a text format for AI analysis
            search_text = "Search results about competitors:\n\n"
            for i, result in enumerate(search_results[:10], 1):
                search_text += f"{i}. Title: {result.get('title', '')}\n"
                search_text += f"   URL: {result.get('url', '')}\n"
                search_text += f"   Description: {result.get('description', '')}\n\n"

            prompt = f"""Analyze these search results about {brand_data.get('brand_name', 'a company')}'s competitors.

Brand being analyzed:
- Name: {brand_data.get('brand_name', 'Unknown')}
- Industry: {brand_data.get('industry', 'Unknown')}
- Niche: {brand_data.get('niche', 'Unknown')}
- Website: {brand_data.get('url', '')}

Search Results:
{search_text}

Based on these search results, identify the TOP 5 ACTUAL COMPETITOR COMPANIES mentioned.
These should be real companies that compete directly with {brand_data.get('brand_name', 'this brand')}.

DO NOT include:
- The brand being analyzed ({brand_data.get('brand_name', '')})
- Article websites (Forbes, TechCrunch, etc.)
- Review sites (G2, Capterra, etc.)
- Generic descriptors

Return exactly 5 real competitor companies in JSON format:
[
  {{
    "brand_name": "Company Name",
    "url": "https://www.companywebsite.com",
    "usp": "What makes them unique/competitive",
    "why_competitor": "Why they compete with {brand_data.get('brand_name', 'this brand')}"
  }}
]

If the search results mention specific companies as competitors, include those.
For each company, provide their actual website URL if possible, otherwise use the format https://www.[companyname].com"""

            response = self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing search results to identify actual competitor companies. Extract only real company names mentioned in the search results. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=1.0,
                max_tokens=1500
            )

            result = response.choices[0].message.content
            if result.startswith('```json'):
                result = result[7:]
            if result.endswith('```'):
                result = result[:-3]

            competitors_data = json.loads(result.strip())

            # Format for our system
            formatted_competitors = []
            for comp in competitors_data[:5]:
                formatted_competitors.append({
                    'brand_name': comp.get('brand_name', 'Unknown'),
                    'url': comp.get('url', ''),
                    'usp': comp.get('usp', comp.get('why_competitor', 'Direct competitor')),
                    'funnel_type': 'direct_purchase',  # Default
                    'has_ads': True  # Assume most have ads
                })

            return formatted_competitors

        except Exception as e:
            print(f"AI extraction error: {e}")
            return None

    def _extract_competitor_from_article(self, title, description):
        """Extract competitor info when the search result is an article about competitors"""
        # Common patterns in titles like "X vs Y" or "Top 10 X alternatives"
        # Try to extract the first mentioned competitor

        # Look for "vs" pattern
        if ' vs ' in title.lower():
            parts = title.split(' vs ')
            if len(parts) > 1:
                competitor_name = parts[1].split(' ')[0].strip()
                return {
                    'brand_name': competitor_name,
                    'url': f'https://www.{competitor_name.lower().replace(" ", "")}.com',
                    'usp': 'Major competitor in the space',
                    'funnel_type': 'direct_purchase',
                    'has_ads': True
                }

        # Default fallback
        return {
            'brand_name': 'Competitor',
            'url': 'https://example.com',
            'usp': 'Alternative solution',
            'funnel_type': 'Unknown',
            'has_ads': False
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