# test_vector_store.py
import requests
import json

def test_vector_store():
    """Test if the vector store has documents and can search"""
    
    # Check system status
    print("🔍 Checking system status...")
    try:
        status_response = requests.get("http://localhost:8000/admin/status")
        status_data = status_response.json()
        print(f"📊 Vector store status: {status_data}")
        
        doc_count = status_data.get('vector_store', {}).get('document_count', 0)
        print(f"📄 Documents in vector store: {doc_count}")
        
    except Exception as e:
        print(f"❌ Status check failed: {e}")
        return
    
    # Test search with different questions
    test_questions = [
        "What suppliers are available?",
        "Tell me about companies in the database",
        "Find electronics suppliers",
        "Show me manufacturing companies"
    ]
    
    for question in test_questions:
        print(f"\n🧪 Testing: '{question}'")
        try:
            response = requests.get(
                "http://localhost:8000/ask",
                params={"question": question},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Answer: {result['answer'][:150]}...")
                print(f"📚 Sources: {result['sources']}")
                print(f"⏱️ Time: {result['processing_time']}s")
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                
        except requests.exceptions.Timeout:
            print("❌ Request timeout - vector store might be processing")
        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_vector_store()