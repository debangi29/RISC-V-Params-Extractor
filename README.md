# RISC-V Architectural Parameter Extractor

## Overview

This project extracts architectural parameters from RISC-V specification documents using multiple Large Language Models (LLMs) and advanced prompting strategies. It identifies implementation-defined, optional, and configurable aspects of the RISC-V architecture through AI-assisted analysis.

## Table of Contents

1. [Features](#features)
2. [System Architecture](#system-architecture)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [LLM Models](#llm-models)
7. [Prompt Strategies](#prompt-strategies)
8. [Output Format](#output-format)
9. [Extending the System](#extending-the-system)
10. [Troubleshooting](#troubleshooting)

## Features

### Core Capabilities
- **Multi-Model Extraction**: Uses 10 different LLMs to extract parameters
- **Multiple Prompt Strategies**: 5 different prompting techniques (zero-shot, one-shot, few-shot, CoT, ToT)
- **Consensus Validation**: Validates results using agreement across models
- **Modular Architecture**: Easy to extend with new models or validation logic
- **Comprehensive Output**: CSV for analysis, YAML for structured results
- **Error Handling**: Configurable retry strategies with exponential backoff

### Key Differentiators
- **Hallucination Mitigation**: Consensus voting reduces false positives
- **Confidence Scoring**: Each parameter tagged with confidence level
- **Trigger Word Detection**: Identifies "may", "should", "optional", "implementation-defined"
- **Multiple Provider Support**: OpenRouter, OpenAI, Anthropic, Google, Groq, Cohere

## System Architecture

<img width="5284" height="8192" alt="RISC-V Parameter Extraction-2026-02-10-182643" src="https://github.com/user-attachments/assets/36b64d4a-24e2-446b-883e-be69a2c3bb83" />

```
Data Flow:
1. Text snippets → Prompt strategies → Formatted prompts
2. Prompts → Model APIs → Raw LLM responses
3. Responses → Error handling → Validated outputs
4. Outputs → Extractor → Parsed parameters
5. Parameters → Consensus validator → Confidence scores
6. Validated params → Output generators → CSV/YAML files
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Steps

1. **Clone or download the project**
   ```bash
   cd "c:\Users\deban\OneDrive\Desktop\RISC-V Extract"
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API keys**
   Edit `.env` file and add your OpenRouter API key:
   ```
   OPENROUTER_API_KEY=your_actual_api_key_here
   ```

## Configuration

### Environment Variables (.env)

```bash
# OpenRouter API Keys (Multiple keys for rate limit distribution)
# The system uses cyclic rotation to distribute load evenly
OPENROUTER_API_KEY_1=sk-or-v1-your_first_key_here
OPENROUTER_API_KEY_2=sk-or-v1-your_second_key_here
OPENROUTER_API_KEY_3=sk-or-v1-your_third_key_here
OPENROUTER_API_KEY_4=sk-or-v1-your_fourth_key_here
OPENROUTER_API_KEY_5=sk-or-v1-your_fifth_key_here

# Alternative: Single API key (if you only have one)
# OPENROUTER_API_KEY=sk-or-v1-your_single_key_here

# Individual Provider APIs (Optional - for future direct integration)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIzaSy...
GROQ_API_KEY=gsk_...
COHERE_API_KEY=...

# Error Handling (ENABLED by default)
ENABLE_EXPONENTIAL_BACKOFF=true    # Retry on failures with exponential delays
MAX_RETRIES=3                      # Number of retry attempts
RETRY_DELAY_SECONDS=2              # Base delay (2s → 4s → 8s)

# Rate Limit Protection
REQUEST_DELAY_SECONDS=0.5          # Delay between requests (prevents rate limiting)
```

### API Key Rotation Strategy

The system uses **cyclic (round-robin) rotation** across multiple API keys:

```
Request 1 → Key 1
Request 2 → Key 2
Request 3 → Key 3
Request 4 → Key 4
Request 5 → Key 5
Request 6 → Key 1 (cycles back)
...
```

**Benefits:**
- **5x capacity**: Distributes load across 5 accounts
- **Even distribution**: Each key gets equal usage
- **Rate limit protection**: Prevents hitting limits on any single key
- **Automatic failover**: If one key runs out of credits, others continue working

### Consensus Validation

Default confidence threshold: **0.7** (70% model agreement)

To customize, modify `extractor/consensus_validator.py`:
```python
validator = ConsensusValidator(confidence_threshold=0.8)  # 80% agreement
```

## Usage

### Basic Usage

Run the complete extraction pipeline:

```bash
python main.py
```

This will:
1. Create a CSV inventory of all snippet files
2. Extract parameters using all 5 prompt strategies
3. Generate comparison CSVs for each strategy
4. Validate results using consensus
5. Create detailed results CSVs
6. Generate final YAML outputs

### Custom Usage

```python
from extractor import RISCVParamsExtractor
from utils import YAMLGenerator

# Initialize extractor
extractor = RISCVParamsExtractor()

# Extract from a single snippet
results = extractor.extract_from_file(
    "snippets/privileged_19_3_1.txt",
    prompt_strategy="few_shot"
)

# Extract from directory
all_results = extractor.extract_from_directory(
    "snippets",
    prompt_strategy="chain_of_thought"
)

# Validate and merge
validated = extractor.validate_and_merge(all_results)

# Generate YAML
YAMLGenerator.create_parameters_yaml(
    validated,
    extractor.get_model_info(),
    "outputs/my_parameters.yaml"
)
```

### Organizing Results by Confidence

After running `main.py`, you can organize results by confidence threshold:

```bash
python organize_results.py
```

This will:
1. Filter parameters with confidence ≥ 0.5 (majority agreement)
2. Group by source file
3. Create organized YAML files in `parameters_majority_confidence/`

## LLM Models

### Models Used (via OpenRouter)

| Provider | Model | Context Length | Notes |
|----------|-------|----------------|-------|
| DeepSeek | deepseek-v3.2 | 163,840 tokens | Latest reasoning model |
| Nvidia | nemotron-3-nano-30b-a3b | 128,000 tokens | Efficient, high-quality |
| Qwen | qwen3-coder-next | 400,000 tokens | Code-specialized |
| OpenAI | gpt-4o-mini | 200,000 tokens | Fast, cost-effective |
| OpenAI | gpt-5.1-codex-mini | 1,048,576 tokens | Code understanding |
| Anthropic | claude-3-haiku | 1,048,576 tokens | Fastest Claude |
| Google | gemini-3-flash-preview | 131,072 tokens | Latest Gemini |
| Google | gemini-2.5-flash | 262,144 tokens | Fast inference |
| Meta | llama-3.1-70b-instruct | 262,144 tokens | Open source |
| Mistral | ministral-14b-2512 | 262,144 tokens | Efficient reasoning |

### Model Selection Rationale

- **Latest models**: DeepSeek V3.2, Gemini 3 Flash, GPT-5.1 Codex
- **Diversity**: 7 different providers reduce bias
- **Specialized**: Qwen3 Coder and GPT-5.1 Codex for technical docs
- **Cost-effective**: Mix of premium and efficient models
- **Availability**: All accessible through OpenRouter with cyclic key rotation

## Prompt Strategies

### 1. Zero-Shot
Direct instruction without examples.

**Best for**: Clear, well-defined tasks

**Example**:
```
Extract parameters from this text...
[specification text]
```

### 2. One-Shot
Single example provided.

**Best for**: Demonstrating format

**Example**:
```
Example:
Input: "Cache size is implementation-defined"
Output: [YAML parameter]

Now extract from: [specification text]
```

### 3. Few-Shot
Multiple examples (3) provided.

**Best for**: Complex extraction patterns

**Example**:
```
Example 1: [input] → [output]
Example 2: [input] → [output]
Example 3: [input] → [output]

Now extract from: [specification text]
```

### 4. Chain-of-Thought (CoT)
Encourages step-by-step reasoning.

**Best for**: Reducing hallucinations

**Example**:
```
Think step-by-step:
1. Identify trigger words
2. Determine what they refer to
3. Extract parameters
4. Verify configurability
5. Format as YAML

[specification text]
```

### 5. Tree-of-Thoughts (ToT)
Explores multiple reasoning paths.

**Best for**: Comprehensive extraction

**Example**:
```
Analyze from multiple perspectives:
Path 1: Literal reading
Path 2: Implicit parameters
Path 3: Constraint analysis

Synthesize findings...
[specification text]
```

## Output Format

### CSV Files

#### snippets_inventory.csv
```csv
filename,path,char_count,line_count
privileged_19_3_1.txt,/path/to/file,450,8
```

#### comparison_[strategy].csv
```csv
snippet,model,success,param_count,param_names,error
privileged_19_3_1.txt,openai/gpt-4o,True,3,"cache_block_size,cache_organization",
```

#### detailed_results_[strategy].csv
```csv
snippet,param_name,description,type,constraints,keywords,confidence,confidence_level,agreement_count,total_models,agreed_models
privileged_19_3_1.txt,cache_block_size,Size of cache block,implementation-specific,power-of-two,"implementation-specific,shall",0.9,high,9,10,"gpt-4o,claude-3.5-sonnet,..."
```

### YAML Files

#### parameters_[strategy].yaml
```yaml
metadata:
  extraction_date: "2026-02-07T15:30:00"
  prompt_strategy: "few_shot"
  models_used:
    - full_name: "openai/gpt-4o"
      provider: "openai"
      model: "gpt-4o"
      access_method: "OpenRouter API"
  total_snippets: 2

parameters:
  - name: cache_block_size
    description: Size of a cache block in bytes
    type: implementation-specific
    constraints: Must be uniform throughout system, power-of-two
    source: privileged_19_3_1.txt
    keywords:
      - implementation-specific
      - shall
    confidence:
      score: 0.9
      level: high
      agreement: "9/10 models"
```

## Extending the System

### Adding a New Model Provider

1. **Create API wrapper** in `model_apis/`:

```python
# model_apis/huggingface_api.py
class HuggingFaceAPI:
    MODELS = ["meta-llama/Llama-2-70b-chat-hf"]
    
    def __init__(self, api_key):
        self.api_key = api_key
        # Initialize client
    
    def generate(self, model, prompt, **kwargs):
        # Implementation
        pass
```

2. **Add to `model_apis/__init__.py`**:
```python
from .huggingface_api import HuggingFaceAPI
__all__ = [..., 'HuggingFaceAPI']
```

3. **Update `.env`**:
```bash
HUGGINGFACE_API_KEY=your_key_here
```

4. **Use in extractor**:
```python
from model_apis import HuggingFaceAPI

hf_api = HuggingFaceAPI()
# Integrate with RISCVParamsExtractor
```

### Adding a New Prompt Strategy

1. **Create strategy class** in `prompts/prompt_strategies.py`:

```python
class CustomPrompt(PromptStrategy):
    @classmethod
    def create(cls, snippet: str) -> str:
        return f"""Your custom prompt template
        
        {snippet}
        
        Output:"""
```

2. **Register in PromptFactory**:
```python
STRATEGIES = {
    ...,
    "custom": CustomPrompt
}
```

### Replacing Consensus Logic

```python
from extractor import ConsensusValidator

class MyCustomValidator(ConsensusValidator):
    def validate_parameters(self, model_outputs):
        # Your custom validation logic
        pass

# Use in extractor
extractor = RISCVParamsExtractor(
    consensus_validator=MyCustomValidator()
)
```

## Troubleshooting

### Common Issues

**1. API Key Error**
```
ValueError: No OpenRouter API keys found
```
**Solution**: Add API keys to `.env` file:
```bash
OPENROUTER_API_KEY_1=sk-or-v1-your_key_here
# Or use single key:
OPENROUTER_API_KEY=sk-or-v1-your_key_here
```

**2. Import Errors**
```
ModuleNotFoundError: No module named 'openai'
```
**Solution**: Run `pip install -r requirements.txt`

**3. YAML Parsing Failures**
```
Warning: Failed to parse YAML
```
**Solution**: This is normal for some models. The system handles it gracefully with type-safe keyword parsing and marks as failed extraction.

**4. Rate Limiting**
```
Error: Rate limit exceeded
```
**Solution**: The system already has rate limit protection enabled:
- Cyclic API key rotation (if using multiple keys)
- 0.5s delay between requests
- Exponential backoff on failures

If still hitting limits:
```bash
# Increase delay in .env
REQUEST_DELAY_SECONDS=1.0

# Add more API keys
OPENROUTER_API_KEY_6=sk-or-v1-...
```

**5. Payment Required (402 Error)**
```
Error: 402 Client Error: Payment Required
```
**Solution**: One or more API keys have insufficient credits.

Check which keys are failing:
1. Review the comparison CSV to see which models fail consistently
2. Log into OpenRouter and check credit balance for each key
3. Remove empty keys from `.env` or add credits

The cyclic rotation will automatically skip to the next key, but if most keys are empty, you'll see many 402 errors.

**6. Mixed Type Keywords Error**
```
TypeError: sequence item 1: expected str instance, int found
```
**Solution**: This has been fixed with type-safe keyword handling. Update to the latest version of `csv_generator.py`.

### Debug Mode

Add verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

extractor = RISCVParamsExtractor()
# Now see detailed logs
```
