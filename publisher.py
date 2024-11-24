import paho.mqtt.client as mqtt
import random
import time
import json
from datetime import datetime

# MQTT settings
BROKER = "localhost"
PORT = 1883
TOPIC_BASE = "time_series/data"  # Base topic

def generate_random_data(stream_id):
    """Generate random time-series data for a specific stream."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    value = random.uniform(10.0, 100.0)  # Random value between 10 and 100
    return {"stream_id": stream_id, "timestamp": timestamp, "value": value}

def publish_data():
    """Connect to MQTT broker and publish random data from three streams."""
    client = mqtt.Client()
    client.connect(BROKER, PORT)

    try:
        while True:
            for stream_id in range(1, 4):  # Stream IDs 1, 2, and 3
                data = generate_random_data(stream_id)
                topic = f"{TOPIC_BASE}/stream{stream_id}"  # Separate topic per stream
                client.publish(topic, json.dumps(data))
                print(f"Published to {topic}: {data}")
            time.sleep(1)  # Publish each set every second
    except KeyboardInterrupt:
        print("Publisher stopped.")
    finally:
        client.disconnect()

if __name__ == "__main__":
    publish_data()
