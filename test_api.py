# Create a .env file in this directory with:
# OPENROUTER_API_KEY=your_key_here

import os
import requests
from dotenv import load_dotenv

def test_openrouter_api():
    # .env dosyasını yükle
    print(f"Debug - Working Directory: {os.getcwd()}")
    print(f"Debug - .env file exists: {os.path.exists('.env')}")
    print(f"Debug - .env file path: {os.path.abspath('.env')}")
    print(f"Debug - __file__: {__file__}")
    print(f"Debug - dirname(__file__): {os.path.dirname(__file__)}")
    print(f"Debug - .env path to load: {os.path.join(os.path.dirname(__file__), '.env')}")
    
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    print(f"Debug - .env content before loading:")
    with open(dotenv_path, 'r') as f:
        print(f.read())
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    print(f"Debug - Full API Key: {api_key}")
    
    if not api_key:
        print("Hata: API anahtarı .env dosyasından yüklenemedi!")
        return
    
    print(f"API Key: {'*' * (len(api_key)-8)}{api_key[-8:]}")  # Son 8 karakteri göster
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "AutogenAssistant",
        "Content-Type": "application/json"  # JSON isteği için gerekli
    }
    
    # 1. API Anahtar Durum Kontrolü
    print("\n1. Checking API Key Status...")
    key_status_url = "https://openrouter.ai/api/v1/auth/key"
    try:
        response = requests.get(key_status_url, headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"Key Status: {response.json()}")
        else:
            print(f"Error checking key status: {response.text}")
    except Exception as e:
        print(f"Exception occurred: {str(e)}")

    # 2. Models Endpoint Testi
    print("\n2. Testing Models API...")
    models_url = "https://openrouter.ai/api/v1/models"
    try:
        response = requests.get(models_url, headers=headers)
        print(f"URL: {models_url}")
        print(f"Headers: {headers}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}...")
        print(" Success!" if response.status_code == 200 else " Failed!")
    except Exception as e:
        print(f"Error: {str(e)}")

    # 3. Chat Completions Testi (Ücretsiz Model Kullanımı)
    print("\n3. Testing Chat Completions...")
    chat_url = "https://openrouter.ai/api/v1/chat/completions"
    test_message = {
        "model": "google/gemini-2.0-pro-exp-02-05:free",  # Gemini modeli
        "messages": [{"role": "user", "content": "Say hello"}],
        "temperature": 0.7
    }
    try:
        response = requests.post(chat_url, headers=headers, json=test_message)
        print(f"URL: {chat_url}")
        print(f"Headers: {headers}")
        print(f"Request body: {test_message}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}...")
        print(" Success!" if response.status_code == 200 else " Failed!")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path=dotenv_path)
    test_openrouter_api()