"""
File: USBmessage.py
Author: Tomas Kotian
Date: 15.5.2024
Description: Process format messages via USB to TMCM-6110
"""
import serial.tools.list_ports

class Message_tx:
    def __init__(self, address: bytes, cmd_n: bytes, type_n: bytes, motor_bank: bytes, value_32b: int):
        """
        Initializes a transmission message.

        Args:
            address (bytes): Address byte of the message.
            cmd_n (bytes): Command byte of the message.
            type_n (bytes): Type byte of the message.
            motor_bank (bytes): Motor bank byte of the message.
            value_32b (int): 32-bit value of the message.

        """
        self.address = address
        self.cmd_n = cmd_n
        self.type_n = type_n
        self.motor_bank = motor_bank
        self.value_32b = value_32b
        self.check_sum = self.checksum()
        self.tmcl_cmd = self.get_cmd()
    
    def checksum(self):
        """
        Calculates the checksum for the message.

        Returns:
            int: The calculated checksum value.

        """
        value_sum = sum(list(self.value_32b.to_bytes(4, "big", signed=True)))
        return sum([self.address, self.cmd_n, self.type_n, self.motor_bank, value_sum]) & 0xFF
    
    def get_cmd(self):
        """
        Generates the command bytes list.

        Returns:
            list: The command bytes list.

        """
        bytes_list = [self.address, self.cmd_n, self.type_n, self.motor_bank] 
        bytes_list.extend(self.to_list())
        bytes_list.append(self.check_sum)
        return bytes_list

    def to_list(self):
        """
        Converts the 32-bit value to a list of bytes.

        Returns:
            list: The list of bytes.

        """
        return list(self.value_32b.to_bytes(4, "big", signed=True))
    
class Message_rx:
    def __init__(self, message: list[int]):
        """
        Initializes a received message.

        Args:
            message (list[int]): The received message.

        """
        self.address = message[0]
        self.module = message[1]
        self.status = message[2]
        self.cmd_n = message[3]
        self.value_32b = int.from_bytes(bytes(message[4:8]), byteorder='big', signed=True) 
        self.check_sum = message[8]
        self.tmcl_cmd = message

class Serial_comunication:
    def __init__(self):
        """
        Initializes serial communication.

        """
        self.ports_dict = {}
        self.error = {}
        self.reply = Message_rx([0, 0, 0, 0, 0, 0, 0, 0, 0])

        self.find_ports()

    def find_ports(self):
        """
        Finds available ports and their serial numbers.

        """
        com_ports = serial.tools.list_ports.comports()
        self.ports_dict = {com.name: com.serial_number for com in com_ports}

    def connect(self, port: str, baudrate: int):
        """
        Connects to a specified port at the given baud rate.

        Args:
            port (str): The port to connect to.
            baudrate (int): The baud rate for the connection.

        """
        try:
            self.ser = serial.Serial(port=port, baudrate=baudrate)
        except Exception as e:
            self.error["connection"] = "Could not connect"

    def send(self, message: Message_tx):
        """
        Sends a message over the serial connection.

        Args:
            message (Message_tx): The message to send.

        """
        self.error.clear()
        try:
            self.ser.write(bytes(message.tmcl_cmd))
            self.reply = self.read()
            if self.is_reply_error(message, self.reply):
                self.error[str(message.tmcl_cmd)] = str(self.reply.tmcl_cmd)
        except:
            self.error["Send/read"] = "Could not send or read message"

    def read(self) -> Message_rx:
        """
        Reads a message from the serial connection.

        Returns:
            Message_rx: The received message.

        """
        if self.ser.readable():
            read_message = list(self.ser.read(9))
            return Message_rx(read_message)
        return Message_rx([])

    status_code = {100:  "OK",
                    101:  "Loaded into EEPROM",
                    1:  "Wrong checksum",
                    2:  "Invalid command",
                    3:  "Wrong type",
                    4:  "Invalid value",
                    5:  "Configuration EEPROM locked",
                    6:  "Command not available"}       
    
    def is_reply_error(self, message_tx: Message_tx, message_rx: Message_rx):
        """
        Checks if the received message indicates an error.

        Args:
            message_tx (Message_tx): The transmitted message.
            message_rx (Message_rx): The received message.

        Returns:
            bool: True if the received message indicates an error, False otherwise.

        """
        if message_rx.status == 100 and message_rx.cmd_n == message_tx.cmd_n:
            return False
        else:
            return True
