from fastapi import FastAPI, WebSocket

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # Accept WebSocket connection
    try:
        while True:
            data = await websocket.receive_text()  # Receive message from client
            print(f"Received: {data}")

            # Echo the received message back to the client
            await websocket.send_text(data)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await websocket.close()  # Close WebSocket connection

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

