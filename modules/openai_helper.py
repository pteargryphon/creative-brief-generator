"""
Helper module to properly initialize OpenAI client
Handles proxy and environment issues
"""
import os

def get_openai_client():
    """
    Get a properly configured OpenAI client
    Handles proxy issues that cause 'proxies' argument errors
    """
    # Remove ALL proxy environment variables before importing OpenAI
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 
                  'ALL_PROXY', 'all_proxy', 'NO_PROXY', 'no_proxy']
    saved_proxies = {}
    
    # Save and remove proxy variables
    for var in proxy_vars:
        if var in os.environ:
            saved_proxies[var] = os.environ[var]
            del os.environ[var]
    
    try:
        # Import OpenAI AFTER removing proxy vars to prevent initialization issues
        from openai import OpenAI
        
        # Initialize OpenAI client
        client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        
        return client
    finally:
        # Restore proxy variables
        for var, value in saved_proxies.items():
            os.environ[var] = value