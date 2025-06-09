# predict.py

import json
import time
import pickle
import numpy as np
import paho.mqtt.client as mqtt
import signal
import sys
from unwrap import weighted_crt_unwrap
from blockchain_log import BlockchainLogger
from iot_utils import connect_mqtt, connect_aws_iot
# At top of predict.py, change:
USE_MQTT = True
BROKER_HOST = "localhost"       # instead of mqtt.example.com
BROKER_PORT = 1883

# Load trained models
with open('rf_model.pkl','rb') as f: rf_model = pickle.load(f)
with open('huber_model.pkl','rb') as f: huber_model = pickle.load(f)
model_loaded = True

# Initialize blockchain logger
logger = BlockchainLogger('predictions_log.json')

# Flag to enable cloud features
USE_MQTT = True
USE_AWS = False

# MQTT callback: received new phase vector
def on_message(client, userdata, msg, properties=None):
    """
    Callback when an MQTT message is received on the subscribed topic.
    """
    try:
        payload = json.loads(msg.payload.decode())
        phases = np.array(payload["phases"])  # e.g. in radians
        freqs = np.array(payload["freqs"])
        # Method 1: CRT unwrap
        d_crt = weighted_crt_unwrap(phases, freqs, noise_vars=None, max_range=200.0)
        # Method 2: ML prediction
        d_rf = rf_model.predict(phases.reshape(1,-1))[0]
        d_huber = huber_model.predict(phases.reshape(1,-1))[0]
        # Combine or choose (here we average)
        d_pred = float(np.mean([d_crt, d_rf, d_huber]))
        timestamp = time.time()
        result = {"distance": d_pred, "timestamp": timestamp, "phases": phases.tolist()}
        print(f"Predicted distance: {d_pred:.2f} m")
        # Publish or store prediction
        if USE_MQTT:
            client.publish("radar/predictions", json.dumps(result))
        if USE_AWS:
            # For AWS IoT, use specialized AWS IoT client (stub below)
            pass  # e.g., aws_client.publish(topic, json.dumps(result))
        # Log in blockchain
        logger.add_record(result)
    except Exception as e:
        print("Error processing message:", e)

def on_disconnect(client, userdata, flags, rc, properties=None):
    print(f"Disconnected with result code {rc}")

def signal_handler(sig, frame):
    print("\nShutting down predictor...")
    if USE_MQTT:
        client.disconnect()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def main():
    if USE_MQTT:
        client = mqtt.Client(protocol=mqtt.MQTTv5, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        client.connect(BROKER_HOST, BROKER_PORT)
        client.on_message = on_message
        client.on_disconnect = on_disconnect
        client.subscribe("radar/phases")
        print("Subscribed to MQTT topic 'radar/phases'.")
        try:
            client.loop_forever()
        except KeyboardInterrupt:
            signal_handler(signal.SIGINT, None)

    if USE_AWS:
        aws_client = connect_aws_iot(...)
        aws_client.subscribe("radar/phases", callback=on_message)
        aws_client.connect()
        print("Subscribed to AWS IoT topic 'radar/phases'.")
        # AWS SDK may block internally or provide a similar loop...
        while True:
            time.sleep(1)

if __name__ == "__main__":
    main()
