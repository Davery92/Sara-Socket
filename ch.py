import chainlit as cl
import os
import datetime
import websockets
from websockets import WebSocketClientProtocol

import requests



def save_file(filepath, content):
    with open(filepath, 'a', encoding='utf-8') as outfile:
        outfile.write(content)

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
        return infile.read()


async def send_user_message(socket, message):
    await socket.send(message)

uri = "ws://10.185.1.9:8765"

@cl.on_chat_start
async def on_chat_start():
    conversation = []
   
    
    cl.user_session.set("memory", conversation)
    
    


@cl.on_message
async def on_message(message: cl.Message):

        async with websockets.connect(uri) as socket:
            user_msg = ('\n\nUser: ' + message.content)
            
            await send_user_message(socket, user_msg)
            response = await socket.recv()
            msg = cl.Message(content=response)

            await msg.send()
            pong_waiter = socket.ping()

            await pong_waiter  # This will raise a TimeoutError if no Pong is received within the timeout period
        
    
   
    


    
