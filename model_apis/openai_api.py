"""
OpenAI API Wrapper
Direct integration with OpenAI API (alternative to OpenRouter).
"""

import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

load_dotenv()


class OpenAIAPI:
    """Wrapper for direct OpenAI API access."""
    
    MODELS = [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-3.5-turbo"
    ]
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI API client.
        
        Args:
            api_key: OpenAI API key (defaults to env variable)
        """
        if OpenAI is None:
            raise ImportError("openai package not installed. Run: pip install openai")
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY in .env")
        
        self.client = OpenAI(api_key=self.api_key)
    
    def generate(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> Dict:
        """
        Generate completion using OpenAI model.
        
        Args:
            model: Model name (e.g., "gpt-4o")
            prompt: Input prompt text
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
        
        Returns:
            Dict containing response text and metadata
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            return {
                "success": True,
                "text": response.choices[0].message.content,
                "model": model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
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
