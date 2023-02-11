import time
import json
import paho.mqtt.publish as publish
import yaml
from os.path import isfile

# Uncomment this section to see what is sent and recieved from Modbus client
#import logging
#logging.basicConfig()
#log = logging.getLogger()
#log.setLevel(logging.DEBUG)

from pymodbus.constants import Endian
from pymodbus.client import ModbusSerialClient
from pymodbus.register_read_message import ReadHoldingRegistersResponse

hostname = '192.168.0.1'
username = 'admin'
password = ''

# If True - do not send data to mqtt brocker just print all parameters
# listed in 'attributes'
debug = False

if ( isfile('configuration.yaml') ):
  with open("configuration.yaml", 'r') as stream:
    configuration = yaml.safe_load(stream)

  debug = configuration['debug']
  hostname = configuration['mqtt']['hostname']
  auth = None
  if configuration['mqtt']['username'] and configuration['mqtt']['password']:
    auth = {
      'username': configuration['mqtt']['username'],
      'password': configuration['mqtt']['password']
    }

model = "EP3000"
baud = 9600
stopbits = 1
parity = "N"
order = Endian.Little
address = 30000
length = 26
id = 10

attributes = [
  {
    'id' : 'MachineTypeI',
    'name' : 'Machine Type',
    'unit_of_measurement' : 't'
  },
  {
    'id' : 'SoftwareVersionI',
    'name' : 'Software Version',
    'unit_of_measurement' : 'v'
  },
  {
    'id' : 'WorkStateI',
    'name' : 'Work State',
    'unit_of_measurement' : 's'
  },
  {
    'id' : 'BatClass',
    'name' : 'Battery',
    'unit_of_measurement' : 'V'
  },
  {
    'id' : 'RatedPower',
    'name' : 'Rated Power',
    'unit_of_measurement' : 'W'
  },
  {
    'id' : 'GridVoltage',
    'name' : 'Grid Voltage',
    'unit_of_measurement' : 'V',
    'multiplier' : 0.1
  },
  {
    'id' : 'GridFrequency',
    'name' : 'Grid Frequency',
    'unit_of_measurement' : 'HZ',
    'multiplier' : 0.1
  },
  {
    'id' : 'OutputVoltage',
    'name' : 'Output Voltage',
    'unit_of_measurement' : 'V',
    'multiplier' : 0.1
  }, 
  {
    'id' : 'OutputFrequency',
    'name' : 'Output Frequency',
    'unit_of_measurement' : 'HZ',
    'multiplier' : 0.1
  },
  {
    'id' : 'LoadCurrent',
    'name' : 'Load Current',
    'unit_of_measurement' : 'A'
  },
  {
    'id' : 'LoadPower',
    'name' : 'Load Power',
    'unit_of_measurement' : 'W'
  },
  {
    'id' : 'VA',
    'name' : 'Volt/Amper',
    'unit_of_measurement' : 'VA'
  },
  {
    'id' : 'LoadPercent',
    'name' : 'Load Percent',
    'unit_of_measurement' : '%',
  },
  {
    'id' : 'BatteryTemperature',
    'name' : 'Battery Temperature',
    'unit_of_measurement' : 'C'
  },
  {
    'id' : 'BatteryVoltage',
    'name' : 'Battery Voltage',
    'unit_of_measurement' : 'V',
    'multiplier' : 0.1
  },
  {
    'id' : 'BatteryCurrent',
    'name' : 'Battery Current Charging',
    'unit_of_measurement' : 'A',
    'multiplier' : 0.1
  },
  {
    'id' : 'BuzzerState',
    'name' : 'Buzzer State',
    'unit_of_measurement' : 'on/off'
  },
  {
    'id' : 'BatterySOC',
    'name' : 'Battery State-of-Charge',
    'unit_of_measurement' : '%'
  },
  {
    'id' : 'TransformerTEMP',
    'name' : 'Inverter Temperature',
    'unit_of_measurement' : 'C'
  },
  {
    'id' : 'SystemAlarmId',
    'name' : 'System Alarm Id',
    'unit_of_measurement' : 'n'
  },
  {
    'id' : 'ChargeStageI',
    'name' : 'Charge Stage',
    'unit_of_measurement' : 'n'
  },
  {
    'id' : 'GridChargeFlagI',
    'name' : 'Grid Charge Flag',
    'unit_of_measurement' : 'n'
  },
  {
    'id' : 'GridState',
    'name' : 'Grid State',
    'unit_of_measurement' : 'n'
  }
]
last_index = len(attributes) - 1

def topic(name_value, component='sensor'):
  return 'homeassistant/' + component + '/ep30_' + name_value

def name(sensor_name, prefix='EP30 ', suffix=''):
  return prefix + sensor_name + suffix

def publish_multiple(msgs):
  try:
    publish.multiple(msgs=msgs, hostname=hostname, auth=auth)
  except Exception as e:
    print(e)


client = ModbusSerialClient(
  port = '/dev/ttyUSB0',
  baudrate = baud,
  parity = parity,
  stopbits = stopbits,
  timeout = 10
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
    if ( 'multiplier' in attributes[index] ):
      value = value * attributes[index]['multiplier']
    unit = attributes[index]['unit_of_measurement']
    print(name + ' (' + unit + '): ' + str(value))
    index += 1
    if ( last_index < index ):
      exit(0)

sensors_definitions = []
for sensor in configuration['sensors']:
  match sensor:
    case 'output_voltage':
      sensors_definitions.append({
        'topic': topic('output_voltage/config'),
        'payload': json.dumps({
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
        'payload': json.dumps({
          "name": name("Load Level"),
          "unit_of_measurement": "%",
          "state_class": "measurement",
          "state_topic": topic('load_level/state'),
        })
      })
    case 'input_voltage':
      sensors_definitions.append({
        'topic': topic('input_voltage/config'),
        'payload': json.dumps({
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
        'payload': json.dumps({
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
        'payload': json.dumps({
          "name": name("Inverter Temperature"),
          "device_class": "temperature",
          "unit_of_measurement": "°C",
          "state_topic": topic('ups_temperature/state'),
        })
      })
    case 'charging_current':
      sensors_definitions.append({
        'topic': topic('charging_current/config'),
        'payload': json.dumps({
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
        'payload': json.dumps({
          "name": name("Battery Level"),
          "unit_of_measurement": "%",
          "state_class": "measurement",
          "state_topic": topic('battery_level/state'),
        })
      })
    case 'output_power':
      sensors_definitions.append({
        'topic': topic('output_power/config'),
        'payload': json.dumps({
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
        'payload': json.dumps({
          "name": name("Load Current"),
          "device_class": "current",
          "unit_of_measurement": "A",
          "state_class": "measurement",
          "state_topic": topic('load_current/state'),
        })
      })

while True:
  publish_multiple(sensors_definitions)

  sensors_data = []

  result = client.read_holding_registers(address, length, slave=id)

  for sensor in configuration['sensors']:
    match sensor:
      case 'output_voltage':
        output_voltage = format(round(result.registers[7] * 0.1, 1), '.1f')
        sensors_data.append({
          'topic': topic('output_voltage/state'),
          'payload': str(output_voltage)
        })

      case 'load_level':
        load_level = result.registers[12]
        sensors_data.append({
          'topic': topic('load_level/state'),
          'payload': str(load_level)
        })

      case 'input_voltage':
        input_voltage = format(round(result.registers[5] * 0.1, 1), '.1f')
        sensors_data.append({
          'topic': topic('input_voltage/state'),
          'payload': str(input_voltage)
        })

      case 'battery_voltage':
        battery_voltage = format(round(result.registers[14] * 0.1, 1), '.1f')
        sensors_data.append({
          'topic': topic('battery_voltage/state'),
          'payload': str(battery_voltage)
        })

      case 'ups_temperature':
        ups_temperature = result.registers[18]
        sensors_data.append({
          'topic': topic('ups_temperature/state'),
          'payload': str(ups_temperature)
        })

      case 'charging_current':
        # Check if battery is discharging. If yes - charging_current parameter
        # is irrelevant and shows some impossible numbers
        if ( result.registers[2] == 1 ):
          charging_current = 0
        else:
          charging_current = format(round(result.registers[15] * 0.1, 1), '.1f')
        sensors_data.append({
          'topic': topic('charging_current/state'),
          'payload': str(charging_current)
        })

      case 'battery_level':
        battery_level = result.registers[17]
        sensors_data.append({
          'topic': topic('battery_level/state'),
          'payload': str(battery_level)
        })

      case 'output_power':
        output_power = result.registers[10]
        sensors_data.append({
          'topic': topic('output_power/state'),
          'payload': str(output_power)
        })

      case 'load_current':
        load_current = result.registers[9]
        sensors_data.append({
          'topic': topic('load_current/state'),
          'payload': str(load_current)
        })

  publish_multiple(sensors_data)

  time.sleep(1)
