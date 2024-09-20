import asyncio
import json

from fastapi import FastAPI, WebSocket
from langchain_core.messages import AIMessage, HumanMessage

from graph import graph_runnable

app = FastAPI()

async def invoke_our_graph(websocket: WebSocket, data: str, user_uuid: str):
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
            print(f"Sent to client - {user_uuid}: {final_text}")
            await websocket.send_text(message)

        elif kind == "on_custom_event":
            message = json.dumps({event["name"]: event["data"]})
            await websocket.send_text(message)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received: {data}")

            try:
                payload = json.loads(data)
                uuid = payload.get("uuid")
                message = payload.get("message")
                init = payload.get("init", False)
                if init:
                    print(f"Initialization received. UUID: {uuid}")
                else:
                    if message:
                        await invoke_our_graph(websocket, message, uuid)
            except json.JSONDecodeError as e:
                print(f"Json encoding error - {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
