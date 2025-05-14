import requests
import json

# Configuration
API_KEY = "sk-Sewi-UGdpPaihexBlXzTkA"  # Replace with your actual API key
URL = "https://api.cogenai.kalavai.net"
MODEL_ID = "qwen-qwen2-5-vl-7b-instruct-awq" # "qwen-qwen2-5-vl-3b-instruct" # "damo-nlp-sg-videollama3-7b"

# Make a request to CoGenAI (OpenAI compatible API)
response = requests.post(
    f"{URL}/v1/chat/completions",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={
        "model": MODEL_ID,
        "messages":[
        {
    	    "role": "user",
            "content": [
                {"type": "text", "text": "Summarize the following video"},
                {"type": "video_url", "video_url": {"url": "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen2-VL/space_woaudio.mp4"}}
                #{"type": "video", "video": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}
            ]
        }],
        "max_tokens": 1000
    }
).json()

print(
    json.dumps(response, indent=2)
) 