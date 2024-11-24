import paho.mqtt.client as mqtt
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import json
import queue
import threading
import time
import pandas as pd

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
    """Plot data from the queue using Seaborn with enhanced aesthetics."""
    global timestamps, values

    # Set Seaborn style
    sns.set(style="darkgrid")
    plt.ion()
    fig, ax = plt.subplots(figsize=(10, 6))

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

        if timestamps:
            # Create DataFrame for plotting
            df = pd.DataFrame({"Timestamp": timestamps, "Value": values})
            
            ax.clear()
            # Line plot for time-series
            sns.lineplot(data=df, x="Timestamp", y="Value", linewidth=2, ax=ax)
            # Scatter plot for individual points
            sns.scatterplot(data=df, x="Timestamp", y="Value", s=50, color="blue", alpha=0.6, ax=ax)

            # Customize the plot
            ax.set_title("Live Time-Series Data", fontsize=18, weight="bold", color="#2e3b4e")
            ax.set_xlabel("Timestamp", fontsize=14, color="#2e3b4e")
            ax.set_ylabel("Value", fontsize=14, color="#2e3b4e")
            ax.tick_params(axis="x", rotation=45, labelsize=10)
            ax.tick_params(axis="y", labelsize=12)

            plt.tight_layout()
            plt.pause(0.01)
            time.sleep(0.1)  # Reduce CPU usage

if __name__ == "__main__":
    # Start MQTT subscriber in a separate thread
    subscriber_thread = threading.Thread(target=mqtt_subscriber)
    subscriber_thread.daemon = True
    subscriber_thread.start()

    # Start the plotting function in the main thread
    plot_data()
