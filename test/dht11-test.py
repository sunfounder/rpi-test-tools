import argparse
import board
import adafruit_dht

parser = argparse.ArgumentParser(description='Read temperature and humidity from DHT11 sensor.')
parser.add_argument('--pin', '-p', type=int, default=18, help='GPIO pin number (default: 4)')
parser.add_argument('--model', '-m', type=str, default='dht11', choices=['dht11', 'dht22', 'am2302'], help='DHT model (default: dht11)')
args = parser.parse_args()

sensor = None
if args.model == 'dht11':
    sensor = adafruit_dht.DHT11
elif args.model == 'dht22':
    sensor = adafruit_dht.DHT22
elif args.model == 'am2302':
    sensor = adafruit_dht.AM2302

pin = getattr(board, f"D{args.pin}")

print(f"Reading temperature and humidity from {sensor} sensor on pin {pin}...")

dhtDevice = sensor(pin, use_pulseio=False)

for i in range(10):
    try:
        temperature = dhtDevice.temperature
        print(f"Temperature: {temperature}°C")
    except RuntimeError as error:
        print(f"Failed to read temperature: {error}")

