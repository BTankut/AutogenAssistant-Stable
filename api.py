import requests
import time
from typing import Dict, Any
from dotenv import load_dotenv
import os

class OpenRouterAPI:
    def __init__(self, api_key: str):
        # Load environment variables
        load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "http://localhost:8501",
            "X-Title": "AutogenAssistant",
            "Content-Type": "application/json"
        }

    def generate_completion(self, 
                          model: str, 
                          messages: list, 
                          temperature: float = 0.7) -> Dict[str, Any]:
        """
        Generate completion using OpenRouter API
        """
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }

        print(f"Debug - API Request:")
        print(f"URL: {url}")
        print(f"Headers: {self.headers}")
        print(f"Payload: {payload}")

        start_time = time.time()
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            print(f"Debug - API Response:")
            print(f"Status Code: {response.status_code}")
            print(f"Response Text: {response.text}")
            
            response.raise_for_status()
            completion_time = time.time() - start_time
            
            result = response.json()
            if "choices" not in result or not result["choices"]:
                return {
                    "success": False,
                    "error": "Invalid API response: missing choices",
                    "raw_response": result
                }
            if "usage" not in result:
                return {
                    "success": True,
                    "response": result["choices"][0]["message"]["content"],
                    "tokens": 0,
                    "time": completion_time
                }
            return {
                "success": True,
                "response": result["choices"][0]["message"]["content"],
                "tokens": result["usage"]["total_tokens"],
                "time": completion_time
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_models(self) -> Dict[str, Any]:
        """
        Get available models from OpenRouter
        """
        url = f"{self.base_url}/models"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return {
                "success": True,
                "models": response.json()["data"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
