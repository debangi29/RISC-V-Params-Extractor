"""
RISC-V Parameter Extractor
Main class for extracting architectural parameters using multiple LLMs.
"""

import os
import yaml
import re
from typing import List, Dict, Any, Optional
from pathlib import Path

from model_apis.openrouter_api import OpenRouterAPI
from prompts.prompt_strategies import PromptFactory
from .error_handler import ErrorHandler
from .consensus_validator import ConsensusValidator


class RISCVParamsExtractor:
    """
    Main extractor class that orchestrates parameter extraction
    across multiple models and prompt strategies.
    """
    
    def __init__(
        self,
        models: Optional[List[str]] = None,
        error_handler: Optional[ErrorHandler] = None,
        consensus_validator: Optional[ConsensusValidator] = None
    ):
        """
        Initialize RISC-V parameter extractor.
        
        Args:
            models: List of model identifiers to use (defaults to all OpenRouter models)
            error_handler: Custom error handler (defaults to config-based)
            consensus_validator: Custom consensus validator (defaults to standard)
        """
        # Initialize API client
        self.api = OpenRouterAPI()
        
        # Set models
        self.models = models or self.api.get_available_models()
        
        # Set error handler
        self.error_handler = error_handler or ErrorHandler()
        
        # Set consensus validator
        self.consensus_validator = consensus_validator or ConsensusValidator()
        
        # Available prompt strategies
        self.prompt_strategies = PromptFactory.get_available_strategies()
    
    def extract_from_snippet(
        self,
        snippet: str,
        prompt_strategy: str = "few_shot",
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        Extract parameters from a single snippet using all models.
        
        Args:
            snippet: RISC-V specification text
            prompt_strategy: Prompting strategy to use
            temperature: Sampling temperature for generation
        
        Returns:
            Dict containing results from all models
        """
        # Create prompt
        prompt = PromptFactory.create_prompt(prompt_strategy, snippet)
        
        # Extract with each model
        results = {}
        
        for model in self.models:
            print(f"  Processing with {model}...")
            
            # Call model with error handling
            response = self.error_handler.execute(
                self.api.generate,
                model=model,
                prompt=prompt,
                temperature=temperature
            )
            
            if response.get("success"):
                # Parse YAML response
                params = self._parse_yaml_response(response.get("text", ""))
                results[model] = {
                    "success": True,
                    "parameters": params,
                    "raw_text": response.get("text", "")
                }
            else:
                results[model] = {
                    "success": False,
                    "error": response.get("error", "Unknown error"),
                    "parameters": []
                }
        
        return results
    
    def extract_from_file(
        self,
        file_path: str,
        prompt_strategy: str = "few_shot"
    ) -> Dict[str, Any]:
        """
        Extract parameters from a text file.
        
        Args:
            file_path: Path to snippet file
            prompt_strategy: Prompting strategy to use
        
        Returns:
            Dict containing extraction results
        """
        # Read snippet
        with open(file_path, 'r', encoding='utf-8') as f:
            snippet = f.read()
        
        # Extract parameters
        return self.extract_from_snippet(snippet, prompt_strategy)
    
    def extract_from_directory(
        self,
        directory: str,
        prompt_strategy: str = "few_shot"
    ) -> Dict[str, Dict[str, Any]]:
        """
        Extract parameters from all .txt files in a directory.
        
        Args:
            directory: Path to directory containing snippet files
            prompt_strategy: Prompting strategy to use
        
        Returns:
            Dict mapping file names to extraction results
        """
        results = {}
        
        # Find all .txt files
        snippet_files = list(Path(directory).glob("*.txt"))
        
        print(f"Found {len(snippet_files)} snippet files")
        
        for file_path in snippet_files:
            print(f"\nProcessing {file_path.name}...")
            results[file_path.name] = self.extract_from_file(
                str(file_path),
                prompt_strategy
            )
        
        return results
    
    def validate_and_merge(
        self,
        extraction_results: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate and merge results using consensus.
        
        Args:
            extraction_results: Results from extract_from_directory
        
        Returns:
            Validated and merged parameters
        """
        all_validated = {}
        
        for snippet_name, model_results in extraction_results.items():
            # Extract just the parameters from each model
            model_params = {}
            for model_name, result in model_results.items():
                if result.get("success"):
                    model_params[model_name] = result.get("parameters", [])
                else:
                    model_params[model_name] = []
            
            # Validate using consensus
            validated = self.consensus_validator.validate_parameters(model_params)
            validated["source_snippet"] = snippet_name
            
            all_validated[snippet_name] = validated
        
        return all_validated
    
    def _parse_yaml_response(self, text: str) -> List[Dict[str, Any]]:
        """
        Parse YAML from model response.
        
        Args:
            text: Model response text
        
        Returns:
            List of parameter dictionaries
        """
        try:
            # Try to extract YAML block
            yaml_match = re.search(r'```ya?ml\s*(.*?)\s*```', text, re.DOTALL)
            if yaml_match:
                yaml_text = yaml_match.group(1)
            else:
                # Try to find YAML-like content
                lines = text.split('\n')
                yaml_lines = []
                in_yaml = False
                
                for line in lines:
                    if line.strip().startswith('- name:'):
                        in_yaml = True
                    if in_yaml:
                        yaml_lines.append(line)
                
                yaml_text = '\n'.join(yaml_lines) if yaml_lines else text
            
            # Parse YAML
            parsed = yaml.safe_load(yaml_text)
            
            if isinstance(parsed, list):
                return parsed
            elif isinstance(parsed, dict):
                return [parsed]
            else:
                return []
                
        except Exception as e:
            print(f"    Warning: Failed to parse YAML: {e}")
            return []
    
    def get_model_info(self) -> List[Dict[str, str]]:
        """
        Get information about models being used.
        
        Returns:
            List of model info dictionaries
        """
        model_info = []
        
        for model in self.models:
            # Parse provider and model name
            if '/' in model:
                provider, model_name = model.split('/', 1)
            else:
                provider = "unknown"
                model_name = model
            
            model_info.append({
                "full_name": model,
                "provider": provider,
                "model": model_name,
                "access_method": "OpenRouter API"
            })
        
        return model_info
