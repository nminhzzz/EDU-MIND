from app.services.embedding_service import get_embedding


def test_embed():
    print("Testing get_embedding('hello')...")
    try:
        vec = get_embedding("hello")
        print(f"Embedding generated successfully! Vector length: {len(vec)}")
        print(f"First 5 elements: {vec[:5]}")
    except Exception as e:
        print("Error calling get_embedding:")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_embed()
