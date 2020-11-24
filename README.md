# ep30_pro_mqtt
Application for Must EP30 Pro Charger/Inverter, that allows integrate it into Home Assistant using MQTT integration.

## Installation

1. Install dependencies using `pip`:

```sh
$ pip install paho-mqtt pyserial
```
   
2. Check out and install the latest source code

```sh
$ git clone https://github.com/mkbodanu4/ep30_pro_mqtt.git
$ cd ep30_pro_mqtt/
```

## Usage
### Running with CLI:

```sh
$ python mqtt.py [-u MQTT_USERNAME] [-u MQTT_PASSWORD] [-v] [-h] SERIAL_PORT MQTT_BROKER_HOSTNAME
```

Linux example

```sh
$ python mqtt.py /dev/ttyS1 127.0.0.1
```

Windows example

```sh
$ python mqtt.py COM1 127.0.0.1
```

Note: You may need to run script with admin/root privileges.

Enabling verbose returns raw data from UPS serial port into console stdout.

# Licence

Code is licensed under the terms of the MIT License (see the file LICENSE).