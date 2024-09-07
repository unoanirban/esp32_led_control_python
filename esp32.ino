#include <WiFi.h>

const char* ssid = "WiFi_SSID";        // Replace with your WiFi SSID
const char* password = "WiFi_passwor"; // Replace with your WiFi password

WiFiServer server(12345);  // Server will be listening on port 12345

const int ledPin = 2;  // GPIO pin where LED is connected (use GPIO 2 for onboard LED)

void setup() {
  Serial.begin(115200);
  pinMode(ledPin, OUTPUT);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }

  Serial.println("Connected to WiFi");
  Serial.println(WiFi.localIP());

  // Start the server
  server.begin();
}

void loop() {
  // Check if a client has connected
  WiFiClient client = server.available();
  if (client) {
    Serial.println("Client connected");
    String command = "";

    while (client.connected()) {
      if (client.available()) {
        char c = client.read();
        command += c;

        // Check if the command is complete (you can define this as per your protocol)
        if (command.indexOf("switchon") != -1) {
          Serial.println("Turning LED ON");
          digitalWrite(ledPin, HIGH);
          client.println("LED is ON");
          command = "";  // Reset command after processing
        }
        else if (command.indexOf("switchoff") != -1) {
          Serial.println("Turning LED OFF");
          digitalWrite(ledPin, LOW);
          client.println("LED is OFF");
          command = "";  // Reset command after processing
        }
      }
    }
    // Close the connection
    client.stop();
    Serial.println("Client disconnected");
  }
}
