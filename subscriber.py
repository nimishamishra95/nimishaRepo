import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
from datetime import datetime
import json
import queue
import threading
import time

# MQTT settings
BROKER = "localhost"
PORT = 1883
TOPIC = "time_series/data"

# Data storage
timestamps = []
values = []
data_queue = queue.Queue()

def on_message(client, userdata, msg):
    """Callback for receiving MQTT messages."""
    data = json.loads(msg.payload.decode())
    data_queue.put(data)

def mqtt_subscriber():
    """Subscribe to the MQTT topic in a separate thread."""
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(BROKER, PORT)
    client.subscribe(TOPIC)
    client.loop_forever()

def plot_data():
    """Plot data from the queue."""
    global timestamps, values

    plt.ion()
    fig, ax = plt.subplots()

    while True:
        # Process new data from the queue
        while not data_queue.empty():
            data = data_queue.get()
            timestamp = datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S")
            value = data["value"]
            
            timestamps.append(timestamp)
            values.append(value)

            # Keep only the latest 100 points
            if len(timestamps) > 100:
                timestamps.pop(0)
                values.pop(0)

        # Update the plot
        ax.clear()
        ax.plot(timestamps, values, marker="o")
        ax.set_title("Live Time-Series Data")
        ax.set_xlabel("Timestamp")
        ax.set_ylabel("Value")
        fig.autofmt_xdate()
        plt.pause(0.01)
        time.sleep(0.1)  # Reduce CPU usage

if __name__ == "__main__":
    # Start MQTT subscriber in a separate thread
    subscriber_thread = threading.Thread(target=mqtt_subscriber)
    subscriber_thread.daemon = True
    subscriber_thread.start()

    # Start the plotting function in the main thread
    plot_data()
