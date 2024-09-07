import socket

def send_command_to_esp32(command):
    esp32_ip = "192.168.x.x"  # Replace with your ESP32's IP address
    esp32_port = 12345         # Replace with the port you're using on the ESP32

    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to the ESP32
        client_socket.connect((esp32_ip, esp32_port))

        # Send the command to ESP32 (as bytes)
        client_socket.send(command.encode())

        # Optional: Receive a response from ESP32
        response = client_socket.recv(1024)
        print(f"Response from ESP32: {response.decode()}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Close the socket
        client_socket.close()

# Example usage
command = "switchon"
send_command_to_esp32(command)
