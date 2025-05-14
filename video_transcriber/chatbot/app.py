import streamlit as st
import requests
from video_utils import download_youtube_video

# Initialize session state variables
if 'api_base_url' not in st.session_state:
    st.session_state.api_base_url = ''
if 'api_key' not in st.session_state:
    st.session_state.api_key = ''
if 'model_id' not in st.session_state:
    st.session_state.model_id = ''
if 'video_filename' not in st.session_state:
    st.session_state.video_filename = None
if 'audio_filename' not in st.session_state:
    st.session_state.audio_filename = None


# Function to fetch available models from the OpenAI-compatible API
def fetch_models(api_base_url, api_key):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    response = requests.get(f'{api_base_url}/models', headers=headers)
    return response.json().get('data', [])

# Function to send a message to the OpenAI-compatible API
def send_message(message, api_base_url, model_id):
    headers = {
        'Authorization': f'Bearer {st.session_state.api_key}',
        'Content-Type': 'application/json'
    }
    data = {
        'model': model_id,
        'messages': st.session_state.messages
    }
    response = requests.post(f'{api_base_url}/chat/completions', headers=headers, json=data)
    return response.json()

def speech_to_text(filename):
    headers = {
        'Authorization': f'Bearer {st.session_state.api_key}',
        'Content-Type': 'application/json'
    }
    audio_file= open(filename, "rb")

    # Make a request to CoGenAI (OpenAI compatible API)
    response = requests.post(
        "https://api.cogenai.kalavai.net/v1/audio/transcriptions",
        headers=headers,
        data={
            "model": "tiny-en"
        },
        files={
            "file": audio_file
        }
    )
    print(response.text)
    return response.json()

def video_to_text(video_filename, question):
    headers = {
        'Authorization': f'Bearer {st.session_state.api_key}',
        'Content-Type': 'application/json'
    }
    from pathlib import Path
    import base64
    video_bytes = Path(video_filename).read_bytes()
    encoded_data = base64.b64encode(video_bytes).decode("utf-8")
    response = requests.post(
        f"{st.session_state.api_base_url}/chat/completions",
        headers=headers,
        json={
            "model": "qwen-qwen2-5-vl-3b-instruct-awq",
            "messages":[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": question},
                    {"type": "video_url", "video_url": {"url": f"data:video/mp4;base64,{encoded_data}"}}
                    #{"type": "video_url", "video_url": {"url": f"data:video/mp4;base64,{encoded_data}"}}
                ]
            }],
            "max_tokens": 1000
        }
    )
    print(response.text)
    return response.json()["choices"][0]["message"]["content"]


# Streamlit UI
st.title("Ask YouTube")

# Input fields for API settings
with st.sidebar:
    st.session_state.api_base_url = st.text_input("API Base URL", value=st.session_state.api_base_url)
    st.session_state.api_key = st.text_input("API Key", value=st.session_state.api_key, type="password")
    if 'models' not in st.session_state:
        st.session_state.models = []
    
    if not st.session_state.models:
        if st.session_state.api_base_url and st.session_state.api_key:
            st.session_state.models = fetch_models(st.session_state.api_base_url, st.session_state.api_key)
    
    if st.session_state.models:
        st.session_state.model_id = st.selectbox("Model ID", [model['id'] for model in st.session_state.models], index=0)
    else:
        st.session_state.model_id = st.text_input("Model ID", value=st.session_state.model_id)

uploaded_video = st.file_uploader(
    "Upload an MP4 video file",
    type=["mp4"]
)
if uploaded_video:
    st.session_state.video_filename = uploaded_video.name
    with open(st.session_state.video_filename, "wb") as f:
        f.write(uploaded_video.getbuffer())

if st.session_state.video_filename is not None:
    st.video(st.session_state.video_filename)

# Chat message container
if 'messages' not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg['role']).container().markdown(msg['content'])

# User input field
text = st.chat_input()
if text:
    st.chat_message("user").container().markdown(text)

    response = video_to_text(
        video_filename=st.session_state.video_filename,
        question=text)
    st.chat_message("assistant").container().markdown(
        response
    )

# if user_input:
    # st.session_state.messages.append({"role": "user", "content": user_input})
    # response = send_message(user_input, st.session_state.api_base_url, st.session_state.api_key, st.session_state.model_id)
    # assistant_response = response['choices'][0]['message']['content']
    # st.session_state.messages.append({"role": "assistant", "content": assistant_response})

    # # Display the assistant's response
    # st.chat_message("assistant").container().markdown(response['choices'][0]['message']['content'])