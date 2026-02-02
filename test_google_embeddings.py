"""Test script to verify Google Generative AI embedding models"""
import google.generativeai as genai
import os

# Configure with API key
api_key = "AIzaSyDXRyikUoc-kARYvhATy62vq_bgBHUE15g"
if not api_key:
    print("ERROR: GOOGLE_API_KEY environment variable not set")
    exit(1)

genai.configure(api_key=api_key)

print("Listing all available models that support embedContent:\n")
for model in genai.list_models():
    if 'embedContent' in model.supported_generation_methods:
        print(f"✓ {model.name}")
        print(f"  Description: {model.description}")
        print()

print("\n" + "="*60)
print("Testing embedding with text-embedding-004:")
print("="*60)
try:
    result = genai.embed_content(
        model="models/text-embedding-004",
        content="This is a test",
        task_type="retrieval_document"
    )
    print(f"✓ SUCCESS: Generated embedding with {len(result['embedding'])} dimensions")
except Exception as e:
    print(f"✗ FAILED: {e}")

print("\n" + "="*60)
print("Testing embedding with embedding-001:")
print("="*60)
try:
    result = genai.embed_content(
        model="models/embedding-001",
        content="This is a test",
        task_type="retrieval_document"
    )
    print(f"✓ SUCCESS: Generated embedding with {len(result['embedding'])} dimensions")
except Exception as e:
    print(f"✗ FAILED: {e}")
