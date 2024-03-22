import asyncio
import websockets
from time import sleep
from websockets import WebSocketClientProtocol

async def send_user_message(socket, message):
    await socket.send(message)

async def interact_with_chatbot(uri):
    while True:
        try:
            async with websockets.connect(uri) as socket:
                print("Connected to chatbot server")

                while True:
                    user_input = input("You: ")
                    if user_input.lower() == "q":
                        await socket.send("/quit")
                        break
                    else:
                        await send_user_message(socket, user_input)
                        message = await socket.recv()
                        print(f"Chatbot response: {message}")
                    pong_waiter = socket.ping()
                    try:
                        await pong_waiter  # This will raise a TimeoutError if no Pong is received within the timeout period
                    except asyncio.TimeoutError:
                        print("Timeout while waiting for Pong!")
                    await asyncio.sleep(2)  # Wait for 10 seconds
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"WebSocket connection closed unexpectedly: {e}")


asyncio.run(interact_with_chatbot("ws://10.185.1.9:8765"))