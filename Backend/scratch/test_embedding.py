import os
from openai import OpenAI

def test_embedding():
    api_key = "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"
    client = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=api_key
    )
    
    # Model in settings or config is "nvidia/nv-embed-v1"
    model = "nvidia/nv-embed-v1"
    
    print(f"Calling NVIDIA NIM Embeddings with model {model}...")
    try:
        response = client.embeddings.create(
            input=["Triết học Mác - Lênin"],
            model=model
        )
        emb = response.data[0].embedding
        print("Success! Embedding dimensions:", len(emb))
        print("First 5 values:", emb[:5])
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_embedding()
