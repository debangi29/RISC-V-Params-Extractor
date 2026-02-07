"""
YAML Generator
Creates structured YAML output files with parameters and metadata.
"""

import yaml
from datetime import datetime
from typing import Dict, List, Any


class YAMLGenerator:
    """Utility class for generating YAML output files."""
    
    @staticmethod
    def create_parameters_yaml(
        validated_results: Dict[str, Any],
        model_info: List[Dict[str, str]],
        output_path: str,
        prompt_strategy: str = "few_shot"
    ):
        """
        Create YAML file with validated parameters.
        
        Args:
            validated_results: Results from validate_and_merge
            model_info: Information about models used
            output_path: Path for output YAML
            prompt_strategy: Prompt strategy used
        """
        # Build YAML structure
        yaml_data = {
            "metadata": {
                "extraction_date": datetime.now().isoformat(),
                "prompt_strategy": prompt_strategy,
                "models_used": model_info,
                "total_snippets": len(validated_results)
            },
            "parameters": []
        }
        
        # Add parameters from all snippets
        for snippet_name, validation in validated_results.items():
            params = validation.get("parameters", [])
            
            for param in params:
                yaml_param = {
                    "name": param.get("name", ""),
                    "description": param.get("description", ""),
                    "type": param.get("type", ""),
                    "constraints": param.get("constraints", ""),
                    "source": snippet_name,
                    "keywords": param.get("keywords", []),
                    "confidence": {
                        "score": round(param.get("confidence", 0), 2),
                        "level": param.get("confidence_level", ""),
                        "agreement": param.get("model_agreement", "")
                    }
                }
                
                yaml_data["parameters"].append(yaml_param)
        
        # Write YAML file
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(
                yaml_data,
                f,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True
            )
        
        print(f"Created parameters YAML: {output_path}")
        print(f"  Total parameters: {len(yaml_data['parameters'])}")
