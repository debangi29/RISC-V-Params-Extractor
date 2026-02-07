"""
Error Handling Module
Provides configurable error handling strategies for API calls.
"""

import os
import time
from typing import Callable, Any, Dict
from abc import ABC, abstractmethod
from dotenv import load_dotenv

load_dotenv()


class ErrorHandlingStrategy(ABC):
    """Base class for error handling strategies."""
    
    @abstractmethod
    def handle(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with error handling.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
        
        Returns:
            Function result or error dict
        """
        pass


class SkipOnErrorStrategy(ErrorHandlingStrategy):
    """Skip and continue on error (default strategy)."""
    
    def handle(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function, return error dict on failure.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
        
        Returns:
            Function result or error dict
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "strategy": "skip_on_error"
            }


class ExponentialBackoffStrategy(ErrorHandlingStrategy):
    """Retry with exponential backoff on error."""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 2.0,
        max_delay: float = 60.0
    ):
        """
        Initialize exponential backoff strategy.
        
        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay in seconds
            max_delay: Maximum delay in seconds
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    def handle(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with exponential backoff retries.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
        
        Returns:
            Function result or error dict
        """
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                
                if attempt < self.max_retries:
                    # Calculate delay with exponential backoff
                    delay = min(
                        self.base_delay * (2 ** attempt),
                        self.max_delay
                    )
                    
                    print(f"    Attempt {attempt + 1} failed: {e}")
                    print(f"    Retrying in {delay:.1f} seconds...")
                    time.sleep(delay)
                else:
                    print(f"    All {self.max_retries + 1} attempts failed")
        
        return {
            "success": False,
            "error": str(last_error),
            "strategy": "exponential_backoff",
            "attempts": self.max_retries + 1
        }


class ErrorHandler:
    """
    Configurable error handler that uses different strategies.
    """
    
    def __init__(self, strategy: ErrorHandlingStrategy = None):
        """
        Initialize error handler.
        
        Args:
            strategy: Error handling strategy (defaults to config-based)
        """
        if strategy:
            self.strategy = strategy
        else:
            # Load from environment
            use_backoff = os.getenv("ENABLE_EXPONENTIAL_BACKOFF", "false").lower() == "true"
            
            if use_backoff:
                max_retries = int(os.getenv("MAX_RETRIES", "3"))
                base_delay = float(os.getenv("RETRY_DELAY_SECONDS", "2.0"))
                
                self.strategy = ExponentialBackoffStrategy(
                    max_retries=max_retries,
                    base_delay=base_delay
                )
            else:
                self.strategy = SkipOnErrorStrategy()
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with configured error handling.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
        
        Returns:
            Function result or error dict
        """
        return self.strategy.handle(func, *args, **kwargs)
