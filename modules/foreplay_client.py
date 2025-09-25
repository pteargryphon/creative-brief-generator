import os
import requests
import json
from datetime import datetime, timedelta

class ForeplayClient:
    def __init__(self):
        self.api_key = os.environ.get('FOREPLAY_API_KEY')
        self.base_url = 'https://api.foreplay.co/v1'  # Update with actual Foreplay API URL
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def get_top_advertisers(self, keywords, competitors):
        """Get top 3 Meta advertisers in the niche"""
        try:
            if not self.api_key:
                # Return mock data if no API key
                return self._get_mock_advertisers(keywords)
            
            advertisers = []
            
            # Search by keywords
            for keyword in keywords[:3]:  # Limit to save API calls
                results = self._search_ads_by_keyword(keyword)
                advertisers.extend(results)
            
            # Search by competitor domains
            for comp in competitors[:2]:  # Check top 2 competitors
                domain = self._extract_domain(comp['url'])
                results = self._search_ads_by_domain(domain)
                advertisers.extend(results)
            
            # Rank and select top 3
            top_advertisers = self._rank_advertisers(advertisers)
            
            # Get detailed ad info for each
            detailed = []
            for advertiser in top_advertisers[:3]:
                detailed.append(self._get_advertiser_details(advertiser))
            
            return detailed
            
        except Exception as e:
            print(f"Foreplay API error: {e}")
            return self._get_mock_advertisers(keywords)
    
    def _search_ads_by_keyword(self, keyword):
        """Search ads by keyword via Foreplay API"""
        try:
            # Foreplay API endpoint for search
            # This is a placeholder - update with actual API structure
            url = f"{self.base_url}/ads/search"
            params = {
                'keyword': keyword,
                'platform': 'facebook',
                'sort_by': 'days_running',
                'limit': 10
            }
            
            response = requests.get(url, params=params, headers=self.headers)
            
            if response.status_code == 200:
                return response.json().get('ads', [])
            
        except Exception as e:
            print(f"Search error: {e}")
        
        return []
    
    def _search_ads_by_domain(self, domain):
        """Search ads by advertiser domain"""
        try:
            # Placeholder for Foreplay API
            url = f"{self.base_url}/advertisers/search"
            params = {
                'domain': domain,
                'platform': 'facebook'
            }
            
            response = requests.get(url, params=params, headers=self.headers)
            
            if response.status_code == 200:
                return response.json().get('advertisers', [])
                
        except Exception as e:
            print(f"Domain search error: {e}")
        
        return []
    
    def _rank_advertisers(self, advertisers):
        """Rank advertisers by longevity and volume"""
        # Score based on days running and number of ads
        scored = []
        
        for advertiser in advertisers:
            score = 0
            score += advertiser.get('days_running', 0) * 2  # Weight longevity
            score += advertiser.get('ad_count', 0)
            score += advertiser.get('engagement_score', 0) * 10
            
            advertiser['score'] = score
            scored.append(advertiser)
        
        # Sort by score
        scored.sort(key=lambda x: x['score'], reverse=True)
        
        return scored
    
    def _get_advertiser_details(self, advertiser):
        """Get detailed info about an advertiser"""
        return {
            'advertiser_name': advertiser.get('name', 'Unknown'),
            'domain': advertiser.get('domain', ''),
            'score': advertiser.get('score', 0),
            'top_ads': advertiser.get('top_ads', [])[:5],  # Limit to 5 ads
            'funnel_url': advertiser.get('landing_page', ''),
            'has_lead_magnet': advertiser.get('has_lead_magnet', False)
        }
    
    def _extract_domain(self, url):
        """Extract domain from URL"""
        from urllib.parse import urlparse
        return urlparse(url).netloc.replace('www.', '')
    
    def _get_mock_advertisers(self, keywords):
        """Return mock Meta advertisers data for testing"""
        keyword = keywords[0] if keywords else 'product'
        
        return [
            {
                'advertiser_name': f'Top {keyword.title()} Brand',
                'domain': 'topbrand.com',
                'score': 950,
                'top_ads': [
                    {
                        'ad_id': '1001',
                        'headline': f'Revolutionary {keyword.title()} - 50% Off Today Only',
                        'body': f'Discover why thousands are switching to our {keyword}...',
                        'cta': 'Shop Now',
                        'days_running': 145,
                        'image_url': 'https://via.placeholder.com/1200x628',
                        'link': 'https://topbrand.com/offer'
                    },
                    {
                        'ad_id': '1002', 
                        'headline': f'The {keyword.title()} That Changed Everything',
                        'body': 'See the before and after results that shocked everyone...',
                        'cta': 'Learn More',
                        'days_running': 89,
                        'image_url': 'https://via.placeholder.com/1200x628',
                        'link': 'https://topbrand.com/testimonials'
                    },
                    {
                        'ad_id': '1003',
                        'headline': f'Why Doctors Recommend This {keyword.title()}',
                        'body': '3 reasons medical professionals choose our solution...',
                        'cta': 'Get Free Guide',
                        'days_running': 67,
                        'image_url': 'https://via.placeholder.com/1200x628',
                        'link': 'https://topbrand.com/guide'
                    }
                ],
                'funnel_url': 'https://topbrand.com/quiz',
                'has_lead_magnet': True
            },
            {
                'advertiser_name': f'Premium {keyword.title()} Co',
                'domain': 'premiumco.com',
                'score': 780,
                'top_ads': [
                    {
                        'ad_id': '2001',
                        'headline': f"This {keyword.title()} Trick Will Blow Your Mind",
                        'body': 'One simple change that makes all the difference...',
                        'cta': 'See How',
                        'days_running': 203,
                        'image_url': 'https://via.placeholder.com/1200x628',
                        'link': 'https://premiumco.com/secret'
                    },
                    {
                        'ad_id': '2002',
                        'headline': f'Get Your First {keyword.title()} Free',
                        'body': 'Limited time offer for new customers only...',
                        'cta': 'Claim Yours',
                        'days_running': 156,
                        'image_url': 'https://via.placeholder.com/1200x628',
                        'link': 'https://premiumco.com/free-trial'
                    }
                ],
                'funnel_url': 'https://premiumco.com/vsl',
                'has_lead_magnet': False
            },
            {
                'advertiser_name': f'{keyword.title()} Direct',
                'domain': 'direct.com',
                'score': 650,
                'top_ads': [
                    {
                        'ad_id': '3001',
                        'headline': f'{keyword.title()} Sale Ends Tonight',
                        'body': "Don't miss out on our biggest discount of the year...",
                        'cta': 'Shop Sale',
                        'days_running': 45,
                        'image_url': 'https://via.placeholder.com/1200x628',
                        'link': 'https://direct.com/sale'
                    },
                    {
                        'ad_id': '3002',
                        'headline': f'Compare Our {keyword.title()} to Others',
                        'body': 'See why we consistently rank #1 in quality...',
                        'cta': 'View Comparison',
                        'days_running': 112,
                        'image_url': 'https://via.placeholder.com/1200x628',
                        'link': 'https://direct.com/compare'
                    }
                ],
                'funnel_url': 'https://direct.com/shop',
                'has_lead_magnet': True
            }
        ]