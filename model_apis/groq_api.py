"""
Groq API Wrapper
Direct integration with Groq API for Llama models (alternative to OpenRouter).
"""

import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

try:
    from groq import Groq
except ImportError:
    Groq = None

load_dotenv()


class GroqAPI:
    """Wrapper for direct Groq API access."""
    
    MODELS = [
        "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant"
    ]
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Groq API client.
        
        Args:
            api_key: Groq API key (defaults to env variable)
        """
        if Groq is None:
            raise ImportError("groq package not installed. Run: pip install groq")
        
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Groq API key not found. Set GROQ_API_KEY in .env")
        
        self.client = Groq(api_key=self.api_key)
    
    def generate(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> Dict:
        """
        Generate completion using Groq model.
        
        Args:
            model: Model name (e.g., "llama-3.1-70b-versatile")
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
