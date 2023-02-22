#!/usr/bin/env python3

from sys import stdin

from line_protocol_parser import parse_line
from influx_line_protocol import Metric

from os.path import isfile
from yaml import safe_load

discharge_full_voltage = 25.6
discharge_empty_voltage = 21.0

charge_float_current = 27.0
charge_full_voltage = 27.2
charge_boost_voltage = 28.8
charge_empty_voltage = 21.0

if ( isfile('configuration.yaml') ):
  with open("configuration.yaml", 'r') as stream:
    configuration = safe_load(stream)
  discharge_full_voltage  = configuration['discharge_config']['full_voltage']
  discharge_empty_voltage = configuration['discharge_config']['empty_voltage']
  charge_float_current    = configuration['charge_config']['float_current']
  charge_full_voltage     = configuration['charge_config']['full_voltage']
  charge_boost_voltage    = configuration['charge_config']['boost_voltage']
  charge_empty_voltage    = configuration['charge_config']['empty_voltage']

while True:
  for line in stdin:
    data = parse_line(line)

    if data['measurement'] != 'modbus':
      print(line)
      continue

    # convert all to float
    battery_charging = data['fields']['battery_charging'] * 1.0
    battery_voltage  = data['fields']['battery_voltage'] * 0.1
    charging_current = data['fields']['battery_charging'] * 0.1
    grid_voltage     = data['fields']['grid_voltage'] * 0.1
    load_current     = data['fields']['load_current'] * 1.0
    load_percent     = data['fields']['load_percent'] * 1.0
    load_power       = data['fields']['load_power'] * 1.0
    output_voltage   = data['fields']['output_voltage'] * 0.1
    ups_tempetature  = data['fields']['ups_tempetature'] * 1.0

    grid_status = data['fields']['grid_status']

    # Check if battery is discharging. If yes - charging_current parameter
    # is irrelevant and shows some impossible numbers
    if grid_status == 1:
      charging_current = 0.0

    # Calculate battery level
    if (grid_status == 2 and charging_current > charge_float_current):
      if battery_voltage > charge_full_voltage:
        battery_level = ( (95.0 +
          (battery_voltage - charge_full_voltage)
          / charge_boost_voltage
          - charge_full_voltage)
          * 5.0)
      else:
        battery_level = ( (battery_voltage - charge_empty_voltage)
        / ( charge_full_voltage - charge_empty_voltage)
        * 95.0 )
    else:
      if battery_voltage > discharge_full_voltage:
        battery_level = 100.0
      else:
        battery_level = ( (battery_voltage - discharge_empty_voltage)
        / (discharge_full_voltage - discharge_empty_voltage)
        * 100.0 )

    metric = Metric("Modbus")
    metric.add_tag('Device', 'EP3000')
    metric.add_value('battery_level', battery_level)
    metric.add_value('battery_voltage', battery_voltage)
    metric.add_value('charging_current', charging_current)
    metric.add_value('input_voltage', grid_voltage)
    metric.add_value('load_current', load_current)
    metric.add_value('load_level', load_percent)
    metric.add_value('output_power', load_power)
    metric.add_value('output_voltage', output_voltage)
    metric.add_value('ups_temperature', ups_tempetature)
    metric.with_timestamp(data['time'])

    print(metric)

