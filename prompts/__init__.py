"""
Prompts Package
Provides various prompting strategies for parameter extraction.
"""

from .prompt_strategies import (
    PromptFactory,
    ZeroShotPrompt,
    OneShotPrompt,
    FewShotPrompt,
    ChainOfThoughtPrompt,
    TreeOfThoughtsPrompt
)

__all__ = [
    'PromptFactory',
    'ZeroShotPrompt',
    'OneShotPrompt',
    'FewShotPrompt',
    'ChainOfThoughtPrompt',
    'TreeOfThoughtsPrompt'
]
