# End-to-end chatbot

Example of how to leverage CoGenAI API to power an audio to speech chatbot. All the models used in this example are available for free in [CoGenAI](https://cogenai.kalavai.net):

- Speech-to-text (tiny.en)
- Text-to-Speech (hexgrad)
- LLM (Qwen3 30B a3b)


## Setup

```bash
virtualenv -p python3 env
source env/bin/activate
```

## Prompts

The project has been entirely generated using a coding model from CoGenAI (Qwen2.5 Coder 32B). The prompts used to get it are listed here:

> I want to create a chatbot UI using streamlit as frontend and python in the backend. The chatbot must use as a model an external OpenAI comptible API service. The user should be able to set the required service parameters: api base url, api key and model id.


> Can you move the openAI compatible API settings to the sidebar?

> Since we are using an OpenAI compatible API, the models available can be listed using the GET endpoint /v1/models. Swap to using a selector instead of a text input to set the model ID, where the options are the models listed by the endpoint call.

TOTAL TOKENS:

- Input: 281.0k
- Output: 4.4k