from pymodbus.constants import Endian
from pymodbus.client import ModbusSerialClient
from pymodbus.register_read_message import ReadHoldingRegistersResponse
import logging

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

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
        'id': 'work state',
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
        'id': 'rated power',
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
        'unit_of_measurement': 'HZ',
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
        'unit_of_measurement': 'HZ',
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
        'id': 'buzzer state',
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
            0: "",
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
            0: 'inverter over temperature',
            1: 'battery over temperature',
            2: 'Battery voltage is too high',
            3: 'Battery voltage is too Low',
            4: 'Over load',
            5: "",
            6: "",
            7: "",
            8: "",
            9: "",
            10: "",
            11: "",
            12: "",
            13: "",
            14: "",
            15: ""
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

address = 30000
baud = 9600
id = 10
length = 26
model = 'EP3000'
order = Endian.LITTLE
parity = 'N'
stopbits = 1

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

result = client.read_holding_registers(address, length, slave=id)


for sensor in sensors:
    register_index = sensor['register_index']
    
    if register_index is None:
        continue
    
    name = sensor['name']

    value = result.registers[register_index]
    if 'multiplier' in sensor:
        value = value * sensor['multiplier']
    if 'options' in sensor:
        value = sensor['options'][value]
    if 'prefix' in sensor:
        value = sensor['prefix'] + str(value)
    if 'suffix' in sensor:
        value = str(value) + sensor['suffix']

    unit = ''
    if 'unit_of_measurement' in sensor:
        unit = sensor['unit_of_measurement']

    print(str(register_index) + ': ' + name + ' (' + unit + '): ' + str(value))
