import streamlit as st
from app import ChatbotAPI

st.title("Chatbot UI")

# Input fields for API parameters in the sidebar
with st.sidebar:
    api_base_url = st.text_input("API Base URL", "https://api.cogenai.kalavai.net")
    api_key = st.text_input("API Key", type="password")
    # Fetch available models
    if api_base_url and api_key:
        try:
            chatbot_api = ChatbotAPI(api_base_url, api_key)
            models = chatbot_api.get_available_models()
            model_id = st.sidebar.selectbox("Model ID", models, index=models.index("qwen-qwen3-30b-a3b") if "qwen-qwen3-30b-a3b" in models else 0)
        except Exception as e:
            st.sidebar.error(f"Failed to fetch models: {e}")
            model_id = st.sidebar.text_input("Model ID", "qwen-qwen3-30b-a3b")
    else:
        model_id = st.sidebar.text_input("Model ID", "qwen-qwen3-30b-a3b")

# Initialize the ChatbotAPI class
if api_base_url and api_key and model_id:
    chatbot_api = ChatbotAPI(api_base_url, api_key, model_id)

# Chat interface
if 'messages' not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if api_base_url and api_key and model_id:
        response = chatbot_api.send_message(prompt)
        if 'choices' in response and len(response['choices']) > 0:
            reply = response['choices'][0]['message']['content']
            st.session_state.messages.append({"role": "assistant", "content": reply})
            with st.chat_message("assistant"):
                st.markdown(reply)
    else:
        st.error("Please enter valid API parameters.")