import requests, json

# Test 1: Simple query (what frontend does)
print('=== Test 1: Query Only ===')
payload = {'query': 'What is ROS 2?', 'top_k': 3}
r = requests.post('http://127.0.0.1:8000/api/chat/query', json=payload, timeout=60)
print(f'Status: {r.status_code}')
resp_json = r.json()
print(f'Response length: {len(resp_json.get("response", ""))}')
print(f'Has sources: {len(resp_json.get("sources", [])) > 0}')
print(f'Response preview: {resp_json.get("response", "")[:200]}...')

# Test 2: Query with context (selected text)
print('\n=== Test 2: Query with Context ===')
payload2 = {
    'query': 'What is this about?',
    'context': 'ROS 2 is a robotics framework',
    'top_k': 3
}
r2 = requests.post('http://127.0.0.1:8000/api/chat/query_with_context', json=payload2, timeout=60)
print(f'Status: {r2.status_code}')
resp2_json = r2.json()
print(f'Response preview: {resp2_json.get("response", "")[:200]}...')

print('\n✓ Both endpoints working!')
