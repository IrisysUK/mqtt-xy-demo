import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from threading import Lock
import struct
import datetime

# update the lines below to point to your MQTT broker and topic
broker_address = "127.0.0.1"
broker_port = 1883
topic = "irisys/V4D-17020025/targets"

# uncomment and edit the below two lines if a username and password are required (for MQTT broker)
#username = "myname"
#password = "mypassword"

# uncomment the below line for TLS authentication and encryption with your own CA key
#ca_certfile = "ca.pem"

# uncomment the below line if the Common Name on your server's certificate does not match (for debug only!)
#tls_insecure = True

# global vars
lock = Lock()               # mutex to protect multithreaded access to x and y position data
x_data, y_data = [], []     # arrays to hold x and y position data in for display
x_marked, y_marked = [], [] # arrays to hold x and y position data for marked targets

# prepare figure for plotting target positions
fig = plt.figure()
marked, = plt.plot(x_marked, y_marked, 'ro')
points, = plt.plot(x_data, y_data, 'b.')
plt.axis([-2, 2, -2, 2])
plt.grid()

# MQTT message-in callback function
def on_message(client, userdata, message):
  # first byte of message is "type"- we only support types 0 and 1, so ignore anything else
  messageType = message.payload[0]
  if messageType != 0 and messageType != 1:
    print("unknown target format: " + str(message.payload))
    return

  # calculate number of targets in message @ 15 bytes per target
  sizeofTarget = 15
  numTargets = int((len(message.payload) - 1) / sizeofTarget)
  offset = 1
  if messageType == 1:
    # next 8 bytes are timestamp (messageType 1)
    timestamp, = struct.unpack_from('<Q', message.payload, offset)
    dt = datetime.datetime.fromtimestamp(timestamp / 1000.0)
    print("timestamp: ", dt)
    offset = offset + 8
  lock.acquire()
  x_data.clear()
  y_data.clear()
  x_marked.clear()
  y_marked.clear()
  for i in range(numTargets):
      # unpack the data (little-endian with no padding):
      #  uint16 - targetID
      #  uint8  - status
      #  float32 - x position (m)
      #  float32 - y position (m)
      #  float32 - height (m)
      targetID, status, x, y, h = struct.unpack_from('<HBfff', message.payload, offset)
      offset = offset + sizeofTarget
      x_data.append(x)
      y_data.append(y)
      if status & 0x20:
        x_marked.append(x)
        y_marked.append(y)
  lock.release()

# connect to the MQTT broker and start the thread to service it
client = mqtt.Client("target_harvester")
client.on_message=on_message
if 'ca_certfile' in vars():
  client.tls_set(ca_certfile)
if 'tls_insecure' in vars():
  client.tls_insecure_set(tls_insecure)
if 'username' in vars() and 'password' in vars():
  client.username_pw_set(username, password)
client.connect(broker_address, broker_port)
client.loop_start()
client.subscribe(topic)

# animation callback function
def update(frame):
  lock.acquire()
  marked.set_data(x_marked, y_marked)
  points.set_data(x_data, y_data)
  lock.release()

# set up the animation loop and show the figure (loop will run until figure is closed)
animation = FuncAnimation(fig, update, interval=30)
plt.show()

client.loop_stop()
