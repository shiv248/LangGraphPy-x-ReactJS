import json
import os
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from graph import invoke_our_graph
from datetime import datetime
from cust_logger import logger, set_files_message_color

app = FastAPI()

set_files_message_color('purple')

app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")

@app.get("/")
async def serve_root():
    return FileResponse(os.path.join("frontend", "build", "index.html"))

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    file_path = os.path.join("frontend", "build", full_path)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return FileResponse(os.path.join("frontend", "build", "index.html"))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    user_uuid = None
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(json.dumps({"timestamp": datetime.now().isoformat(), "uuid": user_uuid, "received": json.loads(data)}))

            try:
                payload = json.loads(data)
                user_uuid = payload.get("uuid")
                message = payload.get("message")
                init = payload.get("init", False)
                if init:
                    logger.info(json.dumps({"timestamp": datetime.now().isoformat(), "uuid": user_uuid, "op": "Initializing ws with client."}))
                else:
                    if message:
                        await invoke_our_graph(websocket, message, user_uuid)
            except json.JSONDecodeError as e:
                logger.error(json.dumps({"timestamp": datetime.now().isoformat(), "uuid": user_uuid, "op": f"JSON encoding error - {e}"}))
    except Exception as e:
        logger.error(json.dumps({"timestamp": datetime.now().isoformat(), "uuid": user_uuid, "op": f"Error: {e}"}))
    finally:
        if user_uuid:
            logger.info(json.dumps({"timestamp": datetime.now().isoformat(), "uuid": user_uuid, "op": "Closing connection."}))
        try:
            await websocket.close()
        except RuntimeError as e:
            logger.error(json.dumps({"timestamp": datetime.now().isoformat(), "uuid": user_uuid, "op": f"WebSocket close error: {e}"}))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")