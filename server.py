import asyncio
import json

from fastapi import FastAPI, WebSocket
from langchain_core.messages import AIMessage, HumanMessage

from graph import graph_runnable

app = FastAPI()

message_history = [AIMessage("Hi how can I help you?")]

async def invoke_our_graph(websocket: WebSocket, data: str):
    message_history.append(HumanMessage(data))
    initial_input = {"messages": message_history}
    thread_config = {"configurable": {"thread_id": "1"}}
    final_text = ""

    async for event in graph_runnable.astream_events(initial_input, thread_config, version="v2"):
        kind = event["event"]
        print(f"Event: {kind}")

        if kind == "on_chat_model_stream":
            # Get the streamed content chunk
            addition = event["data"]["chunk"].content

            # Update final_text progressively with new content
            final_text += addition

            if addition:
                # Send the streamed content as a JSON object
                message = json.dumps({"on_chat_model_stream": addition})
                await websocket.send_text(message)

        elif kind == "on_chat_model_end":
            # Send an end signal to the client
            message = json.dumps({"on_chat_model_end": True})
            print(f"Sent to client: {final_text}")
            await websocket.send_text(message)
            message_history.append(AIMessage(final_text))


        elif kind == "on_custom_event":
            print(event["name"], event["data"])
            await websocket.send_text(event["data"]["input"])

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # Accept WebSocket connection
    try:
        while True:
            data = await websocket.receive_text()  # Receive message from client
            print(f"Received: {data}")

            # Instead of echoing, run the asynchronous number generator
            await invoke_our_graph(websocket, data)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await websocket.close()  # Close WebSocket connection

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
