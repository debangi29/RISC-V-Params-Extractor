import os
import json
import csv
import time
import re
from datetime import datetime
from typing import Dict, List, Tuple
from dotenv import load_dotenv
from model_apis.openrouter_api import OpenRouterAPI
from prompts.prompt_strategies import FewShotPrompt

load_dotenv()

# Ground truth: 20 snippets with their expected parameters
GROUND_TRUTH = [
    {
        "snippet": "The number of cycles required to complete a multiplication operation may vary across implementations, and the latency of the MUL instruction may depend on operand width and pipeline structure.",
        "parameters": ["MUL instruction latency", "Number of execution cycles", "Operand width", "Pipeline structure"]
    },
    {
        "snippet": "A processor may include branch prediction hardware to reduce control hazards, and the size and organization of branch history storage may differ between designs.",
        "parameters": ["Branch prediction support", "Branch history storage size", "Branch history organization"]
    },
    {
        "snippet": "A system may include one or more levels of cache, and the total cache capacity may vary across implementations.",
        "parameters": ["Number of cache levels", "Cache capacity"]
    },
    {
        "snippet": "Cache blocks represent contiguous regions of memory, and the size of a cache block may vary depending on the memory hierarchy design.",
        "parameters": ["Cache block size"]
    },
    {
        "snippet": "The translation lookaside buffer may be unified or split between instruction and data accesses, and the number of entries in each case may differ.",
        "parameters": ["TLB organization", "Instruction TLB entries", "Data TLB entries"]
    },
    {
        "snippet": "An implementation may optionally support virtual memory, and the page size and page table depth may vary across systems.",
        "parameters": ["Virtual memory support", "Page size", "Page table depth"]
    },
    {
        "snippet": "The delay between an interrupt request and the execution of its handler may vary, and software should not assume a fixed interrupt response time.",
        "parameters": ["Interrupt response latency"]
    },
    {
        "snippet": "An implementation may support either precise or imprecise exceptions, and the guarantees provided for exception ordering may differ.",
        "parameters": ["Exception precision", "Exception ordering guarantees"]
    },
    {
        "snippet": "Atomic read-modify-write instructions may be supported, and the maximum memory region over which atomicity is guaranteed may vary.",
        "parameters": ["Atomic instruction support", "Atomicity granularity"]
    },
    {
        "snippet": "The memory system may enforce ordering rules stronger than those required by the base ISA, and the exact ordering behavior may vary.",
        "parameters": ["Memory ordering model", "Ordering guarantees"]
    },
    {
        "snippet": "A floating-point unit may optionally be present, and the supported floating-point precisions and rounding modes may differ.",
        "parameters": ["Floating-point unit presence", "Floating-point precision", "Rounding modes"]
    },
    {
        "snippet": "Certain control and status registers may be accessible from multiple privilege modes, and the set of CSRs available at each level may vary.",
        "parameters": ["CSR accessibility", "Privilege-level access rules"]
    },
    {
        "snippet": "The processor may provide low-power operating states, and the number of such states and transition latency may differ between designs.",
        "parameters": ["Low-power state support", "Number of power states", "Power state transition latency"]
    },
    {
        "snippet": "Instruction cache replacement behavior is chosen by the design, and policies such as random or least-recently-used replacement may be employed.",
        "parameters": ["Instruction cache replacement policy"]
    },
    {
        "snippet": "Unaligned memory accesses may be supported, and the performance impact of such accesses may vary across implementations.",
        "parameters": ["Unaligned access support", "Unaligned access penalty"]
    },
    {
        "snippet": "The maximum length of vector registers may vary, and multiple vector lengths may be supported by an implementation.",
        "parameters": ["Vector register length", "Supported vector lengths"]
    },
    {
        "snippet": "Debug mode may be entered through external or internal triggers, and the number of supported hardware breakpoints may differ.",
        "parameters": ["Debug entry mechanisms", "Number of hardware breakpoints"]
    },
    {
        "snippet": "Hardware prefetching may be employed to reduce memory access latency, and the distance and aggressiveness of prefetching may vary.",
        "parameters": ["Hardware prefetching support", "Prefetch distance", "Prefetch aggressiveness"]
    },
    {
        "snippet": "The machine timer provides a monotonically increasing counter, and the frequency and resolution of this counter may vary.",
        "parameters": ["Timer frequency", "Timer resolution"]
    },
    {
        "snippet": "A cache coherency mechanism may be used in systems with multiple agents, and the protocol used to maintain coherency may differ between implementations.",
        "parameters": ["Cache coherency support", "Cache coherency protocol"]
    }
]

# Select 10 models for testing
TEST_MODELS = [
    "deepseek/deepseek-v3.2",
    "nvidia/nemotron-3-nano-30b-a3b",
    "qwen/qwen3-coder-next",
    "openai/gpt-4o-mini",
    "openai/gpt-5.1-codex-mini",
    "anthropic/claude-3-haiku",
    "google/gemini-3-flash-preview",
    "google/gemini-2.5-flash",
    "meta-llama/llama-3.1-70b-instruct",
    "mistralai/ministral-14b-2512"
]


def normalize_parameter(param: str) -> str:
    """Normalize parameter name for comparison."""
    return param.lower().strip().replace("_", " ").replace("-", " ")


def calculate_accuracy(extracted: List[str], ground_truth: List[str]) -> Dict:
    """
    Calculate accuracy metrics for extracted parameters.
    
    Returns:
        Dict with precision, recall, F1, and matched parameters
    """
    # Normalize all parameters
    extracted_norm = [normalize_parameter(p) for p in extracted]
    truth_norm = [normalize_parameter(p) for p in ground_truth]
    
    # Find matches (exact and partial)
    exact_matches = []
    partial_matches = []
    
    for ext in extracted_norm:
        if ext in truth_norm:
            exact_matches.append(ext)
        else:
            # Check for partial matches (substring)
            for truth in truth_norm:
                if ext in truth or truth in ext:
                    if ext not in partial_matches:
                        partial_matches.append(ext)
                    break
    
    # Calculate metrics
    true_positives = len(exact_matches) + len(partial_matches) * 0.5  # Partial matches count as 0.5
    false_positives = len(extracted_norm) - len(exact_matches) - len(partial_matches)
    false_negatives = len(truth_norm) - len(exact_matches) - len(partial_matches)
    
    precision = true_positives / len(extracted_norm) if extracted_norm else 0
    recall = true_positives / len(truth_norm) if truth_norm else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        "extracted_count": len(extracted),
        "ground_truth_count": len(ground_truth),
        "exact_matches": len(exact_matches),
        "partial_matches": len(partial_matches),
        "precision": round(precision * 100, 2),
        "recall": round(recall * 100, 2),
        "f1_score": round(f1_score * 100, 2),
        "matched_params": exact_matches + partial_matches
    }


def extract_parameters_from_response(response_text: str) -> List[str]:
    """Parse parameter list from model response (YAML format)."""
    try:
        import yaml
        
        # Try to parse as YAML
        # Look for YAML list starting with "- name:"
        params = []
        
        # Try to extract YAML content
        if "- name:" in response_text:
            # Parse YAML
            try:
                parsed = yaml.safe_load(response_text)
                if isinstance(parsed, list):
                    for item in parsed:
                        if isinstance(item, dict) and 'name' in item:
                            params.append(item['name'])
                        elif isinstance(item, str):
                            params.append(item)
                return params
            except:
                pass
        
        # Fallback: Try to extract parameter names using regex
        # Look for "- name: parameter_name" or "name: parameter_name"
        name_pattern = r'(?:^|\n)\s*-?\s*name:\s*([^\n]+)'
        matches = re.findall(name_pattern, response_text, re.MULTILINE)
        if matches:
            return [m.strip() for m in matches]
        
        # Another fallback: Try JSON format
        start_idx = response_text.find('[')
        end_idx = response_text.rfind(']')
        
        if start_idx != -1 and end_idx != -1:
            json_str = response_text[start_idx:end_idx+1]
            params_json = json.loads(json_str)
            if isinstance(params_json, list):
                return [str(p) for p in params_json]
        
        # Last resort: return empty list
        return []
    except Exception as e:
        print(f"    ⚠️  Parse error: {e}")
        return []


def test_model_on_snippet(api: OpenRouterAPI, model: str, snippet_data: Dict, snippet_idx: int) -> Dict:
    """Test a single model on a single snippet."""
    snippet = snippet_data["snippet"]
    ground_truth = snippet_data["parameters"]
    
    print(f"    Snippet {snippet_idx + 1}/20: ", end="", flush=True)
    
    # Generate prompt using few-shot strategy
    prompt = FewShotPrompt.create(snippet)
    
    # Call model
    try:
        response = api.generate(
            model=model,
            prompt=prompt,
            temperature=0.3,
            max_tokens=1000  # Increased for YAML output
        )
        
        if response.get("success"):
            # Extract parameters from response
            extracted_params = extract_parameters_from_response(response.get("text", ""))
            
            # Calculate accuracy
            accuracy = calculate_accuracy(extracted_params, ground_truth)
            
            print(f"✅ F1: {accuracy['f1_score']}%")
            
            return {
                "success": True,
                "extracted": extracted_params,
                "ground_truth": ground_truth,
                "accuracy": accuracy,
                "response_text": response.get("text", "")
            }
        else:
            print(f"❌ API Error: {response.get('error', 'Unknown')}")
            return {
                "success": False,
                "error": response.get("error", "Unknown error"),
                "extracted": [],
                "ground_truth": ground_truth,
                "accuracy": calculate_accuracy([], ground_truth)
            }
    
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "extracted": [],
            "ground_truth": ground_truth,
            "accuracy": calculate_accuracy([], ground_truth)
        }


def test_all_models():
    """Run the complete test suite."""
    print("=" * 80)
    print("RISC-V Parameter Extraction Accuracy Test")
    print("=" * 80)
    print(f"\nTest Configuration:")
    print(f"  - Models: {len(TEST_MODELS)}")
    print(f"  - Snippets: {len(GROUND_TRUTH)}")
    print(f"  - Total tests: {len(TEST_MODELS) * len(GROUND_TRUTH)}")
    print()
    
    # Initialize API
    try:
        api = OpenRouterAPI()
        print(f"✅ OpenRouter API initialized with {len(api.api_keys)} API key(s)")
    except Exception as e:
        print(f"❌ Failed to initialize API: {e}")
        return
    
    # Results storage
    all_results = {}
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Test each model
    for model_idx, model in enumerate(TEST_MODELS, 1):
        print(f"\n{'=' * 80}")
        print(f"Testing Model {model_idx}/{len(TEST_MODELS)}: {model}")
        print('=' * 80)
        
        model_results = []
        
        # Test on all snippets
        for snippet_idx, snippet_data in enumerate(GROUND_TRUTH):
            result = test_model_on_snippet(api, model, snippet_data, snippet_idx)
            model_results.append(result)
            
            # Small delay between requests
            time.sleep(0.5)
        
        # Calculate model-level statistics
        successful_tests = sum(1 for r in model_results if r["success"])
        avg_precision = sum(r["accuracy"]["precision"] for r in model_results) / len(model_results)
        avg_recall = sum(r["accuracy"]["recall"] for r in model_results) / len(model_results)
        avg_f1 = sum(r["accuracy"]["f1_score"] for r in model_results) / len(model_results)
        
        model_summary = {
            "model": model,
            "successful_tests": successful_tests,
            "total_tests": len(GROUND_TRUTH),
            "success_rate": round(successful_tests / len(GROUND_TRUTH) * 100, 2),
            "avg_precision": round(avg_precision, 2),
            "avg_recall": round(avg_recall, 2),
            "avg_f1_score": round(avg_f1, 2),
            "detailed_results": model_results
        }
        
        all_results[model] = model_summary
        
        print(f"\n  Model Summary:")
        print(f"    Success Rate: {model_summary['success_rate']}%")
        print(f"    Avg Precision: {model_summary['avg_precision']}%")
        print(f"    Avg Recall: {model_summary['avg_recall']}%")
        print(f"    Avg F1 Score: {model_summary['avg_f1_score']}%")
        
        # Save incremental progress after each model
        progress_file = f"outputs/progress_{timestamp}.json"
        os.makedirs("outputs", exist_ok=True)
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2)
        print(f"  💾 Progress saved ({len(all_results)}/{len(TEST_MODELS)} models complete)")
    
    # Generate summary report
    print(f"\n{'=' * 80}")
    print("FINAL SUMMARY")
    print('=' * 80)
    
    # Sort models by F1 score
    sorted_models = sorted(all_results.items(), key=lambda x: x[1]["avg_f1_score"], reverse=True)
    
    print(f"\n📊 Model Rankings (by F1 Score):")
    print("-" * 80)
    print(f"{'Rank':<6} {'Model':<45} {'F1':<8} {'Precision':<10} {'Recall':<8}")
    print("-" * 80)
    
    for rank, (model, summary) in enumerate(sorted_models, 1):
        model_short = model.split('/')[-1][:40]
        print(f"{rank:<6} {model_short:<45} {summary['avg_f1_score']:<8}% {summary['avg_precision']:<10}% {summary['avg_recall']:<8}%")
    
    # Save detailed extraction results to text file
    os.makedirs("outputs", exist_ok=True)
    
    # Create detailed text report showing all extracted parameters
    txt_filename = f"outputs/parameter_extractions_{timestamp}.txt"
    with open(txt_filename, 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        f.write("PARAMETER EXTRACTION DETAILED REPORT\n")
        f.write("=" * 100 + "\n\n")
        f.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Models Tested: {len(TEST_MODELS)}\n")
        f.write(f"Snippets Tested: {len(GROUND_TRUTH)}\n\n")
        
        # For each snippet, show all model extractions
        for snippet_idx, snippet_data in enumerate(GROUND_TRUTH, 1):
            f.write("=" * 100 + "\n")
            f.write(f"SNIPPET {snippet_idx}/20\n")
            f.write("=" * 100 + "\n")
            f.write(f"Text: {snippet_data['snippet']}\n\n")
            f.write(f"GROUND TRUTH PARAMETERS ({len(snippet_data['parameters'])}):\n")
            for i, param in enumerate(snippet_data['parameters'], 1):
                f.write(f"  {i}. {param}\n")
            f.write("\n" + "-" * 100 + "\n")
            f.write("MODEL EXTRACTIONS:\n")
            f.write("-" * 100 + "\n\n")
            
            # Show each model's extraction for this snippet
            for model in TEST_MODELS:
                if model in all_results:
                    result = all_results[model]["detailed_results"][snippet_idx - 1]
                    model_short = model.split('/')[-1]
                    
                    f.write(f"📊 {model}\n")
                    if result["success"]:
                        f.write(f"   Extracted {len(result['extracted'])} parameters:\n")
                        if result['extracted']:
                            for i, param in enumerate(result['extracted'], 1):
                                f.write(f"     {i}. {param}\n")
                        else:
                            f.write("     (No parameters extracted)\n")
                        
                        acc = result['accuracy']
                        f.write(f"   Accuracy: Precision={acc['precision']}%, Recall={acc['recall']}%, F1={acc['f1_score']}%\n")
                        f.write(f"   Matches: {acc['exact_matches']} exact, {acc['partial_matches']} partial\n")
                    else:
                        f.write(f"   ❌ FAILED: {result.get('error', 'Unknown error')}\n")
                    f.write("\n")
            
            f.write("\n\n")
    
    print(f"\n✅ Detailed extractions saved to: {txt_filename}")
    
    # Save detailed results to CSV
    csv_filename = f"outputs/parameter_accuracy_test_{timestamp}.csv"
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            "Model", "Model_Short", "Snippet_Index", "Snippet_Text", 
            "Ground_Truth_Count", "Ground_Truth_Params", 
            "Extracted_Count", "Extracted_Params",
            "Exact_Matches", "Partial_Matches",
            "Precision_%", "Recall_%", "F1_Score_%",
            "Success"
        ])
        
        # Data rows
        for model, summary in all_results.items():
            model_short = model.split('/')[-1]
            for idx, result in enumerate(summary["detailed_results"], 1):
                writer.writerow([
                    model,
                    model_short,
                    idx,
                    GROUND_TRUTH[idx-1]["snippet"],
                    len(result["ground_truth"]),
                    " | ".join(result["ground_truth"]),
                    len(result["extracted"]),
                    " | ".join(result["extracted"]) if result["extracted"] else "(none)",
                    result["accuracy"]["exact_matches"],
                    result["accuracy"]["partial_matches"],
                    result["accuracy"]["precision"],
                    result["accuracy"]["recall"],
                    result["accuracy"]["f1_score"],
                    result["success"]
                ])
    
    print(f"✅ Detailed CSV saved to: {csv_filename}")
    
    # Save summary to JSON
    json_filename = f"outputs/parameter_accuracy_summary_{timestamp}.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"✅ Summary JSON saved to: {json_filename}")
    
    # Overall statistics
    print(f"\n{'=' * 80}")
    print("OVERALL STATISTICS")
    print('=' * 80)
    
    overall_f1 = sum(s["avg_f1_score"] for s in all_results.values()) / len(all_results)
    overall_precision = sum(s["avg_precision"] for s in all_results.values()) / len(all_results)
    overall_recall = sum(s["avg_recall"] for s in all_results.values()) / len(all_results)
    
    print(f"\nAverage across all models:")
    print(f"  Precision: {overall_precision:.2f}%")
    print(f"  Recall: {overall_recall:.2f}%")
    print(f"  F1 Score: {overall_f1:.2f}%")
    
    print(f"\nBest performing model: {sorted_models[0][0]}")
    print(f"  F1 Score: {sorted_models[0][1]['avg_f1_score']}%")
    
    print(f"\n{'=' * 80}")
    print("Test Complete!")
    print('=' * 80)


if __name__ == "__main__":
    test_all_models()
