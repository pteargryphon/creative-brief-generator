"""
Helper module for OpenAI operations using direct requests
This bypasses the httpx proxy issues entirely
"""
import os
import requests
import json

class OpenAIHelper:
    """Direct OpenAI API wrapper using requests library"""
    
    def __init__(self):
        self.api_key = os.environ.get('OPENAI_API_KEY')
        self.base_url = "https://api.openai.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        # Using gpt-5-mini as default - it's the latest cost-effective GPT-5 model
        self.model = "gpt-5-mini"
        
    def chat(self):
        """Compatibility layer to mimic OpenAI client structure"""
        return self
    
    @property
    def completions(self):
        """Compatibility layer to mimic OpenAI client structure"""
        return self
        
    def create(self, messages, model=None, temperature=0.7, max_tokens=500, **kwargs):
        """
        Create a chat completion using direct API call
        Mimics the OpenAI client.chat.completions.create() interface
        """
        try:
            # Use provided model or default
            model = model or self.model
            
            data = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            # Add any additional kwargs (like response_format, etc)
            data.update(kwargs)
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=data,
                timeout=60
            )
            
            if response.status_code != 200:
                raise Exception(f"OpenAI API error: {response.status_code} - {response.text[:200]}")
            
            # Return object that mimics OpenAI response structure
            result = response.json()
            return OpenAIResponse(result)
            
        except requests.exceptions.Timeout:
            raise Exception("OpenAI API request timed out")
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

class OpenAIResponse:
    """Wrapper to mimic OpenAI SDK response structure"""
    
    def __init__(self, response_dict):
        self.response_dict = response_dict
        self.choices = [Choice(c) for c in response_dict.get('choices', [])]

class Choice:
    """Wrapper for response choice"""
    
    def __init__(self, choice_dict):
        self.choice_dict = choice_dict
        self.message = Message(choice_dict.get('message', {}))

class Message:
    """Wrapper for response message"""
    
    def __init__(self, message_dict):
        self.message_dict = message_dict
        self.content = message_dict.get('content', '')

def get_openai_client():
    """
    Get OpenAI helper instance
    Returns OpenAIHelper instance that mimics OpenAI client interface
    """
    return OpenAIHelper()