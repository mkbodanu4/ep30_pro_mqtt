# MQTT Client for EP30 Pro
Application for Must EP30 Pro Charger/Inverter, that allows to integrate it into Home Assistant using MQTT.

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

## Configuration

Open `configuration.yaml` and update serial port and MQTT server details with your own.

## Usage
### Running with CLI:

```sh
$ python mqtt.py [-v] [-h]
```

Note: You may need to run script with admin/root privileges.

Enabling verbose returns raw data from UPS serial port into console stdout.

## Running as service (via systemd)

1. Copy `ep30.service` to systemd configuration folder

```sh
$ sudo cp ./ep30.service /etc/systemd/system/ 
```

2. Open file with text editor

```sh
$ sudo nano /etc/systemd/system/ep30.service
```

3. If Mosquitto service not running at same server, remove `mosquitto.service` from `After` option of `[Unit]` section.


4. Update `WorkingDirectory` and `ExecStart` with proper path to code.


5. Start and enable service

```sh
$ sudo systemctl start ep30
$ sudo systemctl enable ep30
```

# Licence

Code is licensed under the terms of the MIT License (see the file LICENSE).