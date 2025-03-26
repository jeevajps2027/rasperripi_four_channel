import asyncio
import serial.tools.list_ports
import serial
from channels.generic.websocket import AsyncWebsocketConsumer
import json
import threading
from asgiref.sync import async_to_sync

class SerialConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'serial_group'

        # Add the consumer to the group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Remove the consumer from the group on disconnect
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        command = data.get('command')

        # Handle 'start_serial' command to initiate serial communication
        if command == 'start_serial':
            await self.start_serial_communication(data)

    async def start_serial_communication(self, data):
        com_port = data.get('com_port')
        baud_rate = data.get('baud_rate')
        parity = data.get('parity')
        stopbit = data.get('stopbit')
        databit = data.get('databit')

        # Configure serial port and start communication
        if self.configure_serial_port(com_port, baud_rate, parity, stopbit, databit):
            # Send initial message (optional)
            command_message = "MMMMMMMMMM"
            self.ser.write(command_message.encode('ASCII'))

            # Start the serial read thread
            self.serial_thread = threading.Thread(target=self.serial_read_thread)
            self.serial_thread.daemon = True  # Ensure thread ends when the main program exits
            self.serial_thread.start()

    def get_available_com_ports(self):
        # Return a list of available serial ports
        return [port.device for port in serial.tools.list_ports.comports()]

    def configure_serial_port(self, com_port, baud_rate, parity, stopbits, bytesize):
        try:
            # Validate that each parameter is not None
            if com_port is None or baud_rate is None or parity is None or stopbits is None or bytesize is None:
                print("One or more required parameters are missing.")
                return False

            # Initialize the serial port with validated parameters
            self.ser = serial.Serial(
                port=com_port,
                baudrate=int(baud_rate),
                bytesize=int(bytesize),
                timeout=None,
                stopbits=float(stopbits),
                parity=parity[0].upper()  # Handle the first letter of parity
            )
            print(f"Connected to {com_port} successfully.")
            return True
        except ValueError as e:
            print(f"Invalid parameter type: {e}")
            return False
        except serial.SerialException as e:
            print(f"Failed to open port {com_port}: {str(e)}")
            return False  # Return False if port couldn't be opened

    def serial_read_thread(self):
        try:
            accumulated_data = ""
            while True:
                if self.ser and self.ser.is_open and self.ser.in_waiting > 0:
                    received_data = self.ser.read(self.ser.in_waiting).decode('ASCII')
                    accumulated_data += received_data

                    # Process the accumulated data
                    if '\r' in accumulated_data:
                        messages = accumulated_data.split('\r')
                        for message in messages:
                            if message.strip():  # Skip empty messages
                                async_to_sync(self.channel_layer.group_send)(  # Send message to WebSocket
                                    self.group_name,
                                    {
                                        'type': 'serial_message',
                                        'message': message.strip()
                                    }
                                )
                        accumulated_data = ""  # Clear accumulated data after processing

                    # Debug: Print received data
                    print(received_data, end='', flush=True)
        except Exception as e:
            print(f"Error in serial read thread: {str(e)}")
        finally:
            # Ensure the serial port is closed properly
            if self.ser and self.ser.is_open:
                self.ser.close()

    async def serial_message(self, event):
        # Send the serial message to WebSocket
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
