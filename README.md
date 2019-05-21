# mqtt-xy-demo
This python script is intended as a simple demonstrator for connecting to a stream of xy coordinate data from an Irisys Vector device via an MQTT broker. The script connects to a locally hosted broker on 127.0.0.1, with no TLS authentication, no encryption and no password. These all can be enabled, however, by modifying the lines at the top of the script in line with the comments.
Targets are plotted live on the axes as blue dots. Targets marked as "tagged" (ie. wearing an Irisys lanyard) are further highlighted with a red circle.

## Requirements
The script just requires python3 and a couple of additional packages which can be installed with pip:
* pip install matplotlib
* pip install paho-mqtt

## MQTT target data format
The target data is delivered as little-endian binary data with no packing. The first byte is the target data format byte and will be zero for the current format. This byte will always be present and the packet ends there if no targets are present for this frame. If targets are present, the data continues with 15 bytes per target, packed as follows:

| DataType | Description                |
| -------- | -------------------------- |
| uint16   | target ID                  |
| uint8    | status bits (0x20: tagged) |
| float32  | x position (m)             |
| float32  | y position (m)             |
| float32  | target height (m)          |

Data is delivered from the device to the broker at 15 frames per second. The display updates at 30 frames per second.
