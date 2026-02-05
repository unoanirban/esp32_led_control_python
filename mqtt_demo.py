import sys
import time
import base64
import cv2
import RPi.GPIO as GPIO
from Adafruit_IO import MQTTClient

# =======================
# 1. Configuration
# =======================
ADAFRUIT_IO_USERNAME = 'anirban_01'
# REPLACE WITH YOUR ACTUAL AIO KEY
ADAFRUIT_IO_KEY = 'YOUR_ADAFRUIT_IO_KEY_HERE' 

LED_FEED_ID = 'relay1'
CAMERA_FEED_ID = 'camera'

LED_PIN = 12   # GPIO 12 (BCM)

# Your IP Webcam stream URL
IP_CAM_URL = 'http://192.168.1.5:8080/video'

# =======================
# 2. GPIO Setup
# =======================
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.output(LED_PIN, GPIO.LOW)

# =======================
# 3. MQTT Callbacks
# =======================
def connected(client):
    print(f'Connected to Adafruit IO! Listening for {LED_FEED_ID} changes...')
    client.subscribe(LED_FEED_ID)

def disconnected(client):
    print('Disconnected from Adafruit IO')

def message(client, feed_id, payload):
    # This runs in the background thread
    print(f'Received: {feed_id} -> {payload}')
    
    if feed_id == LED_FEED_ID:
        if payload.upper() in ['ON', '1']:
            GPIO.output(LED_PIN, GPIO.HIGH)
            print(">> LED TURNED ON")
        else:
            GPIO.output(LED_PIN, GPIO.LOW)
            print(">> LED TURNED OFF")

# =======================
# 4. Initialize MQTT Client
# =======================
client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)
client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message

# Connect to the server
try:
    client.connect()
except Exception as e:
    print(f"Could not connect to Adafruit IO: {e}")
    sys.exit(1)

# IMPORTANT: loop_background() runs the MQTT network loop in a separate thread.
# This ensures the LED remains responsive even while the main loop is busy with the camera.
client.loop_background()

# =======================
# 5. Camera Setup
# =======================
cap = cv2.VideoCapture(IP_CAM_URL)

if not cap.isOpened():
    print("Cannot open IP camera stream")
    # We don't exit here, so that the LED control still works even if Camera fails
else:
    print("Camera stream started...")

# =======================
# 6. Main Loop
# =======================
try:
    while True:
        # If camera is not valid, just wait and loop (LED still works via background thread)
        if not cap.isOpened():
            time.sleep(1)
            continue

        ret, frame = cap.read()
        if not ret:
            print("Frame read failed")
            time.sleep(2)
            continue

        # --- ULTRA COMPRESSION ---
        # 1. Resize to a tiny thumbnail (100x75 pixels)
        frame = cv2.resize(frame, (100, 75))

        # 2. Convert to Grayscale (removes color data, saves 3x size)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 3. Encode to JPEG with extremely low quality (10-15)
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 15])

        # 4. Convert to Base64 string
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        
        size = len(image_base64)
        
        # Adafruit IO Free Limit Check (~1000 bytes safe limit)
        if size < 1024:
            try:
                client.publish(CAMERA_FEED_ID, image_base64)
                print(f"Snapshot sent: {size} bytes")
            except Exception as e:
                print(f"Publish Error: {e}")
        else:
            print(f"Skipped: Image too large ({size} bytes)")

        # Wait 4 seconds before sending the next frame.
        # This keeps you within the "30 points per minute" limit.
        # Note: This sleep DOES NOT block the LED because MQTT is in the background.
        time.sleep(4)

except KeyboardInterrupt:
    print("\nStopping system...")

finally:
    # Cleanup
    cap.release()
    GPIO.cleanup()
    # If using loop_background, strictly speaking we don't need a stop command 
    # as disconnect handles it, but good practice to disconnect cleanly.
    client.disconnect()
