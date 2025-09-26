import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re
import os
from openai import OpenAI
from .error_logger import error_logger

class BrandAnalyzer:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def analyze(self, url):
        """Analyze brand website and extract key information"""
        try:
            # Normalize URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Fetch homepage
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract basic info
            brand_name = self._extract_brand_name(soup, url)
            meta_description = self._extract_meta_description(soup)
            
            # Extract text content
            text_content = self._extract_text_content(soup)
            
            # Use AI to analyze the content
            analysis = self._ai_analyze(text_content, meta_description, url)
            
            # Add extracted data
            analysis['brand_name'] = brand_name
            analysis['url'] = url
            analysis['meta_description'] = meta_description
            
            return analysis
            
        except Exception as e:
            error_logger.log_error('BrandAnalyzer.analyze', e, {'url': url})
            print(f"Error analyzing brand: {e}")
            # Return minimal data on error
            return {
                'brand_name': urlparse(url).netloc,
                'url': url,
                'industry': 'Unknown',
                'niche': 'Unknown',
                'usp': ['Unable to determine'],
                'funnel_type': 'Unknown',
                'keywords': [urlparse(url).netloc.replace('.com', '')]
            }
    
    def _extract_brand_name(self, soup, url):
        """Extract brand name from website"""
        # Try og:site_name
        og_site = soup.find('meta', property='og:site_name')
        if og_site and og_site.get('content'):
            return og_site['content']
        
        # Try title tag
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
            # Return first part before separator
            for sep in [' - ', ' | ', ' — ', ' · ']:
                if sep in title:
                    return title.split(sep)[0].strip()
            return title
        
        # Fallback to domain
        domain = urlparse(url).netloc
        return domain.replace('www.', '').split('.')[0].title()
    
    def _extract_meta_description(self, soup):
        """Extract meta description"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content']
        
        og_desc = soup.find('meta', property='og:description')
        if og_desc and og_desc.get('content'):
            return og_desc['content']
        
        return ""
    
    def _extract_text_content(self, soup):
        """Extract main text content from page"""
        # Remove script and style elements
        for script in soup(['script', 'style']):
            script.decompose()
        
        # Get text from main content areas
        content_areas = []
        
        # Try to find main content areas
        for selector in ['main', 'article', '[role="main"]', '.content', '#content']:
            elements = soup.select(selector)
            if elements:
                for elem in elements[:2]:  # Limit to first 2 matches
                    content_areas.append(elem.get_text(separator=' ', strip=True))
        
        # If no specific content areas, get body text
        if not content_areas:
            body = soup.find('body')
            if body:
                content_areas.append(body.get_text(separator=' ', strip=True))
        
        # Combine and limit length
        text = ' '.join(content_areas)
        # Limit to ~3000 chars for API efficiency
        return text[:3000]
    
    def _ai_analyze(self, text_content, meta_description, url):
        """Use AI to analyze the brand"""
        prompt = f"""Analyze this brand website and extract the following information:

URL: {url}
Meta Description: {meta_description}
Website Content: {text_content[:2000]}

Please provide a JSON response with:
1. industry - The primary industry (e.g., "e-commerce", "SaaS", "healthcare", "finance")
2. niche - The specific niche within the industry (e.g., "women's health supplements", "project management software")
3. usp - Array of 3-5 unique selling propositions (what makes this brand special)
4. funnel_type - The primary conversion funnel type: "direct_purchase", "lead_magnet", "quiz", "vsl", "free_trial", "demo_request", or "other"
5. keywords - Array of 5-10 relevant keywords for finding competitors and ads

Respond with valid JSON only."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-5-mini",  # Using gpt-5-mini for cost efficiency while getting GPT-5 quality
                messages=[
                    {"role": "system", "content": "You are a marketing analyst. Respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Parse JSON response
            import json
            result = response.choices[0].message.content
            # Clean up response if needed
            if result.startswith('```json'):
                result = result[7:]
            if result.endswith('```'):
                result = result[:-3]
            
            return json.loads(result.strip())
            
        except Exception as e:
            error_logger.log_error('BrandAnalyzer._ai_analyze', e, {
                'url': url, 
                'api_key_set': bool(os.environ.get('OPENAI_API_KEY') and os.environ.get('OPENAI_API_KEY') != 'sk-...')
            })
            print(f"AI analysis error: {e}")
            # Return defaults on error
            return {
                'industry': 'Unknown',
                'niche': 'Unknown',
                'usp': ['Unable to determine USP'],
                'funnel_type': 'Unknown',
                'keywords': [urlparse(url).netloc.replace('.com', '')]
            }