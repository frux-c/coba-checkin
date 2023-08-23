import json
import asyncio
from asgiref.sync import async_to_sync, sync_to_async
#channel imports
# from channels.exceptions import DenyConnection
from channels.consumer import AsyncConsumer
from channels.generic.websocket import AsyncJsonWebsocketConsumer

# #django imports
# from django.core.exceptions import ObjectDoesNotExist
# from django.contrib.auth.models import AnonymousUser

#local imports
from .models import CheckIn, Student
import json

class CheckInConsumer(AsyncJsonWebsocketConsumer):
	GROUP_NAME = 'events'
	async def connect(self):
		print('websocket.connect is triggered')
		await self.channel_layer.group_add(
			self.GROUP_NAME,
			self.channel_name
			)
		await self.accept()

	async def disconnect(self,close_code):
		print('websocket.disconnect is triggered')
		self.close(close_code)

	async def receive(self,text_data):
		print('websocket.receive is triggered')
		try:
			response = json.loads(text_data)
		except Exception as e:
			print(e)
			await self.send(text_data=json.dumps(
				{"payload" : {
					"message" : "Parse Error Detected!",
					 "event" : "websocket.error"}
			}))
			return # break out
		event = response.get("event",None)
		message = response.get("message",None)

		if event == "websocket.connect":
			await self.channel_layer.group_send(self.GROUP_NAME,
				{"type" : "send_message",
				 "message" : "new device joined!",
				 "event" : "websocket.connect"})

		if event == "websocket.primary_student_update":
			message = sync_to_async(lambda : ",".join([f"{model.user}" for model in CheckIn.objects.filter(is_on_clock=True)]))
			await self.send(text_data=json.dumps({
				"payload" : {
					"event" : "websocket.update_students",
	         		"message" : await message()
				}}))

		if event == "websocket.student_checkin_status":
			student = message.split(' ',1)
			student_object = await sync_to_async(Student.objects.filter,thread_sensitive=True)(
			                            first_name = student[0],
			                            last_name = student[-1])
			if not await sync_to_async(student_object.exists)():
				await self.send(text_data=json.dumps({
					"payload" : {
						"event" : "websocket.student_checkin_status",
						"message" : "404" # student not found
						}
					}))
				return # break out
			student_object = await sync_to_async(list)(student_object)
			check = await sync_to_async(CheckIn.objects.filter,thread_sensitive=True)(user=student_object[0],
			                                is_on_clock = True)
			await self.send(text_data=json.dumps({
				"payload" : {
					"event" : "websocket.student_checkin_status",
					"message" : await sync_to_async(check.exists)()
					}
				}))

	async def send_message(self,res):
		await self.send(
			text_data=json.dumps({
				"payload" : res
			}))

	def __str__(self):
		return f"CheckInConsumer({self})"
