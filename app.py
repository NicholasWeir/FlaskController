import logging
from flask import Flask, render_template, request, jsonify
import serial
import serial.tools.list_ports
import json

app = Flask(__name__)

# Configure the logger
logging.basicConfig(level=logging.INFO, filename='app.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

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
    # Update available ports for each device
    serial_info['laser']['ports'] = list_serial_ports()
    serial_info['motor']['ports'] = list_serial_ports()
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

        logging.info(f"{device.capitalize()} connected to {port}")
    except serial.SerialException as e:
        serial_info[device]['selected_port'] = None
        serial_info[device]['status'] = f'Error: {str(e)}'
        logging.error(f"Failed to connect {device} to {port}: {str(e)}")

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
    logging.info(f"{device.capitalize()} disconnected")
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
        logging.error(f"Invalid device specified: {device}")
        return jsonify({"error": "Invalid device"}), 400

    if not ser or not ser.is_open:
        logging.error(f"Attempted to control {device} without an established connection")
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
                logging.error(f"Invalid action specified for {device}: {action}")
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
                logging.error(f"Invalid action specified for {device}: {action}")
                return jsonify({"error": "Invalid action"}), 400

        response = ser.readline().decode('utf-8').strip()
        logging.info(f"Command '{action}' executed on {device} with response: {response}")
        return jsonify({"success": True, "response": response})
    except serial.SerialException as e:
        logging.error(f"Serial error while controlling {device}: {str(e)}")
        return jsonify({"error": f"Serial error: {str(e)}"}), 500

@app.route('/manual_command', methods=['POST'])
def manual_command():
    device = request.form.get('device')
    command = request.form.get('command')

    if device == 'laser':
        ser = app.config.get('LASER_SER')
    elif device == 'motor':
        ser = app.config.get('MOTOR_SER')
    else:
        logging.error(f"Invalid device specified for manual command: {device}")
        return jsonify({"error": "Invalid device"}), 400

    if not ser or not ser.is_open:
        logging.error(f"Attempted to send manual command to {device} without an established connection")
        return jsonify({"error": "Serial connection not established"}), 400

    try:
        ser.write((command + '\n').encode('utf-8'))
        response = ser.readline().decode('utf-8').strip()
        logging.info(f"Manual command '{command}' sent to {device} with response: {response}")
        return jsonify({"response": response})
    except serial.SerialException as e:
        logging.error(f"Serial error while sending manual command to {device}: {str(e)}")
        return jsonify({"error": f"Serial error: {str(e)}"}), 500

@app.route('/upload', methods=['POST'])
def upload_json():
    if 'file' not in request.files:
        logging.error("No file part in upload request")
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        logging.error("No file selected for upload")
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.json'):
        try:
            commands = json.load(file)
            device = commands.get('device')
            if device not in ['laser', 'motor']:
                logging.error(f"Invalid device specified in JSON: {device}")
                return jsonify({"error": "Invalid device specified in JSON"}), 400

            ser = app.config.get(f'{device.upper()}_SER')
            if not ser or not ser.is_open:
                logging.error(f"Attempted to execute JSON commands on {device} without an established connection")
                return jsonify({"error": "Serial connection not established"}), 400

            responses = []
            for command in commands.get('commands', []):
                ser.write(command.encode('utf-8'))
                response = ser.readline().decode('utf-8').strip()
                responses.append({"command": command, "response": response})
                logging.info(f"JSON command '{command}' executed on {device} with response: {response}")

            return jsonify({"success": True, "responses": responses})
        
        except json.JSONDecodeError:
            logging.error("Invalid JSON file uploaded")
            return jsonify({"error": "Invalid JSON file"}), 400
    else:
        logging.error("Uploaded file is not a JSON file")
        return jsonify({"error": "File must be a JSON"}), 400

if __name__ == '__main__':
    app.run(debug=True)
