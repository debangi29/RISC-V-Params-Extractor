"""
CSV Generator
Creates CSV files for snippets inventory, model comparison, and detailed results.
"""

import csv
from pathlib import Path
from typing import Dict, List, Any


class CSVGenerator:
    """Utility class for generating CSV output files."""
    
    @staticmethod
    def create_snippets_csv(snippets_dir: str, output_path: str):
        """
        Create CSV inventory of snippet files.
        
        Args:
            snippets_dir: Directory containing snippet files
            output_path: Path for output CSV
        """
        snippet_files = list(Path(snippets_dir).glob("*.txt"))
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Filename", "Path", "Size (bytes)"])
            
            for file_path in snippet_files:
                writer.writerow([
                    file_path.name,
                    str(file_path),
                    file_path.stat().st_size
                ])
        
        print(f"Created snippets CSV: {output_path}")
    
    @staticmethod
    def create_comparison_csv(
        extraction_results: Dict[str, Dict[str, Any]],
        output_path: str
    ):
        """
        Create CSV comparing model outputs.
        
        Args:
            extraction_results: Results from extract_from_directory
            output_path: Path for output CSV
        """
        # Get all models from first snippet
        first_snippet = next(iter(extraction_results.values()))
        models = list(first_snippet.keys())
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            header = ["Snippet"] + models
            writer.writerow(header)
            
            # Data rows
            for snippet_name, model_results in extraction_results.items():
                row = [snippet_name]
                
                for model in models:
                    result = model_results.get(model, {})
                    if result.get("success"):
                        param_count = len(result.get("parameters", []))
                        row.append(f"{param_count} parameters")
                    else:
                        row.append(f"Error: {result.get('error', 'Unknown')}")
                
                writer.writerow(row)
        
        print(f"Created comparison CSV: {output_path}")
    
    @staticmethod
    def create_detailed_csv(
        validated_results: Dict[str, Any],
        output_path: str
    ):
        """
        Create detailed CSV with all parameters and confidence scores.
        
        Args:
            validated_results: Results from validate_and_merge
            output_path: Path for output CSV
        """
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                "Source Snippet",
                "Parameter Name",
                "Description",
                "Type",
                "Constraints",
                "Keywords",
                "Confidence Score",
                "Confidence Level",
                "Model Agreement"
            ])
            
            # Data rows
            for snippet_name, validation in validated_results.items():
                params = validation.get("parameters", [])
                
                for param in params:
                    # Safely handle keywords - convert all to strings
                    keywords = param.get("keywords", [])
                    if isinstance(keywords, list):
                        # Convert all items to strings (handles mixed types from malformed YAML)
                        keywords_str = ", ".join(str(k) for k in keywords)
                    else:
                        # Handle case where keywords is not a list
                        keywords_str = str(keywords) if keywords else ""
                    
                    writer.writerow([
                        snippet_name,
                        param.get("name", ""),
                        param.get("description", ""),
                        param.get("type", ""),
                        param.get("constraints", ""),
                        keywords_str,
                        f"{param.get('confidence', 0):.2f}",
                        param.get("confidence_level", ""),
                        param.get("model_agreement", "")
                    ])
        
        print(f"Created detailed CSV: {output_path}")
