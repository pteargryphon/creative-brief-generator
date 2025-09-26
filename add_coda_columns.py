#!/usr/bin/env python3
"""
Add debug columns to Coda table
"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def add_column(column_name, column_type='text'):
    """Add a column to the Coda table"""
    api_token = os.environ.get('CODA_API_TOKEN')
    doc_id = 'TeddWcsh5U'
    table_id = 'grid-XSXEqW-PnP'
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }
    
    # Coda API endpoint for adding columns
    url = f'https://coda.io/apis/v1/docs/{doc_id}/tables/{table_id}/columns'
    
    payload = {
        'name': column_name,
        'format': {
            'type': column_type
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code in [200, 201, 202]:
            print(f"✅ Successfully added column: {column_name}")
            return True
        elif response.status_code == 400 and 'already exists' in response.text.lower():
            print(f"⚠️  Column '{column_name}' already exists")
            return True
        else:
            print(f"❌ Error adding column '{column_name}': {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("Adding debug columns to Coda table...")
    print("="*50)
    
    # Add Debug_Errors column (for error messages)
    add_column('Debug_Errors', 'text')
    
    # Add API_Status column (for API key status)
    add_column('API_Status', 'text')
    
    # Add Processing_Time column (optional, for performance tracking)
    add_column('Processing_Time', 'text')
    
    print("\n" + "="*50)
    print("Column setup complete!")
    print("\nThese columns will now capture:")
    print("• Debug_Errors: Any errors that occur during generation")
    print("• API_Status: Status of each API (OpenAI, Foreplay, Apify)")
    print("• Processing_Time: How long generation took")

if __name__ == "__main__":
    main()