#!/usr/bin/env python3
"""Test the competitor finder to ensure it returns actual companies, not articles"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.competitor_finder import CompetitorFinder

def test_competitor_finder():
    """Test competitor finder with sample brand data"""

    # Test data for Nike
    brand_data = {
        'brand_name': 'Nike',
        'url': 'https://www.nike.com',
        'industry': 'athletic apparel',
        'niche': 'sports footwear and clothing',
        'usp': ['Just Do It', 'Innovation in athletic performance', 'Professional athlete endorsements'],
        'keywords': ['running shoes', 'athletic wear', 'sports equipment', 'sneakers', 'workout gear']
    }

    print("Testing Competitor Finder for Nike")
    print("=" * 50)

    # Initialize and test
    finder = CompetitorFinder()
    competitors = finder.find(brand_data)

    print(f"\nFound {len(competitors)} competitors:\n")

    for i, comp in enumerate(competitors, 1):
        print(f"{i}. {comp['brand_name']}")
        print(f"   URL: {comp['url']}")
        print(f"   USP: {comp['usp'][:100]}...")
        print()

    # Verify we're getting actual companies, not articles
    article_domains = ['medium.com', 'forbes.com', 'techcrunch.com', 'wikipedia.org']
    for comp in competitors:
        url = comp['url'].lower()
        if any(domain in url for domain in article_domains):
            print(f"⚠️ WARNING: Found article URL instead of company: {comp['url']}")

    print("\nTest complete!")
    return competitors

if __name__ == "__main__":
    test_competitor_finder()