import requests
import json

# Configuration
API_KEY = "sk-Sewi-UGdpPaihexBlXzTkA"  # Replace with your actual API key

# Make a request to CoGenAI (OpenAI compatible API)
response = requests.post(
    "https://api.cogenai.kalavai.net/v1/audio/speech",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={
        "model": "hexgrad-kokoro-82m",
        "input": "The fox and the rock",
        "voice": "af"
    }
)

# Check the response
if response.status_code == 200:
    with open("output.wav", "wb") as f:
        f.write(response.content)
    print("Audio file saved as output.wav")
else:
    print(f"Error: {response.status_code} - {response.text}")