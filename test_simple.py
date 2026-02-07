"""
Simple Model Test - Direct API Test
Tests OpenRouter API without importing other packages.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_model(model_name):
    """Test a single model via OpenRouter."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        print("❌ No API key found")
        return False
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": "Extract parameters from: The cache size is implementation-defined. Output as YAML list."}
        ],
        "temperature": 0.3,
        "max_tokens": 300
    }
    
    try:
        print(f"Testing {model_name}...", end=" ")
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        text = data["choices"][0]["message"]["content"]
        
        print(f"✅ OK ({len(text)} chars)")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)[:50]}")
        return False


def main():
    print("="*60)
    print("Quick Model Test")
    print("="*60)
    
    # Test Anthropic models specifically
    anthropic_models = [
        "anthropic/claude-3.5-sonnet",
        "anthropic/claude-3-opus",
        "anthropic/claude-3-haiku"
    ]
    
    # Test other models
    other_models = [
        "openai/gpt-4o-mini",
        "google/gemini-flash-1.5",
        "meta-llama/llama-3.1-70b-instruct"
    ]
    
    print("\n🔍 Testing ANTHROPIC models:")
    print("-" * 60)
    anthropic_results = {}
    for model in anthropic_models:
        anthropic_results[model] = test_model(model)
    
    print("\n🔍 Testing OTHER models:")
    print("-" * 60)
    other_results = {}
    for model in other_models:
        other_results[model] = test_model(model)
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    anthropic_success = sum(anthropic_results.values())
    other_success = sum(other_results.values())
    
    print(f"\nAnthropic: {anthropic_success}/{len(anthropic_models)} working")
    print(f"Others: {other_success}/{len(other_models)} working")
    
    if anthropic_success == len(anthropic_models):
        print("\n✅ All Anthropic models are WORKING!")
    else:
        print("\n❌ Some Anthropic models failed")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
