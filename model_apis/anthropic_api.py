"""
Anthropic API Wrapper
Direct integration with Anthropic Claude API (alternative to OpenRouter).
"""

import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

try:
    import anthropic
except ImportError:
    anthropic = None

load_dotenv()


class AnthropicAPI:
    """Wrapper for direct Anthropic API access."""
    
    MODELS = [
        "claude-3-5-sonnet-20241022",
        "claude-3-opus-20240229",
        "claude-3-haiku-20240307"
    ]
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Anthropic API client.
        
        Args:
            api_key: Anthropic API key (defaults to env variable)
        """
        if anthropic is None:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")
        
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key not found. Set ANTHROPIC_API_KEY in .env")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def generate(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> Dict:
        """
        Generate completion using Anthropic model.
        
        Args:
            model: Model name (e.g., "claude-3-5-sonnet-20241022")
            prompt: Input prompt text
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
        
        Returns:
            Dict containing response text and metadata
        """
        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            
            return {
                "success": True,
                "text": response.content[0].text,
                "model": model,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
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
