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

```
┌─────────────────────────────────────────────────────────────────────┐
│                         RISC-V PARAMETER EXTRACTOR                   │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│  Input Layer    │
│  (Snippets)     │
│  - .txt files   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      PROMPT STRATEGY LAYER                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────┐  ┌──────┐     │
│  │Zero-Shot │  │One-Shot  │  │Few-Shot  │  │ CoT  │  │ ToT  │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────┘  └──────┘     │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      MODEL API LAYER                                 │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              OpenRouter API (Primary)                        │   │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐   │   │
│  │  │OpenAI  │ │Anthropic│ │Google  │ │ Groq   │ │Cohere  │   │   │
│  │  │3 models│ │3 models │ │2 models│ │1 model │ │1 model │   │   │
│  │  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  Direct API Wrappers (Future Use):                                  │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐          │
│  │OpenAI  │ │Anthropic│ │Google  │ │ Groq   │ │Cohere  │          │
│  │  API   │ │  API    │ │  API   │ │  API   │ │  API   │          │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘          │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    ERROR HANDLING LAYER                              │
│  ┌──────────────────┐         ┌──────────────────────┐             │
│  │ Skip Strategy    │         │ Exponential Backoff  │             │
│  │ (Default)        │         │ (Optional)           │             │
│  └──────────────────┘         └──────────────────────┘             │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    EXTRACTION LAYER                                  │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │         RISCVParamsExtractor (Main Orchestrator)             │  │
│  │  - Manages multi-model extraction                            │  │
│  │  - Parses YAML responses                                     │  │
│  │  - Coordinates prompt strategies                             │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    VALIDATION LAYER                                  │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │         Consensus Validator                                   │  │
│  │  - Counts parameter agreement across models                  │  │
│  │  - Calculates confidence scores                              │  │
│  │  - Merges parameter versions                                 │  │
│  │  - Flags low-confidence items for review                     │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      OUTPUT LAYER                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐ │
│  │ CSV Files    │  │ YAML Files   │  │ Review Files             │ │
│  │ - Inventory  │  │ - Parameters │  │ - Low confidence params  │ │
│  │ - Comparison │  │ - Metadata   │  │                          │ │
│  │ - Detailed   │  │              │  │                          │ │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘

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
# Primary API (Required)
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Individual Provider APIs (Optional - for future direct integration)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIzaSy...
GROQ_API_KEY=gsk_...
COHERE_API_KEY=...

# Error Handling
ENABLE_EXPONENTIAL_BACKOFF=false  # Set to 'true' to enable retries
MAX_RETRIES=3                      # Number of retry attempts
RETRY_DELAY_SECONDS=2              # Base delay between retries
```

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

## LLM Models

### Models Used (via OpenRouter)

| Provider | Model | Context Length | Notes |
|----------|-------|----------------|-------|
| OpenAI | gpt-4o | 128K tokens | Most capable |
| OpenAI | gpt-4o-mini | 128K tokens | Fast, cost-effective |
| OpenAI | gpt-3.5-turbo | 16K tokens | Baseline |
| Anthropic | claude-3.5-sonnet | 200K tokens | Excellent reasoning |
| Anthropic | claude-3-opus | 200K tokens | Most powerful |
| Anthropic | claude-3-haiku | 200K tokens | Fastest |
| Google | gemini-1.5-pro | 2M tokens | Largest context |
| Google | gemini-1.5-flash | 1M tokens | Fast inference |
| Meta (via Groq) | llama-3.1-70b | 128K tokens | Open source |
| Cohere | command-r-plus | 128K tokens | RAG-optimized |

### Model Selection Rationale

- **Diversity**: Multiple providers reduce bias
- **Capabilities**: Mix of reasoning, speed, and context
- **Availability**: All accessible through OpenRouter
- **Cost**: Balanced between performance and budget

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
ValueError: OpenRouter API key not found
```
**Solution**: Add `OPENROUTER_API_KEY` to `.env` file

**2. Import Errors**
```
ModuleNotFoundError: No module named 'openai'
```
**Solution**: Run `pip install -r requirements.txt`

**3. YAML Parsing Failures**
```
Warning: Failed to parse YAML
```
**Solution**: This is normal for some models. The system handles it gracefully and marks as failed extraction.

**4. Rate Limiting**
```
Error: Rate limit exceeded
```
**Solution**: Enable exponential backoff in `.env`:
```bash
ENABLE_EXPONENTIAL_BACKOFF=true
MAX_RETRIES=5
```

### Debug Mode

Add verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

extractor = RISCVParamsExtractor()
# Now see detailed logs
```

## Project Structure

```
RISC-V Extract/
├── snippets/                    # Input specification snippets
│   ├── privileged_19_3_1.txt
│   └── privileged_2_1.txt
├── model_apis/                  # LLM provider integrations
│   ├── __init__.py
│   ├── openrouter_api.py       # Primary (OpenRouter)
│   ├── openai_api.py           # Direct OpenAI
│   ├── anthropic_api.py        # Direct Anthropic
│   ├── google_api.py           # Direct Google
│   ├── groq_api.py             # Direct Groq
│   └── cohere_api.py           # Direct Cohere
├── prompts/                     # Prompt strategies
│   ├── __init__.py
│   └── prompt_strategies.py    # All 5 strategies
├── extractor/                   # Core extraction logic
│   ├── __init__.py
│   ├── risc_v_params_extractor.py  # Main orchestrator
│   ├── error_handler.py        # Error handling strategies
│   └── consensus_validator.py  # Validation logic
├── utils/                       # Output generators
│   ├── __init__.py
│   ├── csv_generator.py
│   └── yaml_generator.py
├── outputs/                     # Generated results
│   ├── snippets_inventory.csv
│   ├── comparison_*.csv
│   ├── detailed_results_*.csv
│   └── parameters_*.yaml
├── main.py                      # Entry point
├── requirements.txt             # Dependencies
├── .env                         # Configuration
└── README.md                    # This file
```

## Contributing

To contribute:
1. Add new models in `model_apis/`
2. Create new prompt strategies in `prompts/`
3. Enhance validation in `extractor/consensus_validator.py`
4. Improve error handling in `extractor/error_handler.py`

## License

This project is provided as-is for RISC-V architectural analysis.

## Contact

For questions or issues, please refer to the project documentation or create an issue in the repository.
