import json
import asyncio
from channels.consumer import AsyncConsumer
from channels.generic.websocket import AsyncJsonWebsocketConsumer
#django imports
import django
django.setup()
#local imports

class CheckInConsumer(AsyncJsonWebsocketConsumer):
	GROUP_NAME = 'events'
	async def connect(self): # called when the websocket is handshaking as part of initial connection
		# accept the connection
		await self.accept()
		# add user to group
		await self.channel_layer.group_add(
			self.GROUP_NAME,
			self.channel_name
		)
		# start keep alive task
		self.keep_alive_task = asyncio.ensure_future(self.send_keep_alive())

	async def disconnect(self,close_code): # called when the websocket closes
		# discard user from group
		await self.channel_layer.group_discard(
			self.GROUP_NAME,
			self.channel_name
		)
		# cancel keep alive task
		self.keep_alive_task.cancel()

	async def receive(self,text_data): # called when the client sends message
		print(
			f"User: {self.scope['user']}",
			f"CheckInConsumer:receive: {text_data}",
			sep="\n"
		)

	async def send_group_message(self,res):
		del res['type']
		await self.send(text_data=json.dumps(res)) # send message to websocket

	async def send_keep_alive(self):
		while True:
			await asyncio.sleep(10)
			await self.send(text_data=json.dumps({'message':'keep_alive', 'type':'keep_alive'}))
		
	def __str__(self):
		return f"CheckInConsumer({self})"