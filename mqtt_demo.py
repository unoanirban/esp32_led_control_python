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
ADAFRUIT_IO_KEY = 'YOUR_ACTUAL_API_KEY_HERE'  # <--- DON'T FORGET THIS

LED_FEED_ID = 'relay1'
CAMERA_FEED_ID = 'camera'
LED_PIN = 12 

IP_CAM_URL = 'http://192.168.1.5:8080/video'

# =======================
# GPIO Setup
# =======================
GPIO.setwarnings(False) # Good to silence warnings on restart
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.output(LED_PIN, GPIO.LOW)

# =======================
# MQTT Callbacks
# =======================
def connected(client):
    print(f'Connected to Adafruit IO. Listening for {LED_FEED_ID}...')
    client.subscribe(LED_FEED_ID)

def disconnected(client):
    print('Disconnected from Adafruit IO')

def message(client, feed_id, payload):
    # This now runs in a background thread, so it's instant!
    if feed_id == LED_FEED_ID:
        print(f'Incoming Command: {payload}')
        if payload.upper() in ['ON', '1']:
            GPIO.output(LED_PIN, GPIO.HIGH)
        else:
            GPIO.output(LED_PIN, GPIO.LOW)

# =======================
# Main Logic
# =======================
# 1. Setup MQTT
client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)
client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message

try:
    client.connect()
    # loop_start runs the network loop in a background thread
    client.loop_start() 
except Exception as e:
    print(f"Failed to connect to MQTT: {e}")
    sys.exit(1)

# 2. Setup Camera
cap = cv2.VideoCapture(IP_CAM_URL)
if not cap.isOpened():
    print("Cannot open IP camera stream")
    GPIO.cleanup()
    sys.exit(1)

print("System Running. Press Ctrl+C to stop.")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Frame drop")
            time.sleep(1)
            continue

        # -------- ULTRA COMPRESSION --------
        # Resize to thumbnail (Maintain aspect ratio if possible, e.g., 4:3)
        frame = cv2.resize(frame, (100, 75)) 
        
        # Grayscale
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Encode: Quality 10 is very blocky but saves space
        success, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 10])
        
        if success:
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            size = len(image_base64)

            # Adafruit IO Free Tier Warning:
            # If you exceed 1KB/sec frequently, you may get throttled (timeout).
            if size < 1024: 
                try:
                    client.publish(CAMERA_FEED_ID, image_base64)
                    print(f"Tx: {size} bytes")
                except Exception as e:
                    print(f"Publish failed: {e}")
            else:
                print(f"Skipped: {size} bytes (Too Large)")

        # Throttle to respect rate limits (e.g., 1 frame every 3 seconds)
        time.sleep(3) 

except KeyboardInterrupt:
    print("\nStopping...")

finally:
    client.loop_stop() # Stop background thread
    cap.release()
    GPIO.cleanup()
    client.disconnect()
