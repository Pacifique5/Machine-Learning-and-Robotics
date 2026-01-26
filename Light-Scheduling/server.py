import asyncio
import websockets
import json
import paho.mqtt.publish as publish
from datetime import datetime

# MQTT configuration
MQTT_BROKER = '157.173.101.159'  # Replace with your broker IP if needed
MQTT_PORT = 1883
MQTT_TOPIC = 'relay/schedule'

# Store the latest schedule
schedule = {'on_time': None, 'off_time': None}

async def handle_connection(websocket, path):
    try:
        async for message in websocket:
            data = json.loads(message)
            on_time = data['onTime']  # e.g., "20:23"
            off_time = data['offTime']  # e.g., "20:24"
            
            # Since the time is already in 24-hour format (HH:MM), use it directly
            schedule['on_time'] = on_time
            schedule['off_time'] = off_time
            
            # Send confirmation back to the browser
            await websocket.send(f"Scheduled: ON at {on_time}, OFF at {off_time}")
            print(f"Received schedule: ON at {on_time}, OFF at {off_time}")
    except Exception as e:
        await websocket.send(f"Error: {str(e)}")
        print(f"WebSocket error: {e}")

async def check_schedule():
    while True:
        now = datetime.now().strftime('%H:%M')  # Current time in HH:MM (24-hour)
        if schedule['on_time'] == now:
            print(f"Triggering ON at {now}")
            publish.single(
                topic=MQTT_TOPIC,
                payload='1',
                hostname=MQTT_BROKER,
                port=MQTT_PORT,
                retain=False
            )
        if schedule['off_time'] == now:
            print(f"Triggering OFF at {now}")
            publish.single(
                topic=MQTT_TOPIC,
                payload='0',
                hostname=MQTT_BROKER,
                port=MQTT_PORT,
                retain=False
            )
        await asyncio.sleep(30)  # Check every 30 seconds

async def main():
    server = await websockets.serve(handle_connection, "localhost", 8765)
    print("WebSocket server running on ws://localhost:8765")
    asyncio.create_task(check_schedule())
    await server.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped")