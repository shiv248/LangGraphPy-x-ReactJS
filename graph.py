# Anything below this is entirely up to you to change and is flexible to your LangGraph build, drop in replacement
# `invoke_our_graph` expects the compiled graph to be called `graph_runnable` to work out of the box.
import sys, os
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from langchain_core.callbacks import adispatch_custom_event
from langchain_core.runnables.config import RunnableConfig
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.checkpoint.memory import MemorySaver

from cust_logger import logger, set_files_message_color

set_files_message_color('MAGENTA')  # Set color for logging in this function

# loads and checks if env var exists before continuing to model invocation
load_dotenv()
env_var_key = "OPENAI_API_KEY"
model_path = os.getenv(env_var_key)

# If the API key is missing, log a fatal error and exit the application, no need to run LLM application without model!
if not model_path:
    logger.fatal(f"Fatal Error: The '{env_var_key}' environment variable is missing.")
    sys.exit(1)

# Initialize the ChatModel LLM
# ChatModel vs LLM concept https://python.langchain.com/docs/concepts/#chat-models
# Available ChatModel integrations with LangChain https://python.langchain.com/docs/integrations/chat/
try:
    llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # base_url="...",
    # organization="...",
    # other params...
)
except Exception as e:
    # Log error if model initialization fails, exits. no vroom vroom :(
    logger.fatal(f"Fatal Error: Failed to initialize model: {e}")
    sys.exit(1)

# This is the default state same as "MessageState" TypedDict but allows us accessibility to custom keys
class GraphsState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    # Custom keys for additional data can be added here such as - conversation_id: str

graph = StateGraph(GraphsState)

# This is part of the easter egg! Essentially it will check for specific mention of keywords in the messages
# and if it exists dispatch an immediate event to the frontend to catch to trigger an action or change in render.
# This is a clear representation of the flexibility both any frontend and LangGraph can have with WS.
async def conditional_check(state: GraphsState, config: RunnableConfig):
    # Try it out! ask the model any of the keywords below and see what happens in the frontend
    messages = state["messages"]
    msg = messages[-1].content
    keywords = ["LangChain", "langchain", "Langchain", "LangGraph", "Langgraph", "langgraph"]
    if any(keyword in msg for keyword in keywords):
        # we pass RunnableConfig in case the server is running on Python 3.10 or earlier
        # https://langchain-ai.github.io/langgraph/how-tos/streaming-tokens/#:~:text=Note%20on%20Python%20%3C%203.11
        await adispatch_custom_event("on_easter_egg", True, config=config)
    pass

# Core invocation of the model
def _call_model(state: GraphsState, config: RunnableConfig):
    messages = state["messages"]
    response = llm.invoke(messages, config=config)
    return {"messages": [response]}

# Define graph nodes and edges for conditional checks and model invocation
graph.add_node("modelNode", _call_model)
graph.add_node("conditional_check", conditional_check)
graph.add_edge(START, "conditional_check")
graph.add_edge("conditional_check", "modelNode")
graph.add_edge("modelNode", END)

memory = MemorySaver()  # Checkpointing mechanism to save conversation by thread_id
                        # https://langchain-ai.github.io/langgraph/how-tos/persistence/

graph_runnable = graph.compile(checkpointer=memory)

# ===========================================================================================================
# `invoke_our_graph` expects the compiled graph to be called `graph_runnable` to work out of the box. feel free to add your own
# event actions. Here is the list of available events: https://python.langchain.com/docs/how_to/streaming/#event-reference
# logs message in {"timestamp": "YYYY-MM-DDTHH:MM:SS.MS", "uuid": "", "llm_method": "", "sent": ""} format
# except for token streaming due to verbosity
import json
from datetime import datetime
from fastapi import WebSocket

# Merging WS with LangGraph to invoke the graph and stream results to WebSocket
async def invoke_our_graph(websocket: WebSocket, data: str, user_uuid: str):
    initial_input = {"messages": data}
    thread_config = {"configurable": {"thread_id": user_uuid}}  # Pass users conversation_id to manage chat memory on server side
    final_text = ""  # accumulate final output to log, rather then each token

    # Asynchronous event-based response processing, data designated by event as key
    async for event in graph_runnable.astream_events(initial_input, thread_config, version="v2"):
        kind = event["event"]

        if kind == "on_chat_model_stream":
            addition = event["data"]["chunk"].content  # gets the token chunk
            final_text += addition
            if addition:
                message = json.dumps({"on_chat_model_stream": addition})
                await websocket.send_text(message)

        elif kind == "on_chat_model_end":
            # Indicate the end of model generation so FE knows the message is over
            message = json.dumps({"on_chat_model_end": True})
            logger.info(json.dumps({"timestamp": datetime.now().isoformat(), "uuid": user_uuid, "llm_method": kind, "sent": final_text}))
            await websocket.send_text(message)

        elif kind == "on_custom_event":
            # sends across custom event as if its its own event for easy working
            # check out `conditional_check` node
            message = json.dumps({event["name"]: event["data"]})
            logger.info(json.dumps({"timestamp": datetime.now().isoformat(), "uuid": user_uuid, "llm_method": kind, "sent": message}))
            await websocket.send_text(message)
