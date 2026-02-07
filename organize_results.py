"""
Organize Extraction Results by Source
Filters parameters with confidence > 0.5 and organizes them by source file.
"""

import yaml
import os
from pathlib import Path
from typing import Dict, List, Any


class ResultsOrganizer:
    """Organizes validated parameters by source and strategy."""
    
    def __init__(self, outputs_dir: str = "outputs", results_dir: str = "parameters_majority_confidence"):
        """
        Initialize the results organizer.
        
        Args:
            outputs_dir: Directory containing the YAML output files
            results_dir: Directory to save organized results
        """
        self.outputs_dir = Path(outputs_dir)
        self.results_dir = Path(results_dir)
        self.confidence_threshold = 0.5
        
        # Strategies to process
        self.strategies = [
            "zero_shot",
            "one_shot",
            "few_shot",
            "chain_of_thought",
            "tree_of_thoughts"
        ]
    
    def organize_all_results(self):
        """Main method to organize all results."""
        print("=" * 80)
        print("RISC-V Parameter Extraction - Results Organizer")
        print("=" * 80)
        print(f"\nConfidence threshold: >= {self.confidence_threshold}")
        print(f"Input directory: {self.outputs_dir}")
        print(f"Output directory: {self.results_dir}")
        print()
        
        # Create results directory
        self.results_dir.mkdir(exist_ok=True)
        
        # Process each strategy
        for strategy in self.strategies:
            self._process_strategy(strategy)
        
        print("\n" + "=" * 80)
        print("Results organization complete!")
        print("=" * 80)
    
    def _process_strategy(self, strategy: str):
        """
        Process a single strategy's YAML file.
        
        Args:
            strategy: Name of the prompt strategy
        """
        yaml_file = self.outputs_dir / f"parameters_{strategy}.yaml"
        
        if not yaml_file.exists():
            print(f" Skipping {strategy}: File not found")
            return
        
        print(f"\nProcessing {strategy}...")
        
        # Load YAML file
        with open(yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data or 'parameters' not in data:
            print(f"   No parameters found in {strategy}")
            return
        
        # Group parameters by source
        source_params = self._group_by_source(data['parameters'])
        
        # Save organized results for each source
        for source_name, params in source_params.items():
            self._save_source_results(strategy, source_name, params, data.get('metadata', {}))
    
    def _group_by_source(self, parameters: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group parameters by source file and filter by confidence.
        
        Args:
            parameters: List of parameter dictionaries
        
        Returns:
            Dictionary mapping source names to filtered parameter lists
        """
        source_groups = {}
        
        for param in parameters:
            # Check confidence threshold
            confidence_score = param.get('confidence', {}).get('score', 0)
            if confidence_score < self.confidence_threshold:
                continue
            
            # Get source (remove .txt extension for folder name)
            source = param.get('source', 'unknown')
            source_name = source.replace('.txt', '')
            
            if source_name not in source_groups:
                source_groups[source_name] = []
            
            source_groups[source_name].append(param)
        
        return source_groups
    
    def _save_source_results(
        self,
        strategy: str,
        source_name: str,
        parameters: List[Dict[str, Any]],
        metadata: Dict[str, Any]
    ):
        """
        Save results for a specific source and strategy.
        
        Args:
            strategy: Prompt strategy name
            source_name: Source file name (without extension)
            parameters: Filtered parameters list
            metadata: Metadata from original YAML
        """
        if not parameters:
            print(f"   No parameters with confidence >= {self.confidence_threshold} for {source_name}")
            return
        
        # Create source directory
        source_dir = self.results_dir / source_name
        source_dir.mkdir(exist_ok=True)
        
        # Prepare output file
        output_file = source_dir / f"{strategy}.yaml"
        
        # Format parameters for output
        formatted_params = []
        for param in parameters:
            formatted_param = {
                'name': param.get('name', ''),
                'description': param.get('description', ''),
                'type': param.get('type', ''),
                'constraints': param.get('constraints', ''),
                'keywords': param.get('keywords', []),
                'confidence_score': param.get('confidence', {}).get('score', 0),
                'confidence_level': param.get('confidence', {}).get('level', ''),
                'model_agreement': param.get('confidence', {}).get('agreement', '')
            }
            formatted_params.append(formatted_param)
        
        # Create output data
        output_data = {
            'metadata': {
                'source_file': f"{source_name}.txt",
                'prompt_strategy': strategy,
                'confidence_threshold': f">= {self.confidence_threshold}",
                'total_parameters': len(formatted_params),
                'extraction_date': metadata.get('extraction_date', ''),
                'models_used': metadata.get('models_used', [])
            },
            'parameters': formatted_params
        }
        
        # Save to YAML
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(output_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        print(f"   Saved {len(formatted_params)} parameters to {source_name}/{strategy}.yaml")


def main():
    """Main entry point."""
    # Get script directory
    script_dir = Path(__file__).parent
    
    # Initialize organizer
    organizer = ResultsOrganizer(
        outputs_dir=script_dir / "outputs",
        results_dir=script_dir / "parameters_majority_confidence"
    )
    
    # Organize all results
    organizer.organize_all_results()


if __name__ == "__main__":
    main()
