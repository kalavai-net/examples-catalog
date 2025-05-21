import os

import time
import streamlit as st
import requests
from video_utils import download_youtube_video

SLEEP_BETWEEN_REQUESTS = 5

# Initialize session state variables
if 'api_base_url' not in st.session_state:
    st.session_state.api_base_url = 'https://api.cogenai.kalavai.net'
if 'api_key' not in st.session_state:
    st.session_state.api_key = ''
if 'vl_model' not in st.session_state:
    st.session_state.vl_model = ''
if 'stt_model' not in st.session_state:
    st.session_state.stt_model = ''
if 'brain_model' not in st.session_state:
    st.session_state.brain_model = ''
if 'video_filename' not in st.session_state:
    st.session_state.video_filename = None
if 'audio_filename' not in st.session_state:
    st.session_state.audio_filename = None


# Function to fetch available models from the OpenAI-compatible API
def fetch_models():
    headers = {
        'Authorization': f'Bearer {st.session_state.api_key}',
        'Content-Type': 'application/json'
    }
    response = requests.get(f'{st.session_state.api_base_url}/models', headers=headers)
    return response.json().get('data', [])

# Function to send a message to the OpenAI-compatible API
def send_message(message):
    headers = {
        'Authorization': f'Bearer {st.session_state.api_key}',
        'Content-Type': 'application/json'
    }
    data = {
        'model': st.session_state.brain_model,
        'messages': [
            {
                "role": "user",
                "content": message
            }
        ]
    }
    response = requests.post(f'{st.session_state.api_base_url}/v1/chat/completions', headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"]

def speech_to_text(filename):

    headers = {
        'Authorization': f'Bearer {st.session_state.api_key}'
    }
    with open(filename, "rb") as f:
        files = {
            "file": (filename, f, "audio/mpeg")
        }
        response = requests.post(
            f"{st.session_state.api_base_url}/v1/audio/transcriptions",
            headers=headers,
            data={
                "model": st.session_state.stt_model
            },
            files=files
        )
        response.raise_for_status()
        return response.json()["text"]

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
        f"{st.session_state.api_base_url}/v1/chat/completions",
        headers=headers,
        json={
            "model": "qwen-qwen2-5-vl-7b-instruct-awq",
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
            st.session_state.models = fetch_models()
    
    if st.session_state.models:
        st.session_state.vl_model = st.selectbox("Video", [model['id'] for model in st.session_state.models], index=0)
        st.session_state.stt_model = st.selectbox("Speech-to-Text", [model['id'] for model in st.session_state.models], index=0)
        st.session_state.brain_model = st.selectbox("Brain", [model['id'] for model in st.session_state.models], index=0)
    else:
        st.session_state.vl_model = st.text_input("Video", value=st.session_state.vl_model)
        st.session_state.stt_model = st.text_input("Speech-to-Text", value=st.session_state.stt_model)
        st.session_state.brain_model = st.text_input("Brain", value=st.session_state.brain_model)


video_url = st.text_input("YouTube URL")
if st.button("Pre-process video"):
    st.session_state.video_filename = download_youtube_video(
        video_url=video_url,
        download_video_only=True
    )
    st.session_state.audio_filename = download_youtube_video(
        video_url=video_url,
        download_audio_only=True
    )
    st.balloons()

if st.session_state.video_filename is not None:
    st.video(st.session_state.video_filename)
if st.session_state.audio_filename is not None:
    st.audio(st.session_state.audio_filename)

# Chat message container
if 'messages' not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg['role']).container().markdown(msg['content'])

# User input field
text = st.chat_input()
if text:
    st.chat_message("user").container().markdown(text)

    # generate transcript
    audio_transcript = speech_to_text(st.session_state.audio_filename)
    st.chat_message("audio").container().markdown(audio_transcript)
    time.sleep(SLEEP_BETWEEN_REQUESTS)

    video_transcription = video_to_text(
        video_filename=st.session_state.video_filename,
        question="Describe in detail what is happening in the video")
    st.chat_message("video").container().markdown(
        video_transcription
    )
    time.sleep(SLEEP_BETWEEN_REQUESTS)
    
    prompt=f"""You are an assistant that knows how to understand videos and answer questions about them. 
    
        Here is the audio transcription:
        {audio_transcript}
        ---
        Here's the description of the images in the video:
        {video_transcription}.

        Given the audio and video transcriptions, answer the following question from the user: {text}
        """
    response = send_message(
        message=prompt
    )
    print(
        "************* PROMPT ***************",
        prompt
    )
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