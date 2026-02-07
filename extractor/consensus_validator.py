"""
Consensus Validator
Validates extracted parameters using multi-model consensus.
"""

from typing import Dict, List, Any
from collections import defaultdict, Counter


class ConsensusValidator:
    """
    Validates parameters by comparing outputs from multiple models.
    Uses consensus voting to determine confidence levels.
    """
    
    def __init__(self, confidence_threshold: float = 0.7):
        """
        Initialize consensus validator.
        
        Args:
            confidence_threshold: Minimum confidence for "high" rating (0.0-1.0)
        """
        self.confidence_threshold = confidence_threshold
    
    def validate_parameters(
        self,
        model_outputs: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Validate parameters using consensus across models.
        
        Args:
            model_outputs: Dict mapping model names to their extracted parameters
        
        Returns:
            Dict containing validated parameters and metadata
        """
        # Count total models
        total_models = len(model_outputs)
        
        if total_models == 0:
            return {
                "parameters": [],
                "validation_summary": {
                    "total_parameters": 0,
                    "high_confidence": 0,
                    "medium_confidence": 0,
                    "low_confidence": 0
                }
            }
        
        # Collect all parameter names
        param_names = defaultdict(int)
        param_details = defaultdict(list)
        
        for model_name, params in model_outputs.items():
            for param in params:
                name = param.get("name", "").strip().lower()
                if name:
                    param_names[name] += 1
                    param_details[name].append({
                        "model": model_name,
                        **param
                    })
        
        # Build validated parameters
        validated_params = []
        
        for param_name, count in param_names.items():
            # Calculate confidence
            confidence = count / total_models
            
            # Determine confidence level
            if confidence >= self.confidence_threshold:
                level = "high"
            elif confidence >= 0.5:
                level = "medium"
            else:
                level = "low"
            
            # Merge parameter details
            merged_param = self._merge_parameter_versions(
                param_name,
                param_details[param_name]
            )
            
            # Add confidence info
            merged_param["confidence"] = confidence
            merged_param["confidence_level"] = level
            merged_param["model_agreement"] = f"{count}/{total_models} models"
            
            validated_params.append(merged_param)
        
        # Sort by confidence (highest first)
        validated_params.sort(key=lambda p: p["confidence"], reverse=True)
        
        # Create summary
        summary = {
            "total_parameters": len(validated_params),
            "high_confidence": sum(1 for p in validated_params if p["confidence_level"] == "high"),
            "medium_confidence": sum(1 for p in validated_params if p["confidence_level"] == "medium"),
            "low_confidence": sum(1 for p in validated_params if p["confidence_level"] == "low")
        }
        
        return {
            "parameters": validated_params,
            "validation_summary": summary
        }
    
    def _merge_parameter_versions(
        self,
        param_name: str,
        versions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Merge multiple versions of the same parameter.
        
        Args:
            param_name: Parameter name
            versions: List of parameter dicts from different models
        
        Returns:
            Merged parameter dict
        """
        # Use most common values for each field
        merged = {"name": param_name}
        
        # Collect all descriptions
        descriptions = [v.get("description", "") for v in versions if v.get("description")]
        if descriptions:
            # Use longest description (usually most detailed)
            merged["description"] = max(descriptions, key=len)
        
        # Collect all types
        types = [v.get("type", "") for v in versions if v.get("type")]
        if types:
            # Use most common type
            type_counter = Counter(types)
            merged["type"] = type_counter.most_common(1)[0][0]
        
        # Collect all constraints
        constraints = []
        for v in versions:
            constraint = v.get("constraints")
            if constraint:
                # Convert to string if it's not already a string or list
                if isinstance(constraint, (str, list)):
                    constraints.append(constraint)
                else:
                    # Convert other types (int, float, etc.) to string
                    constraints.append(str(constraint))
        
        if constraints:
            # Use longest constraints
            # For lists, convert to string representation for comparison
            merged["constraints"] = max(constraints, key=lambda x: len(str(x)) if not isinstance(x, str) else len(x))
        
        # Collect all keywords
        all_keywords = []
        for v in versions:
            keywords = v.get("keywords", [])
            if isinstance(keywords, list):
                all_keywords.extend(keywords)
            elif isinstance(keywords, str):
                all_keywords.append(keywords)
        
        if all_keywords:
            # Use unique keywords
            merged["keywords"] = list(set(all_keywords))
        
        return merged
