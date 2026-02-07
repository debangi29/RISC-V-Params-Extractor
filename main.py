"""
RISC-V Parameter Extractor - Main Entry Point
Extracts architectural parameters from RISC-V specifications using multiple LLMs.
"""

import os
from pathlib import Path

from extractor import RISCVParamsExtractor
from utils import CSVGenerator, YAMLGenerator


def main():
    """Main execution function."""
    
    print("=" * 80)
    print("RISC-V Architectural Parameter Extractor")
    print("=" * 80)
    print()
    
    # Define paths
    base_dir = Path(__file__).parent
    snippets_dir = base_dir / "snippets"
    outputs_dir = base_dir / "outputs"
    
    # Create outputs directory
    outputs_dir.mkdir(exist_ok=True)
    
    # Step 1: Create snippets CSV
    print("Step 1: Creating snippets inventory CSV...")
    CSVGenerator.create_snippets_csv(
        str(snippets_dir),
        str(outputs_dir / "snippets_inventory.csv")
    )
    print()
    
    # Step 2: Initialize extractor
    print("Step 2: Initializing RISC-V Parameter Extractor...")
    extractor = RISCVParamsExtractor()
    
    # Display model information
    model_info = extractor.get_model_info()
    print(f"  Using {len(model_info)} models:")
    for info in model_info:
        print(f"    - {info['full_name']} (via {info['access_method']})")
    print()
    
    # Step 3: Extract parameters using different prompt strategies
    # prompt_strategies = ["zero_shot", "one_shot", "few_shot", "chain_of_thought", "tree_of_thoughts"]
    prompt_strategies = ["one_shot"]
 
    for strategy in prompt_strategies:
        print(f"\nStep 3.{prompt_strategies.index(strategy) + 1}: Extracting with {strategy} strategy...")
        print("-" * 80)
        
        # Extract from all snippets
        extraction_results = extractor.extract_from_directory(
            str(snippets_dir),
            prompt_strategy=strategy
        )
        
        # Step 4: Create comparison CSV
        print(f"\nStep 4.{prompt_strategies.index(strategy) + 1}: Creating comparison CSV...")
        CSVGenerator.create_comparison_csv(
            extraction_results,
            str(outputs_dir / f"comparison_{strategy}.csv")
        )
        
        # Step 5: Validate and merge using consensus
        print(f"\nStep 5.{prompt_strategies.index(strategy) + 1}: Validating with consensus...")
        validated_results = extractor.validate_and_merge(extraction_results)
        
        # Display summary
        for snippet_name, validation in validated_results.items():
            summary = validation.get("validation_summary", {})
            print(f"  {snippet_name}:")
            print(f"    Total parameters: {summary.get('total_parameters', 0)}")
            print(f"    High confidence: {summary.get('high_confidence', 0)}")
            print(f"    Medium confidence: {summary.get('medium_confidence', 0)}")
            print(f"    Low confidence: {summary.get('low_confidence', 0)}")
        
        # Step 6: Create detailed CSV
        print(f"\nStep 6.{prompt_strategies.index(strategy) + 1}: Creating detailed results CSV...")
        CSVGenerator.create_detailed_csv(
            validated_results,
            str(outputs_dir / f"detailed_results_{strategy}.csv")
        )
        
        # Step 7: Create final YAML
        print(f"\nStep 7.{prompt_strategies.index(strategy) + 1}: Creating final parameters YAML...")
        YAMLGenerator.create_parameters_yaml(
            validated_results,
            model_info,
            str(outputs_dir / f"parameters_{strategy}.yaml"),
            prompt_strategy=strategy
        )
        
        print(f"\n{'=' * 80}")
        print(f"Completed extraction with {strategy} strategy")
        print(f"{'=' * 80}\n")
    
    # Final summary
    print("\n" + "=" * 80)
    print("EXTRACTION COMPLETE!")
    print("=" * 80)
    print(f"\nOutputs saved to: {outputs_dir}")
    print("\nGenerated files:")
    print("  - snippets_inventory.csv: List of all input snippets")
    
    for strategy in prompt_strategies:
        print(f"\n  {strategy.upper()} Strategy:")
        print(f"    - comparison_{strategy}.csv: Model-by-model comparison")
        print(f"    - detailed_results_{strategy}.csv: All parameters with confidence scores")
        print(f"    - parameters_{strategy}.yaml: Final validated parameters")
    
    print("\nRecommendation:")
    print("  Compare results across different prompt strategies to identify")
    print("  the most effective approach for your specific use case.")
    print()


if __name__ == "__main__":
    main()
