import socket
import time
def send_command_to_esp32(command):
    esp32_ip = "192.168.X.X"  # Replace with your ESP32's IP address
    esp32_port = 12345         # Replace with the port you're using on the ESP32

    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to the ESP32
        client_socket.connect((esp32_ip, esp32_port))

        # Send the command to ESP32 (as bytes)
        client_socket.send(command.encode())
        # print(f"{command.encode()}")        # To see how the encoded command looks like

        # Optional: Receive a response from ESP32
        response = client_socket.recv(1024)
        # res_dec = response.decode()
        print(f"Response from ESP32: {response.decode()}")
        # print(response)                   # To see the encoded response from ESP32

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Close the socket
        client_socket.close()

# Example usage
# command1 = "switchon"
# command2 = "switchoff"
while True:
    # send_command_to_esp32(command1)
    # time.sleep(1)
    # send_command_to_esp32(command2)
    # time.sleep(1)
    command = input("Enter command: ")        # i.e: "switchon" or "switchoff"
    send_command_to_esp32(command)
    time.sleep(1)


