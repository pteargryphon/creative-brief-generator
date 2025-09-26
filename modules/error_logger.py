"""
Error logging module to track and report errors
"""
import os
import json
from datetime import datetime
import traceback
import requests

class ErrorLogger:
    def __init__(self):
        self.errors = []
        self.coda_token = os.environ.get('CODA_API_TOKEN')
        self.doc_id = 'TeddWcsh5U'
        self.table_id = 'grid-XSXEqW-PnP'
        
    def log_error(self, module, error, context=None):
        """Log an error with context"""
        error_data = {
            'timestamp': datetime.now().isoformat(),
            'module': module,
            'error': str(error),
            'error_type': type(error).__name__,
            'context': context,
            'traceback': traceback.format_exc()
        }
        
        self.errors.append(error_data)
        
        # Print to console for Render logs
        print(f"ERROR in {module}: {error}")
        if context:
            print(f"Context: {context}")
        
        return error_data
    
    def get_errors(self):
        """Get all logged errors"""
        return self.errors
    
    def clear_errors(self):
        """Clear error log"""
        self.errors = []
    
    def get_error_summary(self):
        """Get a summary of all errors for Coda"""
        if not self.errors:
            return "No errors logged"
        
        summary = []
        for err in self.errors:
            summary.append(f"{err['module']}: {err['error_type']} - {err['error'][:100]}")
        
        return "\n".join(summary)
    
    def log_to_coda(self, brief_data):
        """Add error log to the Coda brief data"""
        brief_data['Debug_Errors'] = self.get_error_summary()
        brief_data['API_Status'] = self.check_api_status()
        return brief_data
    
    def check_api_status(self):
        """Check which APIs are working"""
        status = []
        
        # Check OpenAI
        openai_key = os.environ.get('OPENAI_API_KEY', '')
        if not openai_key or openai_key == 'sk-...':
            status.append("❌ OpenAI: Invalid key")
        else:
            status.append(f"✅ OpenAI: Key set ({openai_key[:10]}...)")
        
        # Check Foreplay
        foreplay_key = os.environ.get('FOREPLAY_API_KEY', '')
        if not foreplay_key or foreplay_key == 'your_foreplay_api_key_here':
            status.append("❌ Foreplay: Invalid key")
        else:
            status.append(f"✅ Foreplay: Key set ({foreplay_key[:10]}...)")
        
        # Check Apify
        apify_key = os.environ.get('APIFY_API_TOKEN', '')
        if not apify_key or apify_key == 'your_apify_token_here':
            status.append("❌ Apify: Invalid key")
        else:
            status.append(f"✅ Apify: Key set ({apify_key[:10]}...)")
        
        return " | ".join(status)

# Global error logger instance
error_logger = ErrorLogger()