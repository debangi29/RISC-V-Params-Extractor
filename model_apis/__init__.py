"""
Model APIs Package
Provides unified interface to multiple LLM providers.
"""

from .openrouter_api import OpenRouterAPI

# Optional imports - don't fail if packages aren't installed
try:
    from .openai_api import OpenAIAPI
except ImportError:
    OpenAIAPI = None

try:
    from .anthropic_api import AnthropicAPI
except ImportError:
    AnthropicAPI = None

try:
    from .google_api import GoogleAPI
except ImportError:
    GoogleAPI = None

try:
    from .groq_api import GroqAPI
except ImportError:
    GroqAPI = None

try:
    from .cohere_api import CohereAPI
except ImportError:
    CohereAPI = None

__all__ = [
    'OpenRouterAPI',
    'OpenAIAPI',
    'AnthropicAPI',
    'GoogleAPI',
    'GroqAPI',
    'CohereAPI'
]
