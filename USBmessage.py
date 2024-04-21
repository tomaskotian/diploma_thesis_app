import serial.tools.list_ports
import logging
import datetime

DEBUG = True

def _get_logfile_name():
    today_date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    return f"logs/log_{today_date}.log"

logging.basicConfig(filename=_get_logfile_name(),format='%(asctime)s %(levelname)s - %(name)s - %(funcName)s - %(message)s',level=logging.INFO)
logging.disable()

class Message_tx:
    def __init__(self, address:bytes, cmd_n:bytes, type_n:bytes, motor_bank:bytes, value_32b:int):
        self.address    = address
        self.cmd_n      = cmd_n
        self.type_n     = type_n
        self.motor_bank = motor_bank
        self.value_32b  = value_32b
        self.check_sum  = self.checksum()

        self.tmcl_cmd = self.get_cmd()
    
    def checksum(self):
        value_sum = sum(list(self.value_32b.to_bytes(4,"big",signed=True)))
        return sum([self.address, self.cmd_n, self.type_n, self.motor_bank, value_sum]) & 0xFF
    
    def get_cmd(self):
        bytes_list = [self.address,self.cmd_n,self.type_n,self.motor_bank] 
        bytes_list.extend(self.to_list())
        bytes_list.append(self.check_sum)
        return bytes_list

    def to_list(self):
        return list(self.value_32b.to_bytes(4,"big",signed=True))
    
class Message_rx:
    def __init__(self, message:list[int]):
        self.address   = message[0]
        self.module    = message[1]
        self.status    = message[2]
        self.cmd_n     = message[3]
        self.value_32b = int.from_bytes(bytes(message[4:8]),byteorder='big',signed=True) 
        self.check_sum = message[8]

        self.tmcl_cmd = message

class Serial_comunication:
    def __init__(self):
        self.ports_dict = self.get_ports()

    def get_ports(self):
        try:       
            com_ports = serial.tools.list_ports.comports()
            return {com.name: com.serial_number for com in com_ports}
        except Exception as e:
            logging.error(e)

    def connect(self,port:str, baudrate:int):
        try:
            self.ser = serial.Serial(port=port, baudrate=baudrate)
        except Exception as e:
            logging.error(e)

    def send(self, message:Message_tx):
        try:
            self.ser.write(bytes(message.tmcl_cmd))
            logging.info(f"TX TMCL cmd: {message.tmcl_cmd}")
            self.check_reply(message,self.read())
        except Exception as e:
            logging.error(e)

    def read(self) -> Message_rx:
        try:
            if(self.ser.readable()):
                read_message = list(self.ser.read(9))
                logging.info(f"RX TMCL reply: {read_message}")
                return Message_rx(read_message)
            return Message_rx([])
        except Exception as e:
            logging.error(e)

    status_code = { 100:  "OK",
                    101:  "Loaded into EEPROM",
                    1  :  "Wrong checksum",
                    2  :  "Invalid command",
                    3  :  "Wrong type",
                    4  :  "Invalid value",
                    5  :  "Configuration EEPROM locked",
                    6  :  "Command not available"}       
    
    def check_reply(self,message_tx:Message_tx, message_rx:Message_rx):
        if(message_rx.status == 100 and message_rx.cmd_n == message_tx.cmd_n):
            return True
        else:
            try:
                logging.error(self.status_code[message_rx.status])
            except Exception as e:
                logging.error(e)
            return False

  
    
    if(DEBUG):
        def print_usb_devices(self):
            ports = serial.tools.list_ports.comports()
            if ports:
                print("USB Devices:")
                for port in ports:
                    print(f" - {port.device}: {port.description}")


# ser = Serial_comunication()
# ser.connect("COM8",9600)
# ser.send(Message_tx(0,5,4,0,10))
# print(ser.read().tmcl_cmd)
# ser.send(Message_tx(1,5,4,0,50))
# print(ser.read().tmcl_cmd)

# Message_tx(1,1,4,5,-1000)
Message_rx([1,1,4,5,255,255,0xfc,0x18,0x1d])