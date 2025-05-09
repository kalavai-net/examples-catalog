import streamlit as st
import requests

# Initialize session state variables
if 'api_base_url' not in st.session_state:
    st.session_state.api_base_url = ''
if 'api_key' not in st.session_state:
    st.session_state.api_key = ''
if 'model_id' not in st.session_state:
    st.session_state.model_id = ''

# Function to fetch available models from the OpenAI-compatible API
def fetch_models(api_base_url, api_key):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    response = requests.get(f'{api_base_url}/models', headers=headers)
    return response.json().get('data', [])

# Function to send a message to the OpenAI-compatible API
def send_message(message, api_base_url, api_key, model_id):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    data = {
        'model': model_id,
        'messages': st.session_state.messages
    }
    response = requests.post(f'{api_base_url}/chat/completions', headers=headers, json=data)
    return response.json()

# Streamlit UI
st.title("Chatbot UI")

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

# Chat message container
if 'messages' not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg['role']).container().markdown(msg['content'])

# User input field
user_input = st.chat_input("Say something")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    response = send_message(user_input, st.session_state.api_base_url, st.session_state.api_key, st.session_state.model_id)
    assistant_response = response['choices'][0]['message']['content']
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})

    # Display the assistant's response
    st.chat_message("assistant").container().markdown(response['choices'][0]['message']['content'])