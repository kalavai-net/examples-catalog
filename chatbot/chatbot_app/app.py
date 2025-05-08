import requests

class ChatbotAPI:
    def __init__(self, api_base_url, api_key, model_id=None):
        self.api_base_url = api_base_url
        self.api_key = api_key
        self.model_id = model_id

    def send_message(self, message):
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            'model': self.model_id,
            'messages': [{'role': 'user', 'content': message}]
        }
        response = requests.post(f'{self.api_base_url}/v1/chat/completions', headers=headers, json=data)
        return response.json()

    def get_available_models(self):
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        response = requests.get(f'{self.api_base_url}/v1/models', headers=headers)
        if response.status_code == 200:
            models = response.json().get('data', [])
            return [model['id'] for model in models]
        else:
            raise Exception(f"Failed to fetch models: {response.status_code} - {response.text}")