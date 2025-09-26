import os
import requests
import json
from datetime import datetime, timedelta

class ForeplayClient:
    def __init__(self):
        self.api_key = os.environ.get('FOREPLAY_API_KEY')
        self.base_url = 'https://public.api.foreplay.co'  # Correct Foreplay API URL
        self.headers = {
            'Authorization': self.api_key,  # No 'Bearer' prefix needed
            'Content-Type': 'application/json'
        }
        # Debug: Check if API key is loaded
        if self.api_key:
            print(f"Foreplay: API key loaded (length: {len(self.api_key)})")
        else:
            print("Foreplay: No API key found in environment")

    def get_top_advertisers(self, keywords, competitors):
        """Get top 3 Meta advertisers in the niche"""
        try:
            if not self.api_key:
                print("Foreplay: No API key found, using mock data")
                return self._get_mock_advertisers(keywords)

            print(f"Foreplay: API key found, fetching real ads")
            print(f"Foreplay: Keywords: {keywords[:3]}")

            all_ads = []

            # Search ads by keywords
            for keyword in keywords[:2]:  # Limit to save API credits
                ads = self._search_ads_by_keyword(keyword)
                all_ads.extend(ads)

            # Search by competitor domains if we have them
            for comp in competitors[:1]:  # Check top competitor
                domain = self._extract_domain(comp.get('url', ''))
                if domain:
                    brands = self._search_brands_by_domain(domain)
                    # Convert brands to ad format
                    for brand in brands:
                        all_ads.extend(self._get_brand_ads(brand))

            # Process and rank the ads
            return self._process_ads_to_advertisers(all_ads)

        except Exception as e:
            print(f"Foreplay API error: {e}")
            print(f"Foreplay: Falling back to mock data due to error")
            return self._get_mock_advertisers(keywords)

    def _search_ads_by_keyword(self, keyword):
        """Search ads by keyword via Foreplay API"""
        try:
            url = f"{self.base_url}/api/discovery/ads"
            params = {
                'query': keyword,
                'publisher_platform': 'facebook',  # Focus on Meta ads
                'live': 'true',  # Only get currently running ads
                # Remove display_format - let API return all formats
                'limit': 10,
                'order': 'newest'
            }

            print(f"Foreplay: Searching ads for keyword '{keyword}'")
            response = requests.get(url, params=params, headers=self.headers, timeout=10)

            print(f"Foreplay: Response status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                ads = data.get('data', [])
                print(f"Foreplay: Found {len(ads)} ads for '{keyword}'")
                return ads
            else:
                print(f"Foreplay: API error: {response.status_code} - {response.text[:200]}")

        except Exception as e:
            print(f"Foreplay: Search error for '{keyword}': {e}")

        return []

    def _search_brands_by_domain(self, domain):
        """Search brands by domain via Foreplay API"""
        try:
            url = f"{self.base_url}/api/brand/getBrandsByDomain"
            params = {
                'domain': domain,
                'limit': 5
            }

            print(f"Foreplay: Searching brands for domain '{domain}'")
            response = requests.get(url, params=params, headers=self.headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                brands = data.get('data', [])
                print(f"Foreplay: Found {len(brands)} brands for domain '{domain}'")
                return brands
            else:
                print(f"Foreplay: Domain search error: {response.status_code}")

        except Exception as e:
            print(f"Foreplay: Domain search error: {e}")

        return []

    def _get_brand_ads(self, brand):
        """Get ads for a specific brand"""
        # Extract brand info and return as ad-like structure
        # In reality, you might need another API call to get ads for this brand
        return [{
            'advertiser_name': brand.get('name', 'Unknown'),
            'advertiser_domain': brand.get('domain', ''),
            'ad_count': brand.get('ad_count', 0)
        }]

    def _process_ads_to_advertisers(self, all_ads):
        """Process raw ads into advertiser format with top ads"""
        if not all_ads:
            print("Foreplay: No ads found, using mock data")
            return self._get_mock_advertisers(['marketing'])

        # Group ads by advertiser
        advertisers_map = {}

        for ad in all_ads:
            # Extract advertiser info from ad
            advertiser_name = ad.get('advertiser_name') or ad.get('page_name') or 'Unknown Advertiser'

            if advertiser_name not in advertisers_map:
                advertisers_map[advertiser_name] = {
                    'advertiser_name': advertiser_name,
                    'domain': ad.get('advertiser_domain', ''),
                    'score': 0,
                    'top_ads': [],
                    'funnel_url': ad.get('link_url', ''),
                    'has_lead_magnet': False
                }

            # Add this ad to the advertiser's collection
            ad_data = {
                'ad_id': ad.get('id', ''),
                'headline': ad.get('ad_creative_bodies', [''])[0] if ad.get('ad_creative_bodies') else '',
                'body': ad.get('ad_creative_link_descriptions', [''])[0] if ad.get('ad_creative_link_descriptions') else '',
                'cta': ad.get('cta_type', 'Learn More'),
                'days_running': ad.get('days_running', 0),
                'image_url': ad.get('asset_url', ''),
                'link': ad.get('link_url', '')
            }

            advertisers_map[advertiser_name]['top_ads'].append(ad_data)
            advertisers_map[advertiser_name]['score'] += 10  # Increment score per ad

        # Convert to list and sort by score
        advertisers = list(advertisers_map.values())
        advertisers.sort(key=lambda x: x['score'], reverse=True)

        # Limit top ads per advertiser and return top 3 advertisers
        for advertiser in advertisers:
            advertiser['top_ads'] = advertiser['top_ads'][:3]

        return advertisers[:3]

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