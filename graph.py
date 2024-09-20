import getpass
import os
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage
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

def _call_model(state: GraphsState):
    messages = state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}

graph.add_edge(START, "modelNode")
graph.add_node("modelNode", _call_model)
graph.add_edge("modelNode", END)

memory = MemorySaver()

graph_runnable = graph.compile(checkpointer=memory)

