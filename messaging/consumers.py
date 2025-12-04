import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from .models import Message

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        if not user.is_authenticated:
            await self.close()
            return

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        message = data.get('message')
        sender_id = self.scope['user'].id

        # room_name is left as 'minID_maxID' or similar
        user_ids = [int(x) for x in self.room_name.split('_') if x.isdigit()]
        recipient_id = None
        if len(user_ids) == 2:
            recipient_id = user_ids[0] if user_ids[1] == sender_id else user_ids[1]

        if message and recipient_id:
            msg = await sync_to_async(Message.objects.create)(
                sender_id=sender_id, recipient_id=recipient_id, content=message
            )

            payload = {
                'message': message,
                'sender_id': sender_id,
                'sender_username': self.scope['user'].username,
                'timestamp': msg.timestamp.isoformat(),
            }

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'payload': payload,
                }
            )

    async def chat_message(self, event):
        payload = event['payload']
        await self.send(text_data=json.dumps(payload))
