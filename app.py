from flask import Flask, render_template, request, jsonify
import serial
import serial.tools.list_ports

app = Flask(__name__)

# Initialize serial_info dictionary
serial_info = {
    'laser': {
        'ports': [],  # This will be populated by the list_serial_ports() function
        'selected_port': None,
        'status': 'Disconnected'
    },
    'motor': {
        'ports': [],  # This will be populated by the list_serial_ports() function
        'selected_port': None,
        'status': 'Disconnected'
    }
}

# Function to list available serial ports, including the simulated loopback port
def list_serial_ports():
    ports = [port.device for port in serial.tools.list_ports.comports()]
    ports.append('loop://')  # Add the simulated loopback port
    return ports

@app.route('/')
def index():
    serial_info = {
        'laser': {
            'ports': list_serial_ports(),
            'selected_port': None,
            'status': 'Disconnected'
        },
        'motor': {
            'ports': list_serial_ports(),
            'selected_port': None,
            'status': 'Disconnected'
        }
    }
    return render_template('index.html', serial_info=serial_info)

@app.route('/connect', methods=['POST'])
def connect_serial():
    device = request.form.get('device')
    port = request.form.get('port')
    baudrate = 9600  # You can allow this to be selected as well
    timeout = 1

    try:
        ser = serial.serial_for_url(port, baudrate=baudrate, timeout=timeout)
        ser.flush()
        serial_info[device]['selected_port'] = port
        serial_info[device]['status'] = 'Connected'
        # Store the serial connection for later use
        if device == 'laser':
            app.config['LASER_SER'] = ser
        elif device == 'motor':
            app.config['MOTOR_SER'] = ser
    except serial.SerialException as e:
        serial_info[device]['selected_port'] = None
        serial_info[device]['status'] = f'Error: {str(e)}'

    return jsonify(serial_info[device])

@app.route('/disconnect', methods=['POST'])
def disconnect_serial():
    device = request.form.get('device')
    if device == 'laser' and 'LASER_SER' in app.config:
        app.config['LASER_SER'].close()
        del app.config['LASER_SER']
    elif device == 'motor' and 'MOTOR_SER' in app.config:
        app.config['MOTOR_SER'].close()
        del app.config['MOTOR_SER']
    
    serial_info[device]['status'] = 'Disconnected'
    serial_info[device]['selected_port'] = None
    return jsonify(serial_info[device])

@app.route('/control', methods=['POST'])
def control_device():
    device = request.form.get('device')
    action = request.form.get('action')

    if device == 'laser':
        ser = app.config.get('LASER_SER')
    elif device == 'motor':
        ser = app.config.get('MOTOR_SER')
    else:
        return jsonify({"error": "Invalid device"}), 400

    if not ser or not ser.is_open:
        return jsonify({"error": "Serial connection not established"}), 400

    try:
        if device == 'laser':
            if action == 'on':
                ser.write(b'LASER_ON\n')
            elif action == 'off':
                ser.write(b'LASER_OFF\n')
            elif action == 'set_current':
                current = float(request.form.get('current'))
                command = f'LASER_SET_CURRENT {current}\n'
                ser.write(command.encode('utf-8'))
            else:
                return jsonify({"error": "Invalid action"}), 400
        elif device == 'motor':
            if action == 'on':
                ser.write(b'MOTOR_ON\n')
            elif action == 'off':
                ser.write(b'MOTOR_OFF\n')
            elif action == 'set_speed':
                speed = int(request.form.get('speed'))
                command = f'MOTOR_SET_SPEED {speed}\n'
                ser.write(command.encode('utf-8'))
            else:
                return jsonify({"error": "Invalid action"}), 400
        
        # Read response from the simulated device
        response = ser.readline().decode('utf-8').strip()
        return jsonify({"success": True, "response": response})
        
    except serial.SerialException as e:
        return jsonify({"error": f"Serial error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
