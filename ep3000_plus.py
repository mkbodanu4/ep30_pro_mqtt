from json import dumps
from os.path import isfile
from time import sleep, time_ns
from yaml import safe_load

import paho.mqtt.publish as publish

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# Uncomment this section to see what is sent and recieved from Modbus client
# import logging
# logging.basicConfig()
# log = logging.getLogger()
# log.setLevel(logging.DEBUG)

from pymodbus.constants import Endian
from pymodbus.client import ModbusSerialClient
from pymodbus.register_read_message import ReadHoldingRegistersResponse


def topic(name_value, component='sensor'):
    return 'homeassistant/' + component + '/ep30_' + name_value


def name(sensor_name, prefix='EP30 ', suffix=''):
    return prefix + sensor_name + suffix


def publish_multiple(msgs):
    try:
        publish.multiple(msgs=msgs, hostname=hostname, auth=auth)
    except Exception as e:
        print(e)


def add_sensor_data(name, value):
    if backend == 'mqtt':
        sensors_data.append({
            'topic': topic(str(name) + '/state'),
            'payload': str(value)
        })
    elif backend == 'influx':
        metric.field(name, float(value))


def get_sensor_data(name):
    index = sensor_details[name]['register_index']
    multi = sensor_details[name]['multiplier']
    return float(format(round(result.registers[index] * multi, 1), '.1f'))


def push_data():
    if backend == 'mqtt':
        publish_multiple(sensors_data)
    elif backend == 'influx':
        metric.time(timestemp)
        try:
            write_api.write(bucket=bucket, record=metric)
        except Exception as e:
            print(e)


attributes = [
    {
        'id': 'MachineTypeI',
        'name': 'Machine Type',
        'unit_of_measurement': 't'
    },
    {
        'id': 'SoftwareVersionI',
        'name': 'Software Version',
        'unit_of_measurement': 'v'
    },
    {
        'id': 'WorkStateI',
        'name': 'Work State',
        'unit_of_measurement': 's'
    },
    {
        'id': 'BatClass',
        'name': 'Battery',
        'unit_of_measurement': 'V'
    },
    {
        'id': 'RatedPower',
        'name': 'Rated Power',
        'unit_of_measurement': 'W'
    },
    {
        'id': 'GridVoltage',
        'name': 'Grid Voltage',
        'unit_of_measurement': 'V',
        'multiplier': 0.1
    },
    {
        'id': 'GridFrequency',
        'name': 'Grid Frequency',
        'unit_of_measurement': 'HZ',
        'multiplier': 0.1
    },
    {
        'id': 'OutputVoltage',
        'name': 'Output Voltage',
        'unit_of_measurement': 'V',
        'multiplier': 0.1
    },
    {
        'id': 'OutputFrequency',
        'name': 'Output Frequency',
        'unit_of_measurement': 'HZ',
        'multiplier': 0.1
    },
    {
        'id': 'LoadCurrent',
        'name': 'Load Current',
        'unit_of_measurement': 'A'
    },
    {
        'id': 'LoadPower',
        'name': 'Load Power',
        'unit_of_measurement': 'W'
    },
    {
        'id': 'VA',
        'name': 'Volt/Amper',
        'unit_of_measurement': 'VA'
    },
    {
        'id': 'LoadPercent',
        'name': 'Load Percent',
        'unit_of_measurement': '%',
    },
    {
        'id': 'BatteryTemperature',
        'name': 'Battery Temperature',
        'unit_of_measurement': 'C'
    },
    {
        'id': 'BatteryVoltage',
        'name': 'Battery Voltage',
        'unit_of_measurement': 'V',
        'multiplier': 0.1
    },
    {
        'id': 'BatteryCurrent',
        'name': 'Battery Current Charging',
        'unit_of_measurement': 'A',
        'multiplier': 0.1
    },
    {
        'id': 'BuzzerState',
        'name': 'Buzzer State',
        'unit_of_measurement': 'on/off'
    },
    {
        'id': 'BatterySOC',
        'name': 'Battery State-of-Charge',
        'unit_of_measurement': '%'
    },
    {
        'id': 'TransformerTEMP',
        'name': 'Inverter Temperature',
        'unit_of_measurement': 'C'
    },
    {
        'id': 'SystemAlarmId',
        'name': 'System Alarm Id',
        'unit_of_measurement': 'n'
    },
    {
        'id': 'ChargeStageI',
        'name': 'Charge Stage',
        'unit_of_measurement': 'n'
    },
    {
        'id': 'GridChargeFlagI',
        'name': 'Grid Charge Flag',
        'unit_of_measurement': 'n'
    },
    {
        'id': 'GridState',
        'name': 'Grid State',
        'unit_of_measurement': 'n'
    }
]
last_index = len(attributes) - 1

sensor_details = {
    'battery_voltage': {
        'register_index': 14,
        'multiplier': 0.1
    },
    'charging_current': {
        'register_index': 15,
        'multiplier': 0.1
    },
    'input_voltage': {
        'register_index': 5,
        'multiplier': 0.1
    },
    'load_current': {
        'register_index': 9,
        'multiplier': 1.0
    },
    'load_level': {
        'register_index': 12,
        'multiplier': 1.0
    },
    'output_power': {
        'register_index': 10,
        'multiplier': 1.0
    },
    'output_voltage': {
        'register_index': 7,
        'multiplier': 0.1
    },
    'ups_temperature': {
        'register_index': 18,
        'multiplier': 1.0
    }
}

backend = 'mqtt'
hostname = '192.168.0.1'
org = 'home'
password = ''
sensors = [
    'battery_level',
    'battery_voltage',
    'charging_current',
    'input_voltage',
    'load_current',
    'load_level',
    'output_power',
    'output_voltage',
    'ups_temperature'
]

sleep_time = 1
username = 'admin'

address = 30000
baud = 9600
id = 10
length = 26
model = 'EP3000'
order = Endian.LITTLE
parity = 'N'
stopbits = 1

# If True - do not send data to mqtt broker just print all parameters
# listed in 'attributes'
debug = False

c_boost_voltage = 28.8
c_empty_voltage = 21.0
c_float_current = 27.0
c_full_voltage = 27.2
d_empty_voltage = 21.0
d_full_voltage = 25.6

if isfile('configuration.yaml'):
    with open("configuration.yaml", 'r') as stream:
        configuration = safe_load(stream)

    debug = configuration['debug']
    backend = configuration['backend']
    sensors = configuration['sensors']
    sleep_time = configuration['run']['sleep_time']
    c_boost_voltage = configuration['charge_config']['boost_voltage']
    c_empty_voltage = configuration['charge_config']['empty_voltage']
    c_float_current = configuration['charge_config']['float_current']
    c_full_voltage = configuration['charge_config']['full_voltage']
    d_empty_voltage = configuration['discharge_config']['empty_voltage']
    d_full_voltage = configuration['discharge_config']['full_voltage']

    if backend == 'mqtt':
        hostname = configuration['mqtt']['hostname']
        auth = None
        if configuration['mqtt']['username'] and configuration['mqtt']['password']:
            auth = {
                'username': configuration['mqtt']['username'],
                'password': configuration['mqtt']['password']
            }
    elif backend == 'influx':
        hostname = configuration['influx']['hostname']
        org = configuration['influx']['org']
        token = configuration['influx']['token']
        bucket = configuration['influx']['bucket']

if backend == 'mqtt':
    sensors_definitions = []
    for sensor in sensors:
        match sensor:
            case 'output_voltage':
                sensors_definitions.append({
                    'topic': topic('output_voltage/config'),
                    'payload': dumps({
                        "name": name("Output Voltage"),
                        "device_class": "voltage",
                        "unit_of_measurement": "V",
                        "state_class": "measurement",
                        "state_topic": topic('output_voltage/state'),
                    })
                })
            case 'load_level':
                sensors_definitions.append({
                    'topic': topic('load_level/config'),
                    'payload': dumps({
                        "name": name("Load Level"),
                        "unit_of_measurement": "%",
                        "state_class": "measurement",
                        "state_topic": topic('load_level/state'),
                    })
                })
            case 'input_voltage':
                sensors_definitions.append({
                    'topic': topic('input_voltage/config'),
                    'payload': dumps({
                        "name": name("Input Voltage"),
                        "device_class": "voltage",
                        "unit_of_measurement": "V",
                        "state_class": "measurement",
                        "state_topic": topic('input_voltage/state'),
                    })
                })
            case 'battery_voltage':
                sensors_definitions.append({
                    'topic': topic('battery_voltage/config'),
                    'payload': dumps({
                        "name": name("Battery Voltage"),
                        "device_class": "voltage",
                        "unit_of_measurement": "V",
                        "state_class": "measurement",
                        "state_topic": topic('battery_voltage/state'),
                    })
                })
            case 'ups_temperature':
                sensors_definitions.append({
                    'topic': topic('ups_temperature/config'),
                    'payload': dumps({
                        "name": name("Inverter Temperature"),
                        "device_class": "temperature",
                        "unit_of_measurement": "°C",
                        "state_topic": topic('ups_temperature/state'),
                    })
                })
            case 'charging_current':
                sensors_definitions.append({
                    'topic': topic('charging_current/config'),
                    'payload': dumps({
                        "name": name("Charging Current"),
                        "device_class": "current",
                        "unit_of_measurement": "A",
                        "state_class": "measurement",
                        "state_topic": topic('charging_current/state'),
                    })
                })
            case 'battery_level':
                sensors_definitions.append({
                    'topic': topic('battery_level/config'),
                    'payload': dumps({
                        "name": name("Battery Level"),
                        "unit_of_measurement": "%",
                        "state_class": "measurement",
                        "state_topic": topic('battery_level/state'),
                    })
                })
            case 'output_power':
                sensors_definitions.append({
                    'topic': topic('output_power/config'),
                    'payload': dumps({
                        "name": name("Output Power"),
                        "device_class": "power",
                        "unit_of_measurement": "W",
                        "state_class": "measurement",
                        "state_topic": topic('output_power/state'),
                    })
                })
            case 'load_current':
                sensors_definitions.append({
                    'topic': topic('load_current/config'),
                    'payload': dumps({
                        "name": name("Load Current"),
                        "device_class": "current",
                        "unit_of_measurement": "A",
                        "state_class": "measurement",
                        "state_topic": topic('load_current/state'),
                    })
                })

client = ModbusSerialClient(
    port='/dev/ttyUSB0',
    baudrate=baud,
    parity=parity,
    stopbits=stopbits,
    timeout=10
)
client.connect()

if not client.is_socket_open():
    print("not connected")
    exit(1)

if debug:
    result = client.read_holding_registers(address, length, slave=id)
    index = 0
    for register in result.registers:
        value = result.registers[index]
        name = attributes[index]['name']
        if 'multiplier' in attributes[index]:
            value = value * attributes[index]['multiplier']
        unit = attributes[index]['unit_of_measurement']
        print(name + ' (' + unit + '): ' + str(value))
        index += 1
        if (last_index < index):
            exit(0)

if backend == 'mqtt':
    publish_multiple(sensors_definitions)
elif backend == 'influx':
    try:
        infl_client = InfluxDBClient(url=hostname, token=token, org=org)
        write_api = infl_client.write_api(write_options=SYNCHRONOUS)
    except Exception as e:
        print(e)

while True:
    if backend == 'mqtt':
        sensors_data = []
    elif backend == 'influx':
        metric = Point('Modbus').tag('Device', 'EP3000')

    result = client.read_holding_registers(address, length, slave=id)
    timestemp = time_ns()

    for sensor in sensors:
        match sensor:
            case 'charging_current':
                # Check if battery is discharging. If yes - charging_current parameter
                # is irrelevant and shows some impossible numbers
                if result.registers[2] == 1:
                    charging_current = 0
                else:
                    charging_current = get_sensor_data(sensor)

                add_sensor_data(sensor, charging_current)
                continue

            case 'battery_level':
                battery_voltage = get_sensor_data('battery_voltage')
                charging_current = get_sensor_data('charging_current')
                if (result.registers[2] == 2 and
                        charging_current > float(configuration['charge_config']['float_current'])):
                    if battery_voltage > float(configuration['charge_config']['full_voltage']):
                        battery_level = (95.0 + (battery_voltage
                                                 - float(configuration['charge_config']['full_voltage']))
                                         / (float(configuration['charge_config']['boost_voltage'])
                                            - float(configuration['charge_config']['full_voltage']))
                                         * 5.0)
                    else:
                        battery_level = ((battery_voltage
                                          - float(configuration['charge_config']['empty_voltage']))
                                         / (float(configuration['charge_config']['full_voltage'])
                                            - float(configuration['charge_config']['empty_voltage']))
                                         * 95.0)
                else:
                    if battery_voltage > float(configuration['discharge_config']['full_voltage']):
                        battery_level = 100.0
                    else:
                        battery_level = ((battery_voltage
                                          - float(configuration['discharge_config']['empty_voltage']))
                                         / (float(configuration['discharge_config']['full_voltage'])
                                            - float(configuration['discharge_config']['empty_voltage']))
                                         * 100.0)

                battery_level = round(battery_level, 1)
                add_sensor_data(sensor, battery_level)
                continue

        add_sensor_data(sensor, get_sensor_data(sensor))

    push_data()

    sleep(sleep_time)
