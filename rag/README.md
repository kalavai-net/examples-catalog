# Multi language RAG example

This project uses models hosted in CoGen AI. [Get your free account here](https://cogenai.kalavai.net).


## Get started

First, you need to configure your environment, for which you have two options:
- Use local python
- Use Docker container


### Use local python

This is the recommended way if you have Python installed in your computer. If you don't, [go ahead and install it](https://www.python.org/downloads/) for your  platform.

Run the following from the `rag` folder to configure your environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Use docker

If you don't have (or don't need) python installed, you can still run the code by using a docker container environment. Make sure you have [docker installed](https://docs.docker.com/engine/install/) in your machine.

```bash
docker run -i -t -p 8501:8501 --volume <your local path to the rag project>:/home/rag python:3.10-slim /bin/bash
cd /home/rag
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running the UI agent

Once you have your environment configured, you can run the application:

```bash
streamlit run chatbot_ui.py
```

This will make your agent available via your browser by visiting http://localhost:8501


## Prompts

Bad prompt:

```
build a chatbot
```

Good prompt:

```
@/rag_agent/workflow.py given the current agent workflow implementation, create a front end chatbot UI with streamlit (using chat_message for better UX) where users can ask questions to the agent. Use the run_workflow as endpoint for the chat
```

Best prompt:

```
In the current project I have an implementation of an RAG agent (in @/rag_agent/workflow.py) and now I want to build a chatbot application that can handle multilanguage queries. The agent should take a set of documents (in a user specified folder) for indexing. With the indexing done, users should be able to interface with the agent workflow via a chatbot UI. Please use python as language, and build the UI interface with streamlit (using the chat_message function). There should be a separation of concerns between the backend (workflow and utils) and the frontend (the new chat UI). Make sure the front end submits the user query to the agent via the run_workflow function at @/rag_agent/workflow.py.

```

