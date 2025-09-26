"""
Helper module to properly initialize OpenAI client
Handles proxy and environment issues
"""
import os
from openai import OpenAI

def get_openai_client():
    """
    Get a properly configured OpenAI client
    Handles proxy issues that cause 'proxies' argument errors
    """
    # Remove proxy environment variables that cause issues with OpenAI client
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy']
    saved_proxies = {}
    
    # Temporarily remove proxy variables
    for var in proxy_vars:
        if var in os.environ:
            saved_proxies[var] = os.environ.pop(var)
    
    try:
        # Initialize OpenAI client without proxy interference
        client = OpenAI(
            api_key=os.environ.get('OPENAI_API_KEY'),
            # Explicitly set to None to avoid proxy issues
            http_client=None
        )
        
        return client
    finally:
        # Restore proxy variables
        for var, value in saved_proxies.items():
            os.environ[var] = value