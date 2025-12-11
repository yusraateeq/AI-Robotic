import requests
import json

payload = {"query": "What is a digital twin?", "top_k": 3}
try:
    resp = requests.post("http://127.0.0.1:8000/api/chat/query", json=payload, timeout=60)
    print("HTTP_STATUS:", resp.status_code)
    try:
        print(json.dumps(resp.json(), indent=2))
    except Exception:
        print(resp.text)
except Exception as e:
    print("Request failed:", str(e))
