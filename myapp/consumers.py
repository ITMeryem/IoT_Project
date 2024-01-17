import json
from channels.generic.websocket import AsyncWebsocketConsumer


class SensorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

        temperature = text_data_json['temp']
        humidity = text_data_json['hum']

        # Enregistrez les données dans la base de données ou effectuez toute autre opération nécessaire

        # Répondez avec les mêmes données pour confirmer la réception
        await self.send(text_data=json.dumps({
            'temp': temperature,
            'hum': humidity
        }))
