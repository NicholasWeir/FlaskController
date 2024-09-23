import serial
import threading
import time

# Simulated Serial Device Class
class SimulatedSerialDevice:
    def __init__(self, port, baudrate, timeout):
        # Initialize the loopback serial port
        self.ser = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
        self.ser.flush()  # Clear the input and output buffer
        self.running = True
        self.laser_state = 'off'
        self.laser_current = 0.0

    def start(self):
        # Start the simulated device loop in a background thread
        thread = threading.Thread(target=self.device_loop, daemon=True)
        thread.start()
        return thread

    def device_loop(self):
        while self.running:
            if self.ser.in_waiting > 0:
                # Read the command sent to the emulated device
                command = self.ser.readline().decode('utf-8').strip()
                response = self.process_command(command)
                if response:
                    self.ser.write(response.encode('utf-8'))
            time.sleep(0.1)

    def process_command(self, command):
        print(f"Received command: {command}")
        
        if command == 'LASER_ON':
            self.laser_state = 'on'
            return "Laser is ON\n"
        elif command == 'LASER_OFF':
            self.laser_state = 'off'
            return "Laser is OFF\n"
        elif command.startswith('LASER_SET_CURRENT'):
            try:
                _, current_value = command.split()
                self.laser_current = float(current_value)
                return f"Laser current set to {self.laser_current} A\n"
            except ValueError:
                return "Invalid current value\n"
        else:
            return f"Unknown command: {command}\n"

    def stop(self):
        self.running = False
        self.ser.close()

# Test Client to Send Commands to the Simulated Serial Device
def test_client(device):
    time.sleep(1)  # Give the device time to start

    # Send test commands
    device.ser.write(b'LASER_ON\n')
    print(device.ser.readline().decode('utf-8'))

    device.ser.write(b'LASER_SET_CURRENT 5.0\n')
    print(device.ser.readline().decode('utf-8'))

    device.ser.write(b'LASER_OFF\n')
    print(device.ser.readline().decode('utf-8'))

    device.ser.write(b'LASER_SET_CURRENT invalid_value\n')
    print(device.ser.readline().decode('utf-8'))

    device.ser.write(b'UNKNOWN_COMMAND\n')
    print(device.ser.readline().decode('utf-8'))

# Example Usage
if __name__ == "__main__":
    # Initialize the simulated serial device
    simulated_device = SimulatedSerialDevice(port='COM3', baudrate=9600, timeout=1)
    
    # Start the device simulation in a background thread
    simulated_device.start()

    # Run the test client to interact with the simulated device
    test_client(simulated_device)

    # Stop the simulated device
    simulated_device.stop()