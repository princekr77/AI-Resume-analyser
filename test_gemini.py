import requests

# Paste your API key here for testing
API_KEY = "AIzaSyCYfjP7vmihuxI4XAuX4-tyT7S2S8yiO5o"  # Replace with your actual key

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"

try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ API Key is VALID!")
        print("Available models:")
        models = response.json().get('models', [])
        for model in models[:5]:
            print(f"  - {model.get('name')}")
    else:
        print(f"❌ API Key is INVALID")
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {e}")