# Vibecoding for free: Chatbot

Example of how to leverage CoGenAI API to power a chatbot application. All the models used in this example are available for free in [CoGenAI](https://cogenai.kalavai.net).

This project was created using Vibe Coding ([Roo Code](https://github.com/RooVetGit/Roo-Code) + [CoGenAI API](https://cogenai.kalavai.net)), and the prompts used to generate it are included below.


## Setup

```bash
virtualenv -p python3 env
source env/bin/activate
```

## Run

```bash
streamlit run chatbot_app/app.py
```

## Vibe coding

The project has been entirely generated using a coding model from CoGenAI (**Qwen2.5 Coder 32B**) alongside the [VS extension for Roo Code](https://github.com/qpd-v/Roo-Code?tab=readme-ov-file#installation). Follow along our video tutorial for more information.


## Prompts

The prompts used to generate the project are listed here:

> I want to create a chatbot UI using streamlit (using their chat_message functionality for better UX) as frontend and python in the backend. The chatbot must use as a model an external OpenAI comptible API service. The user should be able to set the required service parameters from the frontend: api base url, api key and model id. Don't use any external library unless striclty necessary (use requests for http requests)

> Can you move the openAI compatible API settings to the sidebar?

> Since we are using an OpenAI compatible API, the models available can be listed using the GET endpoint /v1/models. Swap to using a selector instead of a text input to set the model ID, where the options are the models listed by the endpoint call.

```
TOTAL TOKENS CONSUMED:

- Input: 167k
- Output: 4k
```