"""
Google Gemini API Wrapper
Direct integration with Google Gemini API (alternative to OpenRouter).
"""

import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

try:
    import google.generativeai as genai
except ImportError:
    genai = None

load_dotenv()


class GoogleAPI:
    """Wrapper for direct Google Gemini API access."""
    
    MODELS = [
        "gemini-1.5-pro",
        "gemini-1.5-flash"
    ]
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Google Gemini API client.
        
        Args:
            api_key: Google API key (defaults to env variable)
        """
        if genai is None:
            raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")
        
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key not found. Set GOOGLE_API_KEY in .env")
        
        genai.configure(api_key=self.api_key)
    
    def generate(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> Dict:
        """
        Generate completion using Google Gemini model.
        
        Args:
            model: Model name (e.g., "gemini-1.5-pro")
            prompt: Input prompt text
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
        """
        try:
            model_instance = genai.GenerativeModel(model)
            
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
                **kwargs
            }
            
            response = model_instance.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            return {
                "success": True,
                "text": response.text,
                "model": model,
                "usage": {}
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": model,
                "text": None
            }
    
    @classmethod
    def get_available_models(cls) -> List[str]:
        """Get list of available models."""
        return cls.MODELS.copy()
