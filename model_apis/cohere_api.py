"""
Cohere API Wrapper
Direct integration with Cohere API (alternative to OpenRouter).
"""

import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

try:
    import cohere
except ImportError:
    cohere = None

load_dotenv()


class CohereAPI:
    """Wrapper for direct Cohere API access."""
    
    MODELS = [
        "command-r-plus",
        "command-r"
    ]
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Cohere API client.
        
        Args:
            api_key: Cohere API key (defaults to env variable)
        """
        if cohere is None:
            raise ImportError("cohere package not installed. Run: pip install cohere")
        
        self.api_key = api_key or os.getenv("COHERE_API_KEY")
        if not self.api_key:
            raise ValueError("Cohere API key not found. Set COHERE_API_KEY in .env")
        
        self.client = cohere.Client(api_key=self.api_key)
    
    def generate(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> Dict:
        """
        Generate completion using Cohere model.
        
        Args:
            model: Model name (e.g., "command-r-plus")
            prompt: Input prompt text
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
        
        Returns:
            Dict containing response text and metadata
        """
        try:
            response = self.client.chat(
                model=model,
                message=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
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
