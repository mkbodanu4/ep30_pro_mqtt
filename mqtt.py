import paho.mqtt.publish as publish
import serial
import time
import json
import yaml
import argparse

with open("configuration.yaml", 'r') as stream:
    configuration = yaml.safe_load(stream)

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="turn on verbosity", action="store_true")
args = parser.parse_args()

verboseprint = print if args.verbose else lambda *a, **k: None

sleep_time = configuration['run']['sleep_time']
pause_time = configuration['run']['pause_time']

# Available sensors
rating_voltage = None
rating_current = None
nominal_battery_voltage = None
nominal_frequency = None
input_voltage = None
fault_voltage = None
output_voltage = None
load_level = None
output_frequency = None
battery_voltage = None
ups_temperature = None
utility_fail = None
battery_low = None
working_status = None
ups_failed = None
ups_type = None
test_in_progress = None
shutdown_active = None
beeper_on = None
message_data = None
is_charging = "OFF"
charging_current = None

# Calculated sensors
battery_level = None
output_power = None
input_power = None

hostname = configuration['mqtt']['hostname']
auth = None
if configuration['mqtt']['username'] and configuration['mqtt']['password']:
    auth = {
        'username': configuration['mqtt']['username'],
        'password': configuration['mqtt']['password']
    }


def topic(name, component='sensor'):
    return 'homeassistant/' + component + '/ep30_' + name


def name(sensor_name, prefix='EP30 ', suffix=''):
    return prefix + sensor_name + suffix


def friendly_name(sensor_name, prefix='', suffix=''):
    return prefix + sensor_name + suffix


def publish_multiple(msgs):
    try:
        publish.multiple(msgs=msgs, hostname=hostname, auth=auth)
    except Exception as e:
        print(e)


def publish_single(topic, payload):
    try:
        publish.single(topic=topic, payload=payload, hostname=hostname, auth=auth)
    except Exception as e:
        print(e)


while True:
    sensors_definitions = [
        {
            'topic': topic('rating_voltage/config'),
            'payload': json.dumps({
                "name": name("Rating Voltage"),
                "device_class": "voltage",
                "unit_of_measurement": "V",
                "state_topic": topic('rating_voltage/state'),
            })
        },
        {
            'topic': topic('rating_current/config'),
            'payload': json.dumps({
                "name": name("Rating Current"),
                "device_class": "current",
                "unit_of_measurement": "A",
                "state_topic": topic('rating_current/state'),
            })
        },
        {
            'topic': topic('nominal_battery_voltage/config'),
            'payload': json.dumps({
                "name": name("Nominal Battery Voltage"),
                "device_class": "voltage",
                "unit_of_measurement": "V",
                "state_topic": topic('nominal_battery_voltage/state'),
            })
        },
        {
            'topic': topic('nominal_frequency/config'),
            'payload': json.dumps({
                "name": name("Nominal Frequency"),
                "unit_of_measurement": "Hz",
                "state_topic": topic('nominal_frequency/state'),
            })
        },
        {
            'topic': topic('input_voltage/config'),
            'payload': json.dumps({
                "name": name("Input Voltage"),
                "device_class": "voltage",
                "unit_of_measurement": "V",
                "state_class": "measurement",
                "state_topic": topic('input_voltage/state'),
            })
        },
        {
            'topic': topic('fault_voltage/config'),
            'payload': json.dumps({
                "name": name("Fault Voltage"),
                "device_class": "voltage",
                "unit_of_measurement": "V",
                "state_class": "measurement",
                "state_topic": topic('fault_voltage/state'),
            })
        },
        {
            'topic': topic('output_voltage/config'),
            'payload': json.dumps({
                "name": name("Output Voltage"),
                "device_class": "voltage",
                "unit_of_measurement": "V",
                "state_class": "measurement",
                "state_topic": topic('output_voltage/state'),
            })
        },
        {
            'topic': topic('load_level/config'),
            'payload': json.dumps({
                "name": name("Load Level"),
                "unit_of_measurement": "%",
                "state_class": "measurement",
                "state_topic": topic('load_level/state'),
            })
        },
        {
            'topic': topic('output_frequency/config'),
            'payload': json.dumps({
                "name": name("Output Frequency"),
                "unit_of_measurement": "Hz",
                "state_class": "measurement",
                "state_topic": topic('output_frequency/state'),
            })
        },
        {
            'topic': topic('battery_voltage/config'),
            'payload': json.dumps({
                "name": name("Battery Voltage"),
                "device_class": "voltage",
                "unit_of_measurement": "V",
                "state_class": "measurement",
                "state_topic": topic('battery_voltage/state'),
            })
        },
        {
            'topic': topic('ups_temperature/config'),
            'payload': json.dumps({
                "name": name("Temperature"),
                "device_class": "temperature",
                "unit_of_measurement": "°C",
                "state_topic": topic('ups_temperature/state'),
            })
        },
        {
            'topic': topic('utility_fail/config', 'binary_sensor'),
            'payload': json.dumps({
                "name": name("Utility Fail (Immediate)"),
                "device_class": "power",
                "state_topic": topic('utility_fail/state', 'binary_sensor'),
            })
        },
        {
            'topic': topic('battery_low/config', 'binary_sensor'),
            'payload': json.dumps({
                "name": name("Battery Low"),
                "device_class": "battery",
                "state_topic": topic('battery_low/state', 'binary_sensor'),
            })
        },
        {
            'topic': topic('working_status/config'),
            'payload': json.dumps({
                "name": name("Working Status"),
                "state_topic": topic('working_status/state'),
            })
        },
        {
            'topic': topic('ups_failed/config', 'binary_sensor'),
            'payload': json.dumps({
                "name": name("UPS Failed"),
                "device_class": "problem",
                "state_topic": topic('ups_failed/state', 'binary_sensor'),
            })
        },
        {
            'topic': topic('ups_type/config', 'binary_sensor'),
            'payload': json.dumps({
                "name": name("Type is Line-Interactive"),
                "state_topic": topic('ups_type/state', 'binary_sensor'),
            })
        },
        {
            'topic': topic('test_in_progress/config', 'binary_sensor'),
            'payload': json.dumps({
                "name": name("Test in progress"),
                "state_topic": topic('test_in_progress/state', 'binary_sensor'),
            })
        },
        {
            'topic': topic('shutdown_active/config', 'binary_sensor'),
            'payload': json.dumps({
                "name": name("Shutdown Active"),
                "state_topic": topic('shutdown_active/state', 'binary_sensor'),
            })
        },
        {
            'topic': topic('beeper_on/config', 'binary_sensor'),
            'payload': json.dumps({
                "name": name("Beeper On"),
                "state_topic": topic('beeper_on/state', 'binary_sensor'),
            })
        },
        {
            'topic': topic('message/config'),
            'payload': json.dumps({
                "name": name("Fault State"),
                "state_topic": topic('message/state'),
            })
        },
        {
            'topic': topic('is_charging/config', 'binary_sensor'),
            'payload': json.dumps({
                "name": name("Charger Action"),
                "device_class": "battery_charging",
                "state_class": "measurement",
                "state_topic": topic('is_charging/state', 'binary_sensor'),
            })
        },
        {
            'topic': topic('charging_current/config'),
            'payload': json.dumps({
                "name": name("Charging Current"),
                "device_class": "current",
                "unit_of_measurement": "A",
                "state_class": "measurement",
                "state_topic": topic('charging_current/state'),
            })
        },
        {
            'topic': topic('battery_level/config'),
            'payload': json.dumps({
                "name": name("Battery Level"),
                "device_class": "battery",
                "unit_of_measurement": "%",
                "state_class": "measurement",
                "state_topic": topic('battery_level/state'),
            })
        },
        {
            'topic': topic('output_power/config'),
            'payload': json.dumps({
                "name": name("Output Power"),
                "device_class": "power",
                "unit_of_measurement": "W",
                "state_class": "measurement",
                "state_topic": topic('output_power/state'),
            })
        },
        {
            'topic': topic('input_power/config'),
            'payload': json.dumps({
                "name": name("Input Power"),
                "device_class": "power",
                "unit_of_measurement": "W",
                "state_class": "measurement",
                "state_topic": topic('input_power/state'),
            })
        },
    ]

    publish_multiple(sensors_definitions)

    time.sleep(sleep_time)

    ser = serial.Serial(configuration['serial']['port'], 2400, timeout=10)

    # F

    ser.reset_input_buffer()
    ser.reset_output_buffer()
    ser.write(b"F\n")
    time.sleep(.1)
    ser.flush()
    details_data = ser.read_until(b'\r')

    if details_data:
        details_data = details_data.decode("utf-8")
        verboseprint(details_data)

        rating_voltage = float(details_data[1:6])
        rating_current = float(details_data[7:10])
        nominal_battery_voltage = float(details_data[11:16])
        nominal_frequency = float(details_data[17:21])

        messages = [
            {
                'topic': topic('rating_voltage/state'),
                'payload': str(rating_voltage)
            },
            {
                'topic': topic('rating_current/state'),
                'payload': str(rating_current)
            },
            {
                'topic': topic('nominal_battery_voltage/state'),
                'payload': str(nominal_battery_voltage)
            },
            {
                'topic': topic('nominal_frequency/state'),
                'payload': str(nominal_frequency)
            },
        ]

        publish_multiple(messages)

    time.sleep(pause_time)

    # Q1

    ser.reset_input_buffer()
    ser.reset_output_buffer()
    ser.write(b"Q1\n")
    time.sleep(.1)
    ser.flush()
    data = ser.read_until(b'\r')

    if data:
        data = data.decode("utf-8")
        verboseprint(data)

        input_voltage = float(data[1:6])
        fault_voltage = float(data[7:12])
        output_voltage = float(data[13:18])
        load_level = int(data[19:22])
        output_frequency = float(data[23:27])
        battery_voltage = float(data[28:32])
        ups_temperature = float(data[33:37])
        utility_fail = int(data[38:39])
        battery_low = int(data[39:40])
        working_status = ord(data[40:41])
        ups_failed = int(data[41:42])
        ups_type = int(data[42:43])
        test_in_progress = int(data[43:44])
        shutdown_active = int(data[44:45])
        beeper_on = int(data[45:46])

        messages = [
            {
                'topic': topic('input_voltage/state'),
                'payload': str(input_voltage)
            },
            {
                'topic': topic('fault_voltage/state'),
                'payload': str(fault_voltage)
            },
            {
                'topic': topic('output_voltage/state'),
                'payload': str(output_voltage)
            },
            {
                'topic': topic('load_level/state'),
                'payload': str(load_level)
            },
            {
                'topic': topic('output_frequency/state'),
                'payload': str(output_frequency)
            },
            {
                'topic': topic('battery_voltage/state'),
                'payload': str(battery_voltage)
            },
            {
                'topic': topic('ups_temperature/state'),
                'payload': str(ups_temperature)
            },
            {
                'topic': topic('utility_fail/state', 'binary_sensor'),
                'payload': "OFF" if utility_fail == 1 else "ON"
            },
            {
                'topic': topic('battery_low/state', 'binary_sensor'),
                'payload': "ON" if battery_low == 1 else "OFF"
            },
            {
                'topic': topic('working_status/state'),
                'payload': "BatteryPriority" if working_status == 30 else "Bypass"
            },
            {
                'topic': topic('ups_failed/state', 'binary_sensor'),
                'payload': "ON" if ups_failed == 1 else "OFF"
            },
            {
                'topic': topic('ups_type/state', 'binary_sensor'),
                'payload': "ON" if ups_type == 1 else "OFF"
            },
            {
                'topic': topic('test_in_progress/state', 'binary_sensor'),
                'payload': "ON" if test_in_progress == 1 else "OFF"
            },
            {
                'topic': topic('shutdown_active/state', 'binary_sensor'),
                'payload': "ON" if shutdown_active == 1 else "OFF"
            },
            {
                'topic': topic('beeper_on/state', 'binary_sensor'),
                'payload': "ON" if beeper_on == 1 else "OFF"
            },
        ]

        publish_multiple(messages)

    time.sleep(pause_time)

    # G?

    ser.reset_input_buffer()
    ser.reset_output_buffer()
    ser.write(b"G?\n")
    time.sleep(.1)
    ser.flush()
    message_data = ser.read_until(b'\r')

    if message_data:
        message_data = message_data.decode("utf-8")
        verboseprint(message_data)

        publish_single(topic=topic('message/state'), payload=str(message_data))

    time.sleep(pause_time)

    # D

    ser.reset_input_buffer()
    ser.reset_output_buffer()
    ser.write(b"D\n")
    time.sleep(.1)
    ser.flush()
    is_charging_data = ser.read(3)

    if is_charging_data:
        is_charging_data = is_charging_data.decode("utf-8")
        verboseprint(is_charging_data)

        if is_charging_data:
            is_charging = "ON" if is_charging_data == 'ACK' else "OFF"

            publish_single(topic=topic('is_charging/state', 'binary_sensor'), payload=str(is_charging))

    time.sleep(pause_time)

    # X

    ser.reset_input_buffer()
    ser.reset_output_buffer()
    ser.write(b"X\n")
    time.sleep(.1)
    ser.flush()
    charging_data = ser.read_until(b'\n')

    if charging_data:
        charging_data = charging_data.decode("utf-8").strip()
        verboseprint(charging_data)

        charging_current = charging_data[0:2]
        if charging_current:
            charging_current = float(int(charging_current, 16))

            publish_single(topic=topic('charging_current/state'), payload=str(charging_current))

    time.sleep(pause_time)

    ser.close()

    # Calculating sensor values

    if rating_current is not None and load_level is not None and output_voltage is not None:
        output_power = int(float(rating_current) * (float(load_level) / 100) * float(output_voltage))

        publish_single(topic=topic('output_power/state'), payload=str(output_power))

    if battery_voltage is not None:
        if float(battery_voltage) > float(configuration['invertor_config']['full_voltage']):
            battery_level = 100
        else:
            battery_level = int((float(battery_voltage) - float(configuration['invertor_config']['empty_voltage'])) / (float(configuration['invertor_config']['full_voltage']) - float(configuration['invertor_config']['empty_voltage'])) * 100)

        publish_single(topic=topic('battery_level/state'), payload=str(battery_level))

    if battery_voltage is not None and charging_current is not None:
        if is_charging == "ON":
            input_power = int(float(battery_voltage) * float(charging_current))
        else:
            input_power = 0

        publish_single(topic=topic('input_power/state'), payload=str(input_power))
