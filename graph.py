import json
from datetime import datetime
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from fastapi import WebSocket
from langchain_fireworks import ChatFireworks

from langchain_core.callbacks import adispatch_custom_event
from langchain_core.runnables.config import RunnableConfig
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.checkpoint.memory import MemorySaver

from cust_logger import logger, set_files_message_color

load_dotenv()

llm = ChatFireworks(
  model="accounts/fireworks/models/firefunction-v2",
  temperature=0.0,
  max_tokens=256
  )

# This is the default state  same as "MessageState" TypedDict but allows us accessibility to
# custom keys to our state like user's details
class GraphsState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    # user_id: int

graph = StateGraph(GraphsState)

async def conditional_check(state: GraphsState, config: RunnableConfig):
    messages = state["messages"]
    msg = messages[-1].content
    keywords = ["LangChain", "langchain", "Langchain", "LangGraph", "Langgraph", "langgraph"]
    if any(keyword in msg for keyword in keywords):
        await adispatch_custom_event("on_easter_egg",True, config=config)
    pass

def _call_model(state: GraphsState, config: RunnableConfig):
    messages = state["messages"]
    response = llm.invoke(messages, config=config)
    return {"messages": [response]}

graph.add_node("conditional_check", conditional_check)
graph.add_node("modelNode", _call_model)
graph.add_edge(START, "conditional_check")
graph.add_edge("conditional_check", "modelNode")
graph.add_edge("modelNode", END)

memory = MemorySaver()

graph_runnable = graph.compile(checkpointer=memory)


async def invoke_our_graph(websocket: WebSocket, data: str, user_uuid: str):
    set_files_message_color('MAGENTA')
    initial_input = {"messages": data}
    thread_config = {"configurable": {"thread_id": user_uuid}}
    final_text = ""

    async for event in graph_runnable.astream_events(initial_input, thread_config, version="v2"):
        kind = event["event"]

        if kind == "on_chat_model_stream":
            addition = event["data"]["chunk"].content
            final_text += addition
            if addition:
                message = json.dumps({"on_chat_model_stream": addition})
                await websocket.send_text(message)

        elif kind == "on_chat_model_end":
            message = json.dumps({"on_chat_model_end": True})
            logger.info(json.dumps({"timestamp": datetime.now().isoformat(), "uuid": user_uuid, "llm_method": kind, "sent": final_text}))
            await websocket.send_text(message)

        elif kind == "on_custom_event":
            message = json.dumps({event["name"]: event["data"]})
            logger.info(json.dumps({"timestamp": datetime.now().isoformat(), "uuid": user_uuid, "llm_method": kind, "sent": message}))
            await websocket.send_text(message)

