import sys
import time
import base64
import cv2
import RPi.GPIO as GPIO
from Adafruit_IO import MQTTClient

# =======================
# Configuration
# =======================
ADAFRUIT_IO_USERNAME = 'anirban_01'
ADAFRUIT_IO_KEY = ''

LED_FEED_ID = 'relay1'
CAMERA_FEED_ID = 'camera'

LED_PIN = 12   # GPIO 12 (BCM)

# Your IP Webcam stream URL
IP_CAM_URL = 'http://192.168.1.5:8080/video'

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
    print('Connected to Adafruit IO')
    print('Subscribing to LED feed...')
    client.subscribe(LED_FEED_ID)

def disconnected(client):
    print('Disconnected from Adafruit IO')
    GPIO.cleanup()
    sys.exit(1)

def message(client, feed_id, payload):
    print(f'{feed_id} → {payload}')

    if feed_id == LED_FEED_ID:
        if payload.upper() in ['ON', '1']:
            GPIO.output(LED_PIN, GPIO.HIGH)
            print("LED ON")
        else:
            GPIO.output(LED_PIN, GPIO.LOW)
            print("LED OFF")

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
    print("Cannot open IP camera")
    GPIO.cleanup()
    sys.exit(1)

print("System started...")

# =======================
# Main Loop
# =======================
try:
    while True:

        # Keep MQTT alive
        client.loop()

        ret, frame = cap.read()
        if not ret:
            print("Frame not received")
            time.sleep(1)
            continue

        # -------- ULTRA COMPRESSION BLOCK --------

        # Very small resolution
        frame = cv2.resize(frame, (120, 90))

        # Convert to grayscale
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Very low JPEG quality
        _, buffer = cv2.imencode(
            '.jpg',
            frame,
            [cv2.IMWRITE_JPEG_QUALITY, 15]
        )

        image_base64 = base64.b64encode(buffer).decode('utf-8')

        size = len(image_base64)
        print("Payload bytes:", size)

        # Publish only if under limit
        if size < 1000:
            client.publish(CAMERA_FEED_ID, image_base64)
            print("Image sent")
        else:
            print("Skipped — too large")

        time.sleep(1)

except KeyboardInterrupt:
    print("Stopping...")

finally:
    cap.release()
    GPIO.cleanup()
    client.disconnect()
