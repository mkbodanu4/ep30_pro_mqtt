from json import dumps
from os.path import isfile
from time import sleep, time_ns
from yaml import safe_load

import paho.mqtt.publish as publish

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from pymodbus.constants import Endian
from pymodbus.client import ModbusSerialClient


def topic(name_value, component='sensor'):
    return 'homeassistant/' + component + '/ep30_' + name_value


def name(sensor_name, prefix='EP30 ', suffix=''):
    return prefix + sensor_name + suffix


def publish_multiple(msgs):
    try:
        publish.multiple(msgs=msgs, hostname=hostname, auth=auth)
    except Exception as e:
        print(e)


def add_sensor_data(id, value):
    if configuration['backend'] == 'mqtt':
        sensors_data.append({
            'topic': topic(str(id) + '/state'),
            'payload': str(value)
        })
    elif configuration['backend'] == 'influx':
        metric.field(name, float(value))


def get_sensor_data(sensor):
    if sensor is None:
        return 0.0

    value = result.registers[int(sensor['register_index'])]
    if 'multiplier' in sensor:
        value = value * float(sensor['multiplier'])

    if 'options' in sensor:
        value = sensor['options'][value]
    elif 'prefix' in sensor:
        value = sensor['prefix'] + str(value)
    elif 'suffix' in sensor:
        value = str(value) + sensor['suffix']
    else:
        value = float(format(round(value, 1), '.1f'))

    return value


def get_sensor_data_by_id(id):
    return get_sensor_data(next(
        (sensor for sensor in sensors if sensor['id'] == id),
        None))

sensors = [
    {
        'register_index': None,
        'multiplier': 1.0,
        'id': 'battery_level',
        'name': 'Battery Level',
        'unit_of_measurement': '%',
        'state_class': 'measurement',
        'device_class': 'battery'
    },
    {
        'register_index': 0,
        'multiplier': 1.0,
        'remoteId': 'MachineTypeI',
        'id': 'machine_type',
        'name': 'Machine Type',
        'options': {
            0: 'EP2000PRO',
            1: "",
            2: 'PV2000PRO',
            3: 'EP3300'
        }
    },
    {
        'register_index': 1,
        'multiplier': 1.0,
        'remoteId': 'SoftwareVersionI',
        'id': 'software_version',
        'name': 'Software Version',
        'prefix': '166-00',
        'suffix': '',
    },
    {
        'register_index': 2,
        'multiplier': 1.0,
        'remoteId': 'WorkStateI',
        'id': 'work_state',
        'name': 'Work State',
        'options': {
            0: 'SELF_CHECK',
            1: 'BACKUP',
            2: 'LINE',
            3: 'STOP',
            4: 'CHARGER',
            5: 'SOFT_START',
            6: 'POWER_OFF',
            7: 'STANDBY',
            8: 'DEBUG'
        }
    },
    {
        'register_index': 3,
        'multiplier': 1.0,
        'remoteId': 'BatClass',
        'id': 'battery',
        'name': 'Battery',
        'unit_of_measurement': 'V',
        'device_class': 'voltage'
    },
    {
        'register_index': 4,
        'multiplier': 1.0,
        'remoteId': 'RatedPower',
        'id': 'rated_power',
        'name': 'Rated Power',
        'unit_of_measurement': 'W',
        'device_class': 'power'
    },
    {
        'register_index': 5,
        'multiplier': 0.1,
        'remoteId': 'GridVoltage',
        'id': 'input_voltage',
        'name': 'Grid Voltage',
        'unit_of_measurement': 'V',
        'state_class': 'measurement',
        'device_class': 'voltage'
    },
    {
        'register_index': 6,
        'multiplier': 0.1,
        'remoteId': 'GridFrequency',
        'id': 'input_frequency',
        'name': 'Grid Frequency',
        'unit_of_measurement': 'Hz',
        'state_class': 'measurement',
        'device_class': 'frequency'
    },
    {
        'register_index': 7,
        'multiplier': 0.1,
        'remoteId': 'OutputVoltage',
        'id': 'output_voltage',
        'name': 'Output Voltage',
        'unit_of_measurement': 'V',
        'state_class': 'measurement',
        'device_class': 'voltage'
    },
    {
        'register_index': 8,
        'multiplier': 0.1,
        'remoteId': 'OutputFrequency',
        'id': 'output_frequency',
        'name': 'Output Frequency',
        'unit_of_measurement': 'Hz',
        'state_class': 'measurement',
        'device_class': 'frequency'
    },
    {
        'register_index': 9,
        'multiplier': 0.1,
        'remoteId': 'LoadCurrent',
        'id': 'load_current',
        'name': 'Load Current',
        'unit_of_measurement': 'A',
        'state_class': 'measurement',
        'device_class': 'current'
    },
    {
        'register_index': 10,
        'multiplier': 1.0,
        'remoteId': 'LoadPower',
        'id': 'output_power',
        'name': 'Load Power',
        'unit_of_measurement': 'W',
        'state_class': 'measurement',
        'device_class': 'power'
    },
    {
        'register_index': 12,
        'multiplier': 1.0,
        'remoteId': 'LoadPercent',
        'id': 'load_level',
        'name': 'Load Percent',
        'unit_of_measurement': '%',
        'state_class': 'measurement'
    },
    {
        'register_index': 14,
        'multiplier': 0.1,
        'remoteId': 'BatteryVoltage',
        'id': 'battery_voltage',
        'name': 'Battery Voltage',
        'unit_of_measurement': 'V',
        'state_class': 'measurement',
        'device_class': 'voltage'
    },
    {
        'register_index': 15,
        'multiplier': 0.1,
        'remoteId': 'BatteryCurrent',
        'id': 'charging_current',
        'name': 'Battery Current Charging',
        'unit_of_measurement': 'A',
        'state_class': 'measurement',
        'device_class': 'current'
    },
    {
        'register_index': 16,
        'multiplier': 1.0,
        'remoteId': 'BatteryTemperature',
        'id': 'battery_temperature',
        'name': 'Battery temperature',
        'unit_of_measurement': '°C',
        'state_class': 'measurement',
        'device_class': 'temperature'
    },
    {
        'register_index': 17,
        'multiplier': 1.0,
        'remoteId': 'BatterySOC',
        'id': 'battery_soc',
        'name': 'Battery State-of-Charge',
        'unit_of_measurement': '%',
        'state_class': 'measurement',
        'device_class': 'battery'
    },
    {
        'register_index': 18,
        'multiplier': 1.0,
        'remoteId': 'TransformerTEMP',
        'id': 'ups_temperature',
        'name': 'Inverter Temperature',
        'unit_of_measurement': '°C',
        'state_class': 'measurement',
        'device_class': 'temperature'
    },
    {
        'register_index': 20,
        'multiplier': 1.0,
        'remoteId': 'BuzzerStateI',
        'id': 'buzzer_state',
        'name': 'Buzzer State',
        'options': {
            0: 'Normal',
            1: 'Silence'
        }
    },
    {
        'register_index': 21,
        'multiplier': 1.0,
        'remoteId': 'SystemFaultId',
        'id': 'system_fault',
        'name': 'System Fault',
        'options': {
            0: "OK",
            1: 'fan error',
            2: 'Over temperature',
            3: 'Battery voltage is too high',
            4: 'Battery voltage is too Low',
            5: 'short',
            6: 'Inverter output voltage is high',
            7: 'Over load',
            11: 'Main relay failed',
            28: 'rated load recognition failed',
            41: 'Inverter grid voltage is low',
            42: 'Inverter grid voltage is high',
            43: 'Inverter grid under frequency',
            44: 'Inverter grid over frequency',
            51: 'Over current',
            58: 'Inverter output voltage is low'
        }
    },
    {
        'register_index': 22,
        'multiplier': 1.0,
        'remoteId': 'SystemAlarmId',
        'id': 'system_alarm',
        'name': 'System Alarm',
        'options': {
            0: "OK",
            1: 'inverter over temperature',
            2: 'battery over temperature',
            3: 'Battery voltage is too high',
            4: 'Battery voltage is too Low',
            5: 'Over load',
            6: "",
            7: "",
            8: "",
            9: "",
            10: "",
            11: "",
            12: "",
            13: "",
            14: "",
            15: "",
            16: ""
        }
    },
    {
        'register_index': 23,
        'multiplier': 1.0,
        'remoteId': 'ChargeStageI',
        'id': 'charge_stage',
        'name': 'Charge Stage',
        'options': {
            0: 'cc',
            1: 'cv',
            2: 'fv'
        }
    },
    {
        'register_index': 24,
        'multiplier': 1.0,
        'remoteId': 'GridChargeFlagI',
        'id': 'grid_charge_flag',
        'name': 'Grid Charge Flag',
        'options': {
            0: 'Grid no charge',
            1: 'Grid charge'
        }
    },
    {
        'register_index': 25,
        'multiplier': 1.0,
        'remoteId': 'GridState',
        'id': 'grid_state',
        'name': 'Grid State',
        'options': {
            0: 'Disconnected',
            1: 'Connected',
            2: 'Warning'
        }
    }
]

# modbus
baud = 9600
parity = 'N'
stopbits = 1
address = 30000
slave_id = 10
length = 26

# All magic starts here

if not isfile('configuration.yaml'):
    print("Configuration file missing")
    exit(1)

with open("configuration.yaml", 'r') as stream:
    configuration = safe_load(stream)

client = ModbusSerialClient(
    port=configuration['serial']['port'],
    baudrate=baud,
    parity=parity,
    stopbits=stopbits,
    timeout=10
)
client.connect()

if not client.is_socket_open():
    print("Modbus not connected")
    exit(1)

if configuration['backend'] == 'mqtt':
    hostname = configuration['mqtt']['hostname']
    auth = None
    if configuration['mqtt']['username'] and configuration['mqtt']['password']:
        auth = {
            'username': configuration['mqtt']['username'],
            'password': configuration['mqtt']['password']
        }
elif configuration['backend'] == 'influx':
    hostname = configuration['influx']['hostname']
    org = configuration['influx']['org']
    token = configuration['influx']['token']
    bucket = configuration['influx']['bucket']

    try:
        infl_client = InfluxDBClient(url=hostname, token=token, org=org)
        write_api = infl_client.write_api(write_options=SYNCHRONOUS)
    except Exception as e:
        print(e)

while True:

    if configuration['backend'] == 'mqtt':
        sensors_definitions = []

        for sensor in sensors:
            payload = {
                "name": name(sensor['name']),
                "state_topic": topic(sensor['id'] + '/state'),
            }

            if "device_class" in sensor:
                payload["device_class"] = sensor['device_class']

            if "unit_of_measurement" in sensor:
                payload["unit_of_measurement"] = sensor['unit_of_measurement']

            if "state_class" in sensor:
                payload["state_class"] = sensor['state_class']

            sensors_definitions.append({
                'topic': topic(sensor['id'] + '/config'),
                'payload': dumps(payload)
            })

        publish_multiple(sensors_definitions)

    sleep(configuration['run']['sleep_time'])

    sensors_data = []

    if configuration['backend'] == 'influx':
        metric = Point('Modbus').tag('Device', 'EP3000')

    result = client.read_holding_registers(address=address, count=length, slave=slave_id)
    timestamp = time_ns()

    for sensor in sensors:
        match sensor['id']:
            case 'charging_current':
                # Check if battery is discharging. If yes - charging_current parameter
                # is irrelevant and shows some impossible numbers
                if result.registers[2] == 1:
                    charging_current = 0
                else:
                    charging_current = get_sensor_data(sensor)

                add_sensor_data(sensor['id'], charging_current)
                continue

            case 'battery_level':
                battery_voltage = get_sensor_data_by_id('battery_voltage')
                charging_current = get_sensor_data_by_id('charging_current')
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
                add_sensor_data(sensor['id'], battery_level)
                continue

        add_sensor_data(sensor['id'], get_sensor_data(sensor))

    if configuration['backend'] == 'mqtt':
        publish_multiple(sensors_data)
    elif configuration['backend'] == 'influx':
        metric.time(timestamp)
        try:
            write_api.write(bucket=bucket, record=metric)
        except Exception as e:
            print(e)

    sleep(.1)
