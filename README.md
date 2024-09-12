# Control ESP32 from PC using python script
This project demonstrates how to control an ESP32 microcontroller from a PC using Python commands sent over Wi-Fi through sockets.

This project demonstrates controlling an LED connected to an ESP32 from a PC using Python and Wi-Fi sockets. Commands like switchon and switchoff are sent over Wi-Fi to the ESP32, which adjusts the LED accordingly.

Key points:

ESP32 controls an LED via GPIO pins based on commands received over Wi-Fi.
Python script on the PC sends commands via sockets to the ESP32.
Both devices must be on the same Wi-Fi network.
Commands include switchon, switchoff, and exit.
The project requires Python 3.x and the socket library.
Steps include setting up the ESP32, running the Python script, and entering commands to control the LED.
