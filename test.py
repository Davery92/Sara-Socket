import asyncio
import websockets

async def chatbot(websocket, path):
    print("Connected")

    while True:
        # Your server-side logic here
        message = await websocket.recv()
        print(f"Received: {message}")
        # Your response to the client goes here
        await websocket.send("Hello from Chatbot!")

start_server = websockets.serve(chatbot, "localhost", 8765)

asyncio.run(start_server)