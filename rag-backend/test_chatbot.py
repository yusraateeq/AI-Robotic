import requests
import json

# Test the chatbot API
def test_chatbot():
    url = "http://localhost:8001/api/chat/query"  # Using port 8001

    # Example query
    query_data = {
        "query": "What is the main topic of the textbook?",
        "top_k": 3  # Number of relevant chunks to retrieve
    }

    try:
        response = requests.post(url, json=query_data)

        if response.status_code == 200:
            result = response.json()
            print("✅ Chatbot API is working!")
            print(f"Response: {result['response']}")
            print(f"Sources: {len(result['sources'])} sources found")
            print(f"Session ID: {result['session_id']}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Make sure the server is running on http://localhost:8001")
        print("Try running: uvicorn main:app --reload --port 8001")
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        print("Make sure the server is running on http://localhost:8001")

if __name__ == "__main__":
    test_chatbot()