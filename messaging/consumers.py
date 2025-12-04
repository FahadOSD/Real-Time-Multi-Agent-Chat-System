# messaging/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if not user or not user.is_authenticated:
            await self.close(code=4003)  # Forbidden
            return

        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        user_id = user.id

        # In connect() method — replace the security check with this:
        user_id_str = str(user.id)
        allowed = any(user_id_str in part for part in self.room_name.split("_"))
        if not allowed:
            await self.close(code=4003)
            return
        self.group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message", "")

        # Import only here (safe)
        from .models import Message
        user_ids = [int(x) for x in self.room_name.split("_") if x.isdigit()]
        recipient_id = user_ids[0] if user_ids[1] == self.scope["user"].id else user_ids[1]

        # Save message
        await database_sync_to_async(Message.objects.create)(
            sender=self.scope["user"],
            recipient_id=recipient_id,
            content=message
        )

        payload = {
            "message": message,
            "sender_id": self.scope["user"].id,
            "sender_username": self.scope["user"].username,
            "timestamp": "__now__"  # frontend will replace
        }

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat_message",
                "payload": payload,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event["payload"]))