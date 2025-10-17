# test_rag.py
import requests
import json

def test_rag_system():
    """Test the RAG system with a sample question"""
    
    # Test question about suppliers
    test_questions = [
        "What suppliers do you recommend for electronics?",
        "Tell me about available suppliers",
        "What companies are in the database?"
    ]
    
    for question in test_questions:
        try:
            print(f"\n🧪 Testing question: '{question}'")
            response = requests.get(
                "http://localhost:8000/ask",
                params={"question": question}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success!")
                print(f"Answer: {result['answer'][:200]}...")
                print(f"Sources: {result['sources']}")
                print(f"Processing time: {result['processing_time']}s")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")

def test_system_status():
    """Test the system status endpoint"""
    try:
        response = requests.get("http://localhost:8000/admin/status")
        print(f"\n📊 System Status:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"❌ Status check failed: {e}")

if __name__ == "__main__":
    test_system_status()
    test_rag_system()