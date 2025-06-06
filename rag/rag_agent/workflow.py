"""
This file contains the Agent's workflow as a step by step list of actions.

Each action is defined as a method in the AgentWorkflow class.
You can expand it by adding or modifying the steps.

For more info, check Llama index documentation: 
https://docs.llamaindex.ai/en/stable/module_guides/workflow/
"""

import asyncio

from llama_index.core.workflow import (
    Event,
    StartEvent,
    StopEvent,
    Workflow,
    step,
    Context
)
from llama_index.core.schema import NodeWithScore

from rag_agent.utils import (
    chat_request,
    generate_index
)


class QuestionTranslatedEvent(Event):
    question: str

class RetrieverEvent(Event):
    nodes: list[NodeWithScore]

class AnswerEvent(Event):
    answer: str

class AgentFlow(Workflow):

    @step
    async def translate_question(self, ctx: Context, ev: StartEvent) -> QuestionTranslatedEvent | None:
        index = ev.get("index")
        question = ev.get("question")
        language = ev.get("language")

        translation = chat_request(
            messages=[
                {"role": "assistant", "content": "You are an expert translator of any language to english. Translate the user input into English."},
                {"role": "user", "content": question}
            ]
        )
        await ctx.set("query", translation)
        await ctx.set("language", language)
        return QuestionTranslatedEvent(question=str(translation), index=index)
    
    @step
    async def retrieve(
        self, ctx: Context, ev: QuestionTranslatedEvent
    ) -> RetrieverEvent | None:
        "Entry point for RAG, triggered by a StartEvent with `query`."
        query = ev.question
        index = ev.index

        if not query:
            return None

        # get the index from the global context
        if index is None:
            print("Index is empty, load some documents before querying!")
            return None

        retriever = index.as_retriever(similarity_top_k=3)
        nodes = await retriever.aretrieve(query)
        print(f"[retriever]: retrieved {len(nodes)} nodes.")
        return RetrieverEvent(nodes=nodes)

    @step
    async def answer_question(self, ctx: Context, ev: RetrieverEvent) -> AnswerEvent:
        question = await ctx.get("query", default=None)
        knowledge = ev.nodes

        print("[answer] ->> Nodes: ", len(knowledge))

        knowledge = [node.text for node in knowledge]

        answer = chat_request(
            messages=[
                {"role": "assistant", "content": f"You are an expert assistant that answers questions solely based on the information available to it. Here's your knowledge: {knowledge}"},
                {"role": "user", "content": question}
            ]
        )
        return AnswerEvent(answer=answer)
    
    @step
    async def translate_back(self, ctx: Context, ev: AnswerEvent) -> StopEvent:
        answer = ev.answer
        language = await ctx.get("language", default=None)

        answer = chat_request(
            messages=[
                {"role": "assistant", "content": f"You are an expert translator from English to {language}. Translate the following answer to {language}: {answer}."},
                {"role": "user", "content": answer}
            ]
        )
        return StopEvent(result=answer)


async def run_workflow(index, question, language):
    w = AgentFlow(timeout=600, verbose=False)

    result = await w.run(question=question, language=language, index=index)
    return str(result)


if __name__ == "__main__":
    index = generate_index(folder="./data")

    result = asyncio.run(
        run_workflow(index=index, question="Que demuestran los resultados experimentales?", language="Spanish")
    )
    print(result)

