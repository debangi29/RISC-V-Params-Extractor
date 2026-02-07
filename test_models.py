"""
Test Script for All LLM Models
Tests each model individually to verify API connectivity and response.
"""

import os
import sys
from dotenv import load_dotenv
from model_apis.openrouter_api import OpenRouterAPI

load_dotenv()

def test_single_model(api, model_name):
    """Test a single model with a simple prompt."""
    print(f"\n{'='*60}")
    print(f"Testing: {model_name}")
    print('='*60)
    
    # Simple test prompt
    test_prompt = """Extract parameters from this text:

The cache block size is implementation-defined. Systems may use blocks from 32 to 128 bytes.

Output as YAML:
- name: parameter_name
  description: what it does
  type: implementation-defined
  keywords: [may, implementation-defined]
"""
    
    try:
        print("Sending request...")
        response = api.generate(
            model=model_name,
            prompt=test_prompt,
            temperature=0.3,
            max_tokens=500
        )
        
        if response.get("success"):
            print("✅ SUCCESS")
            print(f"Response length: {len(response.get('text', ''))} characters")
            print(f"\nFirst 200 chars of response:")
            print("-" * 60)
            print(response.get('text', '')[:200])
            print("-" * 60)
            
            # Check usage if available
            usage = response.get('usage', {})
            if usage:
                print(f"\nTokens used: {usage}")
            
            return True
        else:
            print("❌ FAILED")
            print(f"Error: {response.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print("❌ EXCEPTION")
        print(f"Error: {str(e)}")
        return False


def main():
    """Test all models."""
    print("="*60)
    print("RISC-V Parameter Extractor - Model Test Suite")
    print("="*60)
    
    # Check API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("\n❌ ERROR: OPENROUTER_API_KEY not found in .env file")
        print("Please add your API key to the .env file")
        sys.exit(1)
    
    print(f"\n✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    # Initialize API
    try:
        api = OpenRouterAPI()
        print("✅ OpenRouter API initialized")
    except Exception as e:
        print(f"❌ Failed to initialize API: {e}")
        sys.exit(1)
    
    # Get all models
    models = api.get_available_models()
    print(f"\n📋 Testing {len(models)} models:")
    for i, model in enumerate(models, 1):
        print(f"  {i}. {model}")
    
    # Test each model
    results = {}
    
    for model in models:
        success = test_single_model(api, model)
        results[model] = success
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    successful = sum(1 for v in results.values() if v)
    failed = len(results) - successful
    
    print(f"\n✅ Successful: {successful}/{len(results)}")
    print(f"❌ Failed: {failed}/{len(results)}")
    
    print("\nDetailed Results:")
    print("-" * 60)
    
    # Group by provider
    providers = {}
    for model, success in results.items():
        provider = model.split('/')[0]
        if provider not in providers:
            providers[provider] = []
        providers[provider].append((model, success))
    
    for provider, model_results in sorted(providers.items()):
        print(f"\n{provider.upper()}:")
        for model, success in model_results:
            status = "✅" if success else "❌"
            print(f"  {status} {model}")
    
    # Specific Anthropic check
    print("\n" + "="*60)
    print("ANTHROPIC MODELS CHECK")
    print("="*60)
    
    anthropic_models = [m for m in models if m.startswith('anthropic/')]
    anthropic_success = [results[m] for m in anthropic_models]
    
    if all(anthropic_success):
        print("✅ All Anthropic models working correctly!")
    elif any(anthropic_success):
        print("⚠️  Some Anthropic models working, some failing")
    else:
        print("❌ All Anthropic models failed")
    
    for model in anthropic_models:
        status = "✅" if results[model] else "❌"
        print(f"  {status} {model}")
    
    print("\n" + "="*60)
    
    if failed > 0:
        print("\n⚠️  Some models failed. This could be due to:")
        print("  - Rate limiting")
        print("  - API key permissions")
        print("  - Temporary service issues")
        print("  - Network connectivity")
        print("\nTry running the test again in a few minutes.")
    else:
        print("\n🎉 All models are working correctly!")


if __name__ == "__main__":
    main()
