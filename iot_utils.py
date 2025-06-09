# iot_utils.py

import ssl
import paho.mqtt.client as mqtt
# For AWS IoT: from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient (if installed)

def connect_mqtt(broker, port, client_id, cafile=None, certfile=None, keyfile=None):
    """
    Connect to an MQTT broker (non-AWS) using Paho.
    """
    client = mqtt.Client(client_id=client_id)
    if cafile and certfile and keyfile:
        client.tls_set(ca_certs=cafile, certfile=certfile, keyfile=keyfile, 
                       tls_version=ssl.PROTOCOL_TLSv1_2)
    client.connect(broker, port)
    return client

def connect_aws_iot(client_id, endpoint, port=8883, cafile='root-CA.crt', 
                    certfile='device.pem.crt', keyfile='private.pem.key'):
    """
    Stub for AWS IoT connection (requires AWSIoTPythonSDK).
    """
    # Example using AWS IoT Device SDK:
    # aws_client = AWSIoTMQTTClient(client_id)
    # aws_client.configureEndpoint(endpoint, port)
    # aws_client.configureCredentials(cafile, keyfile, certfile)
    # aws_client.connect()
    # return aws_client
    raise NotImplementedError("AWS IoT integration requires AWSIoTPythonSDK.")
