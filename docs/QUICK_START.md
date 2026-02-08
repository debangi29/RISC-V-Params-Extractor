# Quick Start Guide

## 5-Minute Setup

### Step 1: Install Dependencies (1 minute)

```bash
cd "c:\Users\deban\OneDrive\Desktop\RISC-V Extract"
pip install -r requirements.txt
```

### Step 2: Configure API Key (1 minute)

1. Get an OpenRouter API key from: https://openrouter.ai/
2. Edit `.env` file:
   ```bash
   OPENROUTER_API_KEY=your_actual_key_here
   ```

### Step 3: Run Extraction (3 minutes)

```bash
python main.py
```

That's it! Results will be in the `outputs/` directory.

## What You Get

After running, you'll find in `outputs/`:

### For Each Prompt Strategy:
- `comparison_[strategy].csv` - Model-by-model results
- `detailed_results_[strategy].csv` - All parameters with confidence
- `parameters_[strategy].yaml` - Final validated parameters

### Recommended First Look:
```bash
# View the few-shot results (best balance)
outputs/parameters_few_shot.yaml
```

## Understanding the Output

### YAML Structure
```yaml
metadata:
  extraction_date: "2026-02-07T..."
  prompt_strategy: "few_shot"
  models_used: [...]
  
parameters:
  - name: cache_block_size
    description: "Size of a cache block"
    type: "implementation-specific"
    constraints: "power-of-two, uniform throughout system"
    source: "privileged_19_3_1.txt"
    keywords: ["implementation-specific", "shall"]
    confidence:
      score: 0.9
      level: "high"
      agreement: "9/10 models"
```

### Confidence Levels
- **High** (≥70% agreement): Reliable, use with confidence
- **Medium** (50-69% agreement): Likely correct, verify if critical
- **Low** (<50% agreement): Review manually, possible hallucination

## Common Tasks

### Extract from New Snippets

1. Add `.txt` files to `snippets/` directory
2. Run `python main.py`
3. Check `outputs/` for results

### Use Specific Prompt Strategy

```python
from extractor import RISCVParamsExtractor

extractor = RISCVParamsExtractor()

# Use only Chain-of-Thought
results = extractor.extract_from_directory(
    "snippets",
    prompt_strategy="chain_of_thought"
)
```

### Use Fewer Models (Faster/Cheaper)

```python
from extractor import RISCVParamsExtractor

# Use only 3 models
extractor = RISCVParamsExtractor(
    models=[
        "openai/gpt-4o",
        "anthropic/claude-3.5-sonnet",
        "google/gemini-flash-1.5"
    ]
)
```

### Enable Retry on Errors

Edit `.env`:
```bash
ENABLE_EXPONENTIAL_BACKOFF=true
MAX_RETRIES=5
```

## Next Steps

1. **Review Results**: Check `outputs/parameters_few_shot.yaml`
2. **Compare Strategies**: Look at different prompt strategy outputs
3. **Adjust Confidence**: Modify threshold in `extractor/consensus_validator.py`
4. **Add Models**: See `docs/MODEL_INFORMATION.md`
5. **Customize Prompts**: See `docs/PROMPT_DEVELOPMENT.md`

## Troubleshooting

### "API key not found"
→ Make sure `.env` has `OPENROUTER_API_KEY=...`

### "Module not found"
→ Run `pip install -r requirements.txt`

### "No snippets found"
→ Add `.txt` files to `snippets/` directory

### "Rate limit exceeded"
→ Enable exponential backoff in `.env`

## Getting Help

- Read `README.md` for full documentation
- Check `docs/` folder for detailed guides
- Review code comments for implementation details

## Example Workflow

```bash
# 1. Setup
pip install -r requirements.txt

# 2. Configure
# Edit .env with your API key

# 3. Add your snippets
# Copy .txt files to snippets/

# 4. Run extraction
python main.py

# 5. Review results
# Check outputs/parameters_few_shot.yaml

# 6. Analyze
# Open outputs/detailed_results_few_shot.csv in Excel
```

## Cost Estimate

For 2 snippets with 10 models:
- **Total cost**: ~$0.10-0.15
- **Time**: ~3-5 minutes

For 100 snippets:
- **Total cost**: ~$5-7
- **Time**: ~2-3 hours

## Tips

1. **Start Small**: Test with 1-2 snippets first
2. **Use Few-Shot**: Best balance of accuracy and cost
3. **Check Confidence**: Focus on high-confidence parameters
4. **Compare Strategies**: Different strategies find different parameters
5. **Validate Manually**: Always review low-confidence items

Enjoy extracting RISC-V parameters!
