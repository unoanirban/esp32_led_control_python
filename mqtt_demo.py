import sys
import time
import base64
import cv2
import RPi.GPIO as GPIO
from Adafruit_IO import MQTTClient

# =======================
# Configuration
# =======================
ADAFRUIT_IO_USERNAME = ''
ADAFRUIT_IO_KEY = ''

LED_FEED_ID = 'relay1'
CAMERA_FEED_ID = 'humidity'

LED_PIN = 12  # GPIO 12 (BCM)

IP_CAM_URL = 'http://192.168.xx.xx:8080/video'

# =======================
# GPIO Setup
# =======================
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.output(LED_PIN, GPIO.LOW)

# =======================
# MQTT Callbacks
# =======================
def connected(client):
    print(f'Connected to Adafruit IO! Subscribing to {LED_FEED_ID}...')
    client.subscribe(LED_FEED_ID)

def disconnected(client):
    print('Disconnected from Adafruit IO!')
    GPIO.cleanup()
    sys.exit(1)

def message(client, feed_id, payload):
    print(f'Feed {feed_id} received new value: {payload}')

    if feed_id == LED_FEED_ID:
        if payload.upper() in ['ON', '1']:
            GPIO.output(LED_PIN, GPIO.HIGH)
            print('LED ON')
        else:
            GPIO.output(LED_PIN, GPIO.LOW)
            print('LED OFF')

# =======================
# MQTT Client
# =======================
client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message

client.connect()

# =======================
# Camera Setup
# =======================
cap = cv2.VideoCapture(IP_CAM_URL)

if not cap.isOpened():
    print('Failed to open IP camera')
    GPIO.cleanup()
    sys.exit(1)

print('System running...')

# =======================
# Main Loop
# =======================
try:
    while True:
        # Allow MQTT to receive LED commands
        client.loop()

        ret, frame = cap.read()
        if not ret:
            print('Camera frame not received')
            time.sleep(1)
            continue

        # Resize for MQTT safety
        frame = cv2.resize(frame, (320, 240))

        # Encode as JPEG
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 40])

        # Convert to Base64
        image_base64 = base64.b64encode(buffer).decode('utf-8')

        # Publish image
        client.publish(CAMERA_FEED_ID, image_base64)
        print('Image sent')

        time.sleep(1)

except KeyboardInterrupt:
    print('\nStopping program...')

finally:
    cap.release()
    GPIO.cleanup()
    client.disconnect()
