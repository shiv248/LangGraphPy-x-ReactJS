import getpass
import os
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.callbacks import adispatch_custom_event
from langchain_core.runnables.config import RunnableConfig
from langgraph.graph import START, END, StateGraph, MessagesState
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.checkpoint.memory import MemorySaver

from dotenv import load_dotenv
from langchain_fireworks import ChatFireworks

load_dotenv()

# Initialize a Fireworks chat model
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

