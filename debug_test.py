#!/usr/bin/env python3
"""
Debug test script to check each component individually
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_brand_analyzer():
    """Test brand analyzer with GleeFull"""
    print("\n" + "="*60)
    print("TESTING BRAND ANALYZER")
    print("="*60)
    
    from modules.brand_analyzer import BrandAnalyzer
    analyzer = BrandAnalyzer()
    
    result = analyzer.analyze("https://gleefullsupps.com/")
    
    print(f"Brand Name: {result.get('brand_name', 'ERROR')}")
    print(f"Industry: {result.get('industry', 'ERROR')}")
    print(f"Niche: {result.get('niche', 'ERROR')}")
    print(f"USP: {result.get('usp', 'ERROR')}")
    print(f"Funnel Type: {result.get('funnel_type', 'ERROR')}")
    
    return result

def test_foreplay():
    """Test Foreplay API"""
    print("\n" + "="*60)
    print("TESTING FOREPLAY API")
    print("="*60)
    
    from modules.foreplay_client import ForeplayClient
    client = ForeplayClient()
    
    # Test with keywords
    result = client.get_advertisers(['supplements', 'health', 'wellness'])
    
    print(f"Found {len(result)} advertisers")
    for adv in result[:2]:
        print(f"- {adv.get('advertiser_name', 'ERROR')}: {adv.get('score', 0)} score")
        print(f"  Ads: {len(adv.get('top_ads', []))}")
    
    return result

def test_reddit():
    """Test Reddit mining"""
    print("\n" + "="*60)
    print("TESTING REDDIT MINING")
    print("="*60)
    
    from modules.reddit_miner import RedditMiner
    miner = RedditMiner()
    
    # Test with keywords
    result = miner.mine_problems(['supplements', 'vitamins'], 'gleefullsupps')
    
    print(f"Found {len(result)} problem categories")
    for problem in result[:3]:
        print(f"- {problem.get('category', 'ERROR')} ({problem.get('count', 0)} mentions)")
        print(f"  Example: {problem.get('example_quote', 'ERROR')[:100]}...")
    
    return result

def test_openai():
    """Test OpenAI API directly"""
    print("\n" + "="*60)
    print("TESTING OPENAI API")
    print("="*60)
    
    try:
        import openai
        openai.api_key = os.environ.get('OPENAI_API_KEY')
        
        if not openai.api_key or openai.api_key == 'sk-...':
            print("ERROR: No valid OpenAI API key")
            return None
            
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'OpenAI is working'"}],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        print(f"OpenAI Response: {result}")
        return result
        
    except Exception as e:
        print(f"ERROR: {e}")
        return None

def main():
    print("\n" + "="*60)
    print("CREATIVE BRIEF GENERATOR - DEBUG TEST")
    print("="*60)
    
    # Show environment status
    print("\nEnvironment Variables:")
    env_vars = {
        'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY', 'NOT SET'),
        'FOREPLAY_API_KEY': os.environ.get('FOREPLAY_API_KEY', 'NOT SET'),
        'APIFY_API_TOKEN': os.environ.get('APIFY_API_TOKEN', 'NOT SET'),
        'CODA_API_TOKEN': os.environ.get('CODA_API_TOKEN', 'NOT SET'),
    }
    
    for key, value in env_vars.items():
        if value == 'NOT SET':
            print(f"❌ {key}: NOT SET")
        elif value in ['sk-...', 'your_foreplay_api_key_here', 'your_apify_token_here']:
            print(f"⚠️  {key}: Placeholder value")
        else:
            masked = value[:8] + '...' if len(value) > 8 else '***'
            print(f"✅ {key}: {masked}")
    
    # Test each component
    print("\nRunning component tests...")
    
    # Test OpenAI first (most critical)
    openai_result = test_openai()
    if not openai_result:
        print("\n⚠️  OpenAI not working - brand analysis will fail!")
    
    # Test brand analyzer
    brand_result = test_brand_analyzer()
    
    # Test Foreplay
    foreplay_result = test_foreplay()
    
    # Test Reddit
    reddit_result = test_reddit()
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    if brand_result.get('industry') == 'Unknown':
        print("❌ Brand Analyzer: Failed (check OpenAI API key)")
    else:
        print("✅ Brand Analyzer: Working")
    
    if not foreplay_result:
        print("❌ Foreplay: Failed (check API key)")
    else:
        print("✅ Foreplay: Working")
    
    if not reddit_result:
        print("❌ Reddit: Failed (check Apify token)")
    else:
        print("✅ Reddit: Working")

if __name__ == "__main__":
    main()