import paho.mqtt.client as mqtt
import threading
import time
import signal
import sys

# Create a broker client with protocol version 5 and latest callback API
broker = mqtt.Client(protocol=mqtt.MQTTv5, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

# Set up broker callbacks
def on_connect(client, userdata, flags, rc, properties=None):
    print(f"Broker connected with result code {rc}")

def on_message(client, userdata, msg, properties=None):
    # Forward the message to all subscribers
    client.publish(msg.topic, msg.payload)

def on_disconnect(client, userdata, flags, rc, properties=None):
    print(f"Broker disconnected with result code {rc}")

# Set callbacks
broker.on_connect = on_connect
broker.on_message = on_message
broker.on_disconnect = on_disconnect

# Connect to localhost
broker.connect("localhost", 1883)

# Start the broker loop in a separate thread
def run_broker():
    try:
        broker.loop_forever()
    except Exception as e:
        print(f"Broker error: {e}")

broker_thread = threading.Thread(target=run_broker)
broker_thread.daemon = True
broker_thread.start()

print("Simple MQTT broker running on localhost:1883")
print("Press Ctrl+C to stop")

def signal_handler(sig, frame):
    print("\nShutting down broker...")
    broker.disconnect()
    broker_thread.join(timeout=1)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    signal_handler(signal.SIGINT, None) 