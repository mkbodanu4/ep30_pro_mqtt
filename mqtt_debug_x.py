import serial
import time
import yaml

with open("configuration.yaml", 'r') as stream:
    configuration = yaml.safe_load(stream)

while True:

    ser = serial.Serial(configuration['serial']['port'], 2400, timeout=10)

    # X

    ser.reset_input_buffer()
    ser.reset_output_buffer()
    ser.write(b"X\n")
    time.sleep(.1)
    ser.flush()
    charging_data = ser.read_until(b'\n')

    ser.close()

    charging_data = charging_data.decode("utf-8").strip()
    charging_data = charging_data.split(" ")
    print("\n")

    charging_current = float(int(charging_data[0], 16))
    print(charging_current)
    value2 = float(int(charging_data[1], 16))
    print(value2)
    value3 = float(int(charging_data[2], 16))
    print(value3)
    value4 = float(int(charging_data[3], 16))
    print(value4)

    time.sleep(.1)