import asyncio
import json 
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from random import randint 
from time import sleep
from coba.models import CheckIn

class PracticeConsumer(AsyncConsumer):
    # when websocket connect
    async def websocket_connect(self,event):
        print("connected",event)
        await self.send({"type" : "websocket.accept"})

        await self.send({"type" : "websocket.send", "text" : 0})

    async def websocket_receive(self,event):
        # when message is recieved

        print("receive",event)
        sleep(1)
        await self.send({"type" : "websocket.send", "text" : str(randint(0,100))})

    async def websocket_disconnect(self,event):
        # when websocket disconnects
        print("disconnected",event)