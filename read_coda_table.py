#!/usr/bin/env python3
"""
Script to read the Coda table and check for errors
"""
import requests
import json
import sys

def read_coda_table(api_token):
    """Read the Coda table and display the latest row"""
    
    doc_id = "TeddWcsh5U"
    table_id = "grid-XSXEqW-PnP"
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }
    
    # Get table rows
    url = f'https://coda.io/apis/v1/docs/{doc_id}/tables/{table_id}/rows'
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('items'):
            print(f"Found {len(data['items'])} rows in the table\n")
            
            # Get the latest row (last item)
            latest_row = data['items'][-1]
            
            print("Latest row data:")
            print("="*50)
            
            # Parse and display values
            values = latest_row.get('values', {})
            for key, value in values.items():
                # Clean up the column name (remove the 'c-' prefix if present)
                clean_key = key.replace('c-', '').replace('_', ' ').title()
                
                # Check for potential errors
                error_indicators = ['error', 'Error', 'ERROR', 'null', 'None', 'undefined', '[]', '{}']
                is_error = any(indicator in str(value) for indicator in error_indicators)
                
                if is_error or not value or value == "":
                    print(f"❌ {clean_key}: {value or 'EMPTY'}")
                else:
                    # Truncate long values for display
                    display_value = str(value)[:200] + "..." if len(str(value)) > 200 else value
                    print(f"✅ {clean_key}: {display_value}")
            
            print("\n" + "="*50)
            return latest_row
        else:
            print("No rows found in the table")
            return None
            
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response: {e.response.text if e.response else 'No response'}")
        return None
    except Exception as e:
        print(f"Error reading Coda table: {e}")
        return None

if __name__ == "__main__":
    # Get API token from command line or environment
    import os
    
    api_token = None
    
    if len(sys.argv) > 1:
        api_token = sys.argv[1]
    else:
        api_token = os.environ.get('CODA_API_TOKEN')
    
    if not api_token:
        print("Please provide your Coda API token:")
        print("  python read_coda_table.py YOUR_API_TOKEN")
        print("Or set CODA_API_TOKEN environment variable")
        sys.exit(1)
    
    read_coda_table(api_token)