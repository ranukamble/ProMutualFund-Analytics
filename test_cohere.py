import os
import requests

api_key = os.getenv('COHERE_API_KEY', '')
prompt = "Hello"

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

models = ['command-r', 'command-light', 'command-nightly', 'command-r-08-2024']

for model in models:
    payload = {
        'model': model,
        'message': prompt,
        'temperature': 0.1
    }
    resp = requests.post('https://api.cohere.com/v1/chat', headers=headers, json=payload)
    print(f"Model {model}: {resp.status_code}")
    if resp.status_code == 200:
        print("SUCCESS")
        break
    else:
        print(resp.text)
