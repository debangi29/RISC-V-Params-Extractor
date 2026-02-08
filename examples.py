"""
Example: Simple Parameter Extraction
Demonstrates basic usage of the RISC-V Parameter Extractor.
"""

from extractor import RISCVParamsExtractor
from utils import YAMLGenerator
import json

def example_single_snippet():
    """Extract from a single snippet."""
    print("=" * 60)
    print("Example 1: Single Snippet Extraction")
    print("=" * 60)
    
    # Initialize extractor
    extractor = RISCVParamsExtractor()
    
    # Extract from one file
    results = extractor.extract_from_file(
        "snippets/privileged_19_3_1.txt",
        prompt_strategy="few_shot"
    )
    
    # Display results
    print("\nResults by model:")
    for model, result in results.items():
        if result.get("success"):
            params = result.get("parameters", [])
            print(f"\n{model}: Found {len(params)} parameters")
            for param in params:
                print(f"  - {param.get('name', 'unnamed')}")
        else:
            print(f"\n{model}: Failed - {result.get('error', 'Unknown error')}")


def example_with_validation():
    """Extract and validate using consensus."""
    print("\n" + "=" * 60)
    print("Example 2: Extraction with Consensus Validation")
    print("=" * 60)
    
    # Initialize extractor
    extractor = RISCVParamsExtractor()
    
    # Extract from all snippets
    print("\nExtracting from all snippets...")
    extraction_results = extractor.extract_from_directory(
        "snippets",
        prompt_strategy="few_shot"
    )
    
    # Validate using consensus
    print("\nValidating with consensus...")
    validated = extractor.validate_and_merge(extraction_results)
    
    # Display summary
    for snippet_name, validation in validated.items():
        summary = validation.get("validation_summary", {})
        print(f"\n{snippet_name}:")
        print(f"  Total parameters: {summary.get('total_parameters', 0)}")
        print(f"  High confidence: {summary.get('high_confidence', 0)}")
        print(f"  Medium confidence: {summary.get('medium_confidence', 0)}")
        print(f"  Low confidence: {summary.get('low_confidence', 0)}")
        
        # Show high-confidence parameters
        high_conf_params = [
            p for p in validation.get("parameters", [])
            if p.get("confidence_level") == "high"
        ]
        
        if high_conf_params:
            print(f"\n  High-confidence parameters:")
            for param in high_conf_params[:3]:  # Show first 3
                print(f"    - {param.get('name')}: {param.get('confidence', 0):.1%} agreement")


def example_custom_models():
    """Use a subset of models."""
    print("\n" + "=" * 60)
    print("Example 3: Custom Model Selection")
    print("=" * 60)
    
    # Use only 3 fast models
    fast_models = [
        "openai/gpt-4o-mini",
        "anthropic/claude-3-haiku",
        "google/gemini-flash-1.5"
    ]
    
    extractor = RISCVParamsExtractor(models=fast_models)
    
    print(f"\nUsing {len(fast_models)} models:")
    for model in fast_models:
        print(f"  - {model}")
    
    # Extract
    results = extractor.extract_from_file(
        "snippets/privileged_2_1.txt",
        prompt_strategy="zero_shot"
    )
    
    print("\nExtraction complete!")
    for model, result in results.items():
        status = "[OK]" if result.get("success") else "[FAIL]"
        print(f"  {status} {model}")


def example_compare_strategies():
    """Compare different prompt strategies."""
    print("\n" + "=" * 60)
    print("Example 4: Comparing Prompt Strategies")
    print("=" * 60)
    
    extractor = RISCVParamsExtractor()
    strategies = ["zero_shot", "few_shot", "chain_of_thought"]
    
    snippet_file = "snippets/privileged_19_3_1.txt"
    
    print(f"\nComparing strategies on: {snippet_file}\n")
    
    for strategy in strategies:
        print(f"\n{strategy.upper()}:")
        results = extractor.extract_from_file(snippet_file, prompt_strategy=strategy)
        
        # Count successful extractions
        successful = sum(1 for r in results.values() if r.get("success"))
        total_params = sum(
            len(r.get("parameters", []))
            for r in results.values()
            if r.get("success")
        )
        
        print(f"  Successful models: {successful}/{len(results)}")
        print(f"  Total parameters extracted: {total_params}")


if __name__ == "__main__":
    print("\nRISC-V Parameter Extractor - Examples\n")
    
    # Run examples
    example_single_snippet()
    example_with_validation()
    example_custom_models()
    example_compare_strategies()
    
    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Run 'python main.py' for full extraction")
    print("  2. Check 'outputs/' directory for results")
    print("  3. Read 'docs/QUICK_START.md' for more info")
    print()
