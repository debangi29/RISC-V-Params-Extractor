"""
OpenRouter API Wrapper
Provides unified access to multiple LLM providers through OpenRouter.
Supports multiple API keys with random selection to avoid rate limits.
"""

import os
import random
import requests
import time
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

api_tracker = 0

class OpenRouterAPI:
    """
    Wrapper for OpenRouter API that provides access to multiple LLM providers.
    Supports multiple API keys to distribute load and avoid rate limiting.
    """
    
    # Available models through OpenRouter (verified 2026-02-07)
    MODELS = [
        # Nvidia models
        "nvidia/nemotron-3-nano-30b-a3b:free",
        # QWEN models
        "qwen/qwen3-coder-next",
        # Moonshot kimi k2
        "moonshotai/kimi-k2.5",
        # OpenAI models
        "openai/gpt-4o-mini",
        "openai/gpt-3.5-turbo",
        # Anthropic models
        "anthropic/claude-3-haiku",
        # Google models
        "google/gemini-3-flash-preview",
        "google/gemini-2.5-flash",
        # Meta models
        "meta-llama/llama-3.1-70b-instruct",
        # Mistral models
        "mistralai/ministral-14b-2512"
    ]
    
    def __init__(self, api_keys: Optional[List[str]] = None):
        """
        Initialize OpenRouter API client with multiple API keys.
        
        Args:
            api_keys: List of OpenRouter API keys (defaults to env variables)
        """
        if api_keys:
            self.api_keys = api_keys
        else:
            # Load multiple API keys from environment
            self.api_keys = self._load_api_keys_from_env()
        
        if not self.api_keys:
            raise ValueError("No OpenRouter API keys found. Set OPENROUTER_API_KEY or OPENROUTER_API_KEY_1, OPENROUTER_API_KEY_2, etc. in .env")
        
        print(f"  Loaded {len(self.api_keys)} API key(s) for load distribution")
        
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.request_delay = float(os.getenv("REQUEST_DELAY_SECONDS", "0.5"))
    
    def _load_api_keys_from_env(self) -> List[str]:
        """Load all API keys from environment variables."""
        keys = []
        
        # Try single key first
        single_key = os.getenv("OPENROUTER_API_KEY")
        if single_key:
            keys.append(single_key)
        
        # Try numbered keys (OPENROUTER_API_KEY_1, OPENROUTER_API_KEY_2, etc.)
        i = 1
        while True:
            key = os.getenv(f"OPENROUTER_API_KEY_{i}")
            if key:
                keys.append(key)
                i += 1
            else:
                break
        
        return keys
    
    def _get_random_api_key(self) -> str:
        """Randomly select an API key from the pool."""
        # return random.choice(self.api_keys)
        global api_tracker
        api_tracker += 1
        return self.api_keys[api_tracker%5]
    
    def _get_headers(self, api_key: str) -> Dict[str, str]:
        """Generate headers with the specified API key."""
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/risc-v-param-extractor",
            "X-Title": "RISC-V Parameter Extractor"
        }
    
    def generate(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> Dict:
        """
        Generate completion using specified model.
        Randomly selects an API key to distribute load.
        
        Args:
            model: Model identifier (e.g., "openai/gpt-4o")
            prompt: Input prompt text
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional model-specific parameters
        
        Returns:
            Dict containing response text and metadata
        """
        # Randomly select an API key
        api_key = self._get_random_api_key()
        headers = self._get_headers(api_key)
        
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        try:
            # Add small delay to avoid rate limiting
            if self.request_delay > 0:
                time.sleep(self.request_delay)
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "success": True,
                "text": data["choices"][0]["message"]["content"],
                "model": model,
                "usage": data.get("usage", {}),
                "raw_response": data
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "model": model,
                "text": None
            }
    
    @classmethod
    def get_available_models(cls) -> List[str]:
        """
        Get list of available models.
        
        Returns:
            List of model identifiers
        """
        return cls.MODELS.copy()
    
    @classmethod
    def get_provider_models(cls, provider: str) -> List[str]:
        """
        Get models from a specific provider.
        
        Args:
            provider: Provider name (e.g., "openai", "anthropic")
        
        Returns:
            List of models from that provider
        """
        return [m for m in cls.MODELS if m.startswith(f"{provider}/")]
