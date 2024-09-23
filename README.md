# Flask Serial Device Control

This project is a Flask web application that allows users to control devices (like a laser and motor) via serial communication. The application supports selecting a serial port, connecting/disconnecting devices, sending commands, and uploading a JSON file with a sequence of commands to configure the devices.

## Features

- **Device Control**: Control devices like a laser and motor using a web interface.
- **Serial Port Selection**: Choose from available serial ports, including a simulated `loop://` port.
- **Connect/Disconnect Devices**: Easily manage the connection status of devices.
- **Command Execution**: Send individual commands to devices and receive feedback.
- **JSON Upload**: Upload a JSON file containing a sequence of commands to configure devices.

## Requirements

- Python 3.x
- Flask
- pyserial

## Installation

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/yourusername/flask-serial-control.git
    cd flask-serial-control
    ```

2. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

    *If `requirements.txt` does not exist, manually install the necessary packages:*

    ```bash
    pip install flask pyserial
    ```

3. **Run the Application**:
    ```bash
    python app.py
    ```

    The application will start on `http://127.0.0.1:5000`.

## Usage

### 1. **Web Interface**

- **Device Control**:
    - Open your browser and navigate to `http://127.0.0.1:5000`.
    - Select the serial port for the device you want to control (e.g., laser or motor).
    - Connect to the selected port.
    - Send commands to the device (e.g., turn on/off, set current or speed).

- **Upload JSON File**:
    - Use the provided file upload form to upload a JSON file containing commands.
    - The JSON file should specify the device and a list of commands to be sent.
  
### 2. **JSON File Format**

The JSON file should have the following structure:

```json
{
    "device": "laser",
    "commands": [
        "LASER_ON\n",
        "LASER_SET_CURRENT 5.0\n",
        "LASER_OFF\n"
    ]
}
```

### 3. **Simulated Serial Port (`loop://`)**

- The application includes a simulated serial port (`loop://`) that echoes back commands. This is useful for testing the application without needing physical devices.

## Example JSON File

Here is an example of a JSON file to control the laser:

```json
{
    "device": "laser",
    "commands": [
        "LASER_ON\n",
        "LASER_SET_CURRENT 5.0\n",
        "LASER_OFF\n"
    ]
}
```

## Project Structure

```plaintext
.
├── app.py                  # Main Flask application
├── simulator.py            # Simulated serial device (optional, if needed)
├── templates
│   └── index.html          # HTML template for the web interface
├── static
│   └── jquery-3.6.0.min.js # JavaScript library for AJAX
└── README.md               # Project documentation
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.
