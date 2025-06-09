import paho.mqtt.client as mqtt
import json
import time
import signal
import sys

def create_client():
    client = mqtt.Client(protocol=mqtt.MQTTv5, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.connect("localhost", 1883)
    return client

def publish_message(client):
    phases = [0.1, -2.3, 1.2]
    freqs = [5e9, 5.5e9, 6e9]
    message = json.dumps({"phases": phases, "freqs": freqs})
    client.publish("radar/phases", message)

def signal_handler(sig, frame):
    print("\nShutting down publisher...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def main():
    while True:
        try:
            client = create_client()
            client.loop_start()
            publish_message(client)
            client.loop_stop()
            client.disconnect()
            time.sleep(1)
        except KeyboardInterrupt:
            signal_handler(signal.SIGINT, None)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main() 