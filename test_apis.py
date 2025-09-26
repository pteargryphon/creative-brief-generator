#!/usr/bin/env python3
"""
Test script to verify all API connections
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openai():
    """Test OpenAI API"""
    try:
        import openai
        openai.api_key = os.environ.get('OPENAI_API_KEY')
        
        if not openai.api_key or openai.api_key == 'sk-...':
            return "❌ OpenAI: No valid API key set"
        
        # Try a simple completion
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'test'"}],
            max_tokens=10
        )
        return "✅ OpenAI: Working"
    except Exception as e:
        return f"❌ OpenAI: {str(e)[:100]}"

def test_foreplay():
    """Test Foreplay API"""
    try:
        import requests
        api_key = os.environ.get('FOREPLAY_API_KEY')
        
        if not api_key or api_key == 'your_foreplay_api_key_here':
            return "❌ Foreplay: No valid API key set"
        
        # Test API endpoint (adjust based on Foreplay docs)
        headers = {'Authorization': f'Bearer {api_key}'}
        response = requests.get('https://api.foreplay.co/v1/advertisers', headers=headers, timeout=5)
        
        if response.status_code == 401:
            return "❌ Foreplay: Invalid API key"
        elif response.status_code == 200:
            return "✅ Foreplay: Working"
        else:
            return f"❌ Foreplay: Status {response.status_code}"
    except Exception as e:
        return f"❌ Foreplay: {str(e)[:100]}"

def test_apify():
    """Test Apify API"""
    try:
        import requests
        api_token = os.environ.get('APIFY_API_TOKEN')
        
        if not api_token or api_token == 'your_apify_token_here':
            return "❌ Apify: No valid API token set"
        
        # Test API endpoint
        headers = {'Authorization': f'Bearer {api_token}'}
        response = requests.get('https://api.apify.com/v2/user/me', headers=headers, timeout=5)
        
        if response.status_code == 401:
            return "❌ Apify: Invalid API token"
        elif response.status_code == 200:
            return "✅ Apify: Working"
        else:
            return f"❌ Apify: Status {response.status_code}"
    except Exception as e:
        return f"❌ Apify: {str(e)[:100]}"

def test_coda():
    """Test Coda API"""
    try:
        import requests
        api_token = os.environ.get('CODA_API_TOKEN')
        doc_id = os.environ.get('CODA_DOC_ID', 'TeddWcsh5U')
        table_id = os.environ.get('CODA_TABLE_ID', 'grid-XSXEqW-PnP')
        
        if not api_token:
            return "❌ Coda: No API token set"
        
        # Test API endpoint
        headers = {'Authorization': f'Bearer {api_token}'}
        response = requests.get(f'https://coda.io/apis/v1/docs/{doc_id}', headers=headers, timeout=5)
        
        if response.status_code == 401:
            return "❌ Coda: Invalid API token"
        elif response.status_code == 200:
            return f"✅ Coda: Working (Doc: {doc_id}, Table: {table_id})"
        else:
            return f"❌ Coda: Status {response.status_code}"
    except Exception as e:
        return f"❌ Coda: {str(e)[:100]}"

def main():
    print("=" * 60)
    print("API CONNECTION TEST")
    print("=" * 60)
    print()
    
    # Test each API
    print(test_openai())
    print(test_foreplay())
    print(test_apify())
    print(test_coda())
    
    print()
    print("=" * 60)
    print("Environment Variables Status:")
    print("=" * 60)
    
    # Check which env vars are set
    env_vars = {
        'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY', 'NOT SET'),
        'FOREPLAY_API_KEY': os.environ.get('FOREPLAY_API_KEY', 'NOT SET'),
        'APIFY_API_TOKEN': os.environ.get('APIFY_API_TOKEN', 'NOT SET'),
        'CODA_API_TOKEN': os.environ.get('CODA_API_TOKEN', 'NOT SET'),
        'CODA_DOC_ID': os.environ.get('CODA_DOC_ID', 'NOT SET'),
        'CODA_TABLE_ID': os.environ.get('CODA_TABLE_ID', 'NOT SET'),
    }
    
    for key, value in env_vars.items():
        if value == 'NOT SET':
            print(f"❌ {key}: NOT SET")
        elif value in ['sk-...', 'your_foreplay_api_key_here', 'your_apify_token_here', 'optional_template_doc_id']:
            print(f"⚠️  {key}: Using placeholder value")
        else:
            # Mask the actual value for security
            masked = value[:8] + '...' if len(value) > 8 else value
            print(f"✅ {key}: Set ({masked})")

if __name__ == "__main__":
    main()