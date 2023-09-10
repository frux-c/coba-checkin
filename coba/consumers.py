import json
from channels.consumer import AsyncConsumer
from channels.generic.websocket import AsyncJsonWebsocketConsumer
#django imports
import django
django.setup()
#local imports
import json

class CheckInConsumer(AsyncJsonWebsocketConsumer):
	GROUP_NAME = 'events'
	async def connect(self): # called when the websocket is handshaking as part of initial connection
		await self.channel_layer.group_add(
			self.GROUP_NAME,
			self.channel_name
		)
		await self.accept()

	async def disconnect(self,close_code): # called when the websocket closes
		self.close(close_code)

	async def receive(self,text_data): # called when the client sends message
		print(f"channel name: {self.channel_name}")
		print(f"incoming message: {text_data}")

	async def send_group_message(self,res):
		del res['type']
		await self.send(text_data=json.dumps(res)) # send message to websocket

	def __str__(self):
		return f"CheckInConsumer({self})"
