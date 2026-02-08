"""
Generate reports from progress file
This script takes a progress JSON file and generates all the final reports
"""

import json
import csv
import sys
from datetime import datetime

def generate_reports_from_progress(progress_file):
    """Generate all reports from a progress JSON file."""
    
    # Load progress data
    with open(progress_file, 'r', encoding='utf-8') as f:
        all_results = json.load(f)
    
    print(f"Loaded results for {len(all_results)} models")
    
    # Extract timestamp from filename
    timestamp = progress_file.split('_')[-1].replace('.json', '')
    
    # Ground truth (same as in main script)
    GROUND_TRUTH = [
        {"snippet": "The number of cycles required to complete a multiplication operation may vary across implementations, and the latency of the MUL instruction may depend on operand width and pipeline structure.", "parameters": ["MUL instruction latency", "Number of execution cycles", "Operand width", "Pipeline structure"]},
        {"snippet": "A processor may include branch prediction hardware to reduce control hazards, and the size and organization of branch history storage may differ between designs.", "parameters": ["Branch prediction support", "Branch history storage size", "Branch history organization"]},
        {"snippet": "A system may include one or more levels of cache, and the total cache capacity may vary across implementations.", "parameters": ["Number of cache levels", "Cache capacity"]},
        {"snippet": "Cache blocks represent contiguous regions of memory, and the size of a cache block may vary depending on the memory hierarchy design.", "parameters": ["Cache block size"]},
        {"snippet": "The translation lookaside buffer may be unified or split between instruction and data accesses, and the number of entries in each case may differ.", "parameters": ["TLB organization", "Instruction TLB entries", "Data TLB entries"]},
        {"snippet": "An implementation may optionally support virtual memory, and the page size and page table depth may vary across systems.", "parameters": ["Virtual memory support", "Page size", "Page table depth"]},
        {"snippet": "The delay between an interrupt request and the execution of its handler may vary, and software should not assume a fixed interrupt response time.", "parameters": ["Interrupt response latency"]},
        {"snippet": "An implementation may support either precise or imprecise exceptions, and the guarantees provided for exception ordering may differ.", "parameters": ["Exception precision", "Exception ordering guarantees"]},
        {"snippet": "Atomic read-modify-write instructions may be supported, and the maximum memory region over which atomicity is guaranteed may vary.", "parameters": ["Atomic instruction support", "Atomicity granularity"]},
        {"snippet": "The memory system may enforce ordering rules stronger than those required by the base ISA, and the exact ordering behavior may vary.", "parameters": ["Memory ordering model", "Ordering guarantees"]},
        {"snippet": "A floating-point unit may optionally be present, and the supported floating-point precisions and rounding modes may differ.", "parameters": ["Floating-point unit presence", "Floating-point precision", "Rounding modes"]},
        {"snippet": "Certain control and status registers may be accessible from multiple privilege modes, and the set of CSRs available at each level may vary.", "parameters": ["CSR accessibility", "Privilege-level access rules"]},
        {"snippet": "The processor may provide low-power operating states, and the number of such states and transition latency may differ between designs.", "parameters": ["Low-power state support", "Number of power states", "Power state transition latency"]},
        {"snippet": "Instruction cache replacement behavior is chosen by the design, and policies such as random or least-recently-used replacement may be employed.", "parameters": ["Instruction cache replacement policy"]},
        {"snippet": "Unaligned memory accesses may be supported, and the performance impact of such accesses may vary across implementations.", "parameters": ["Unaligned access support", "Unaligned access penalty"]},
        {"snippet": "The maximum length of vector registers may vary, and multiple vector lengths may be supported by an implementation.", "parameters": ["Vector register length", "Supported vector lengths"]},
        {"snippet": "Debug mode may be entered through external or internal triggers, and the number of supported hardware breakpoints may differ.", "parameters": ["Debug entry mechanisms", "Number of hardware breakpoints"]},
        {"snippet": "Hardware prefetching may be employed to reduce memory access latency, and the distance and aggressiveness of prefetching may vary.", "parameters": ["Hardware prefetching support", "Prefetch distance", "Prefetch aggressiveness"]},
        {"snippet": "The machine timer provides a monotonically increasing counter, and the frequency and resolution of this counter may vary.", "parameters": ["Timer frequency", "Timer resolution"]},
        {"snippet": "A cache coherency mechanism may be used in systems with multiple agents, and the protocol used to maintain coherency may differ between implementations.", "parameters": ["Cache coherency support", "Cache coherency protocol"]}
    ]
    
    # 1. Generate detailed text report
    txt_filename = f"outputs/parameter_extractions_{timestamp}.txt"
    with open(txt_filename, 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        f.write("PARAMETER EXTRACTION DETAILED REPORT\n")
        f.write("=" * 100 + "\n\n")
        f.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Models Tested: {len(all_results)}\n")
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
            for model, model_data in all_results.items():
                result = model_data["detailed_results"][snippet_idx - 1]
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
    
    print(f"✅ Detailed extractions saved to: {txt_filename}")
    
    # 2. Generate CSV report
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
    
    # 3. Generate summary report
    print(f"\n{'=' * 80}")
    print("SUMMARY REPORT")
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
    
    # Overall statistics
    print(f"\n{'=' * 80}")
    print("OVERALL STATISTICS")
    print('=' * 80)
    
    overall_f1 = sum(s["avg_f1_score"] for s in all_results.values()) / len(all_results)
    overall_precision = sum(s["avg_precision"] for s in all_results.values()) / len(all_results)
    overall_recall = sum(s["avg_recall"] for s in all_results.values()) / len(all_results)
    
    print(f"\nAverage across all {len(all_results)} models:")
    print(f"  Precision: {overall_precision:.2f}%")
    print(f"  Recall: {overall_recall:.2f}%")
    print(f"  F1 Score: {overall_f1:.2f}%")
    
    print(f"\nBest performing model: {sorted_models[0][0]}")
    print(f"  F1 Score: {sorted_models[0][1]['avg_f1_score']}%")
    
    print(f"\n{'=' * 80}")
    print("Reports Generated Successfully!")
    print('=' * 80)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        progress_file = sys.argv[1]
    else:
        # Use the most recent progress file
        progress_file = "outputs/progress_20260208_024545.json"
    
    generate_reports_from_progress(progress_file)
