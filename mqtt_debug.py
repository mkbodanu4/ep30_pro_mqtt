import serial
import time
import yaml

with open("configuration.yaml", 'r') as stream:
    configuration = yaml.safe_load(stream)

ser = serial.Serial(configuration['serial']['port'], 2400, timeout=10)

# F

ser.reset_input_buffer()
ser.reset_output_buffer()
ser.write(b"F\n")
time.sleep(.1)
ser.flush()
details_data = ser.read_until(b'\r')
print(details_data)

time.sleep(.1)

# Q1

ser.reset_input_buffer()
ser.reset_output_buffer()
ser.write(b"Q1\n")
time.sleep(.1)
ser.flush()
data = ser.read_until(b'\r')
print(data)

time.sleep(.1)

# G?

ser.reset_input_buffer()
ser.reset_output_buffer()
ser.write(b"G?\n")
time.sleep(.1)
ser.flush()
message_data = ser.read_until(b'\r')
print(message_data)

time.sleep(.1)

# D

ser.reset_input_buffer()
ser.reset_output_buffer()
ser.write(b"D\n")
time.sleep(.1)
ser.flush()
is_charging_data = ser.read(3)
print(is_charging_data)


time.sleep(.1)

# X

ser.reset_input_buffer()
ser.reset_output_buffer()
ser.write(b"X\n")
time.sleep(.1)
ser.flush()
charging_data = ser.read_until(b'\n')
print(charging_data)

print("\n")

ser.close()

charging_data = charging_data.decode("utf-8").strip()
charging_data = charging_data.split(" ")
print(charging_data)
charging_current = float(int(charging_data[0], 16))
print(charging_current)
value2 = float(int(charging_data[1], 16))
print(value2)
value3 = float(int(charging_data[2], 16))
print(value3)
value4 = float(int(charging_data[3], 16))
print(value4)
