import asyncio
import websockets
from uuid import uuid4
import ollama
from websockets import WebSocketServerProtocol
from uuid import uuid4
import datetime
from qdrant_client.http import models
from qdrant_client import QdrantClient
from pymongo import MongoClient

mclient = MongoClient('mongodb://localhost:27017/')
db = mclient['saradb']
collection = db['chat_history']

qclient = QdrantClient("localhost", port=6333)

note_convo = []
conversation = []

save_convo = ["save this conversation", "save this convo"]


def save_file(filepath, content):
    with open(filepath, 'a', encoding='utf-8') as outfile:
        outfile.write(content)

def save_convo_note(title):
     dir_name = r"C:\Users\David\OneDrive - Avery-Labs\Documents\Davids-Vault\Sara"
     convo = ''.join(map(str, note_convo))
     save_file("%s/%s.md" % (dir_name, title), convo)
     print("saving")

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
        return infile.read()

class CustomServerProtocol(WebSocketServerProtocol):
    async def ping(self, data=None):
        print("Ping received. Sending Pong...")
        await self.pong()
        
        
        

async def chatbot(websocket: CustomServerProtocol, path):
    uuid = str(uuid4())
    #await websocket.send("Hello, I am Sara. How can I help you?")

    

    while True:
        try:
            id = str(uuid4())
            a = datetime.datetime.now()
            ID = a.strftime("%A %d %B %Y")
            message = await websocket.recv()
            response = ollama.embeddings(model='nomic-embed-text', prompt=message)
            response = response['embedding']
            query = qclient.search(
                collection_name="test_collection",
                query_vector=response,
                limit=3,)
            conversation.append({'role': 'system', 'content': open_file('prompts/memory.txt').replace('<<MESSAGES>>', str(query[0].payload))})
            conversation.append({"role": "user", "content": message})
            user_msg = ('\n\nUser: ' + message)
            note_convo.append(user_msg)

            print(conversation)
            mystring = message
            for word in save_convo:
                if word in mystring:
                    #note_convo.append(user_msg)
                    keyword = 'as'
                    before_keyword, keyword, after_keyword = mystring.partition(keyword)
                    save_convo_note(after_keyword)
                    break
            else:    
                document = {'role': 'user', 'content': message, "date": ID}
                collection.insert_one(document)
                qclient.upsert(
                    collection_name="test_collection",
                    points=[models.PointStruct(id=id,payload={
                                "user": message,
                            },vector=response,),],)
                stream  = ollama.chat(
                    model='cas/nous-hermes-2-mistral-7b-dpo:latest',
                    messages=conversation,
                    stream=False
                )
                response = stream['message']['content']
                await websocket.send(stream['message']['content'])
                conversation.append({"role": "assistant", "content": response})
                ai_ass = ('\n\n Sara: ' + response)
                note_convo.append(ai_ass)
                id = str(uuid4())
                response = ollama.embeddings(model='nomic-embed-text', prompt=response)
                response = response['embedding']
                document = {'role': 'assistant', 'content': response, "date": ID}
                collection.insert_one(document)
                qclient.upsert(
                    collection_name="test_collection",
                    points=[models.PointStruct(id=id,payload={
                                "assistant": response,
                            },vector=response,),],)
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed")
            break  # Exit the loop and end the coroutine

 


if len(conversation) > 20:
    conversation.pop(0)
start_server = websockets.serve(chatbot, "0.0.0.0", 8765, create_protocol=CustomServerProtocol)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()