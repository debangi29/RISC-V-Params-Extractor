"""
Prompt Strategies for RISC-V Parameter Extraction
Implements multiple prompting techniques: zero-shot, one-shot, few-shot, CoT, and ToT.
"""

from typing import Dict, List


class PromptStrategy:
    """Base class for prompt strategies."""
    
    TRIGGER_WORDS = [
        "may", "might", "should", "could",
        "optional", "optionally",
        "implementation defined", "implementation-defined",
        "implementation specific", "implementation-specific",
        "platform defined", "platform-specific"
    ]
    
    @staticmethod
    def get_base_instruction() -> str:
        """Get the base instruction for parameter extraction."""
        return """You are an expert in RISC-V architecture. Your task is to extract architectural parameters from specification text.

A parameter is any aspect of the architecture that is:
- Implementation-defined or implementation-specific
- Optional or configurable
- Described with words like "may", "might", "should", "could"

For each parameter, provide:
1. **name**: A concise identifier (snake_case)
2. **description**: What the parameter controls
3. **type**: The category (e.g., "implementation-specific", "optional", "configurable")
4. **constraints**: Any mentioned limitations or requirements
5. **keywords**: Trigger words found in the text

Format your response as a valid YAML list."""


class ZeroShotPrompt(PromptStrategy):
    """Zero-shot prompting: Direct instruction without examples."""
    
    @classmethod
    def create(cls, snippet: str) -> str:
        """
        Create zero-shot prompt.
        
        Args:
            snippet: RISC-V specification text
        
        Returns:
            Formatted prompt string
        """
        return f"""{cls.get_base_instruction()}

**Specification Text:**
{snippet}

**Extract all parameters in YAML format:**"""


class OneShotPrompt(PromptStrategy):
    """One-shot prompting: Single example provided."""
    
    EXAMPLE = {
        "text": """The cache line size is implementation-defined. Systems may use cache lines 
ranging from 32 to 128 bytes, and the size should be a power of two.""",
        "output": """- name: cache_line_size
  description: Size of a cache line in bytes
  type: implementation-defined
  constraints: Must be power of two, range 32-128 bytes
  keywords: [implementation-defined, may, should]"""
    }
    
    @classmethod
    def create(cls, snippet: str) -> str:
        """
        Create one-shot prompt with single example.
        
        Args:
            snippet: RISC-V specification text
        
        Returns:
            Formatted prompt string
        """
        return f"""{cls.get_base_instruction()}

**Example:**

Input Text:
{cls.EXAMPLE['text']}

Output:
{cls.EXAMPLE['output']}

---

**Now extract parameters from this specification text:**
{snippet}

**Output in YAML format:**"""


class FewShotPrompt(PromptStrategy):
    """Few-shot prompting: Multiple examples provided."""
    
    EXAMPLES = [
        {
            "text": """The cache line size is implementation-defined. Systems may use cache lines 
ranging from 32 to 128 bytes, and the size should be a power of two.""",
            "output": """- name: cache_line_size
  description: Size of a cache line in bytes
  type: implementation-defined
  constraints: Must be power of two, range 32-128 bytes
  keywords: [implementation-defined, may, should]"""
        },
        {
            "text": """The number of hardware performance counters is implementation-specific. 
Implementations may provide between 2 and 29 counters.""",
            "output": """- name: hardware_performance_counter_count
  description: Number of hardware performance monitoring counters
  type: implementation-specific
  constraints: Range 2-29 counters
  keywords: [implementation-specific, may]"""
        },
        {
            "text": """Support for misaligned memory accesses is optional. If supported, 
the implementation should handle them efficiently.""",
            "output": """- name: misaligned_memory_access_support
  description: Whether misaligned memory accesses are supported
  type: optional
  constraints: If supported, should be efficient
  keywords: [optional, should]"""
        }
    ]
    
    @classmethod
    def create(cls, snippet: str) -> str:
        """
        Create few-shot prompt with multiple examples.
        
        Args:
            snippet: RISC-V specification text
        
        Returns:
            Formatted prompt string
        """
        examples_text = "\n\n---\n\n".join([
            f"**Example {i+1}:**\n\nInput Text:\n{ex['text']}\n\nOutput:\n{ex['output']}"
            for i, ex in enumerate(cls.EXAMPLES)
        ])
        
        return f"""{cls.get_base_instruction()}

{examples_text}

---

**Now extract parameters from this specification text:**
{snippet}

**Output in YAML format:**"""


class ChainOfThoughtPrompt(PromptStrategy):
    """Chain-of-Thought prompting: Encourage step-by-step reasoning."""
    
    @classmethod
    def create(cls, snippet: str) -> str:
        """
        Create CoT prompt that encourages reasoning.
        
        Args:
            snippet: RISC-V specification text
        
        Returns:
            Formatted prompt string
        """
        return f"""{cls.get_base_instruction()}

**Specification Text:**
{snippet}

**Think step-by-step:**

1. First, identify all trigger words (may, might, should, optional, implementation-defined, etc.)
2. For each trigger word, determine what aspect it refers to
3. Extract the parameter name, description, and constraints
4. Verify each parameter is truly configurable or implementation-specific
5. Format the results as YAML

**Your reasoning and final YAML output:**"""


class TreeOfThoughtsPrompt(PromptStrategy):
    """Tree-of-Thoughts prompting: Explore multiple reasoning paths."""
    
    @classmethod
    def create(cls, snippet: str) -> str:
        """
        Create ToT prompt that explores multiple interpretations.
        
        Args:
            snippet: RISC-V specification text
        
        Returns:
            Formatted prompt string
        """
        return f"""{cls.get_base_instruction()}

**Specification Text:**
{snippet}

**Analyze using multiple perspectives:**

**Path 1 - Literal Reading:**
- What parameters are explicitly stated as optional or implementation-defined?

**Path 2 - Implicit Parameters:**
- What aspects are described but not explicitly marked as configurable?
- Are there ranges, choices, or alternatives mentioned?

**Path 3 - Constraint Analysis:**
- What constraints or requirements are mentioned?
- Do these constraints imply configurability?

**Synthesis:**
After exploring these paths, synthesize the findings into a comprehensive list of parameters.

**Final YAML output with all discovered parameters:**"""


class PromptFactory:
    """Factory for creating prompts with different strategies."""
    
    STRATEGIES = {
        "zero_shot": ZeroShotPrompt,
        "one_shot": OneShotPrompt,
        "few_shot": FewShotPrompt,
        "chain_of_thought": ChainOfThoughtPrompt,
        "tree_of_thoughts": TreeOfThoughtsPrompt
    }
    
    @classmethod
    def create_prompt(cls, strategy: str, snippet: str) -> str:
        """
        Create prompt using specified strategy.
        
        Args:
            strategy: Strategy name (zero_shot, one_shot, few_shot, chain_of_thought, tree_of_thoughts)
            snippet: RISC-V specification text
        
        Returns:
            Formatted prompt string
        
        Raises:
            ValueError: If strategy is unknown
        """
        if strategy not in cls.STRATEGIES:
            raise ValueError(
                f"Unknown strategy: {strategy}. "
                f"Available: {list(cls.STRATEGIES.keys())}"
            )
        
        return cls.STRATEGIES[strategy].create(snippet)
    
    @classmethod
    def get_available_strategies(cls) -> List[str]:
        """Get list of available prompt strategies."""
        return list(cls.STRATEGIES.keys())
