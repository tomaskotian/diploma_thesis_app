import serial.tools.list_ports

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
        self.ports_dict = {}
        self.error = {}
        self.reply = Message_rx([0,0,0,0,0,0,0,0,0])

        self.find_ports()

    def find_ports(self):
        com_ports = serial.tools.list_ports.comports()
        self.ports_dict = {com.name: com.serial_number for com in com_ports}

    def connect(self,port:str, baudrate:int):
        try:
            self.ser = serial.Serial(port=port, baudrate=baudrate)
        except Exception as e:
            self.error["connection"] = "Could not connect"

    def send(self, message:Message_tx):
        self.error.clear()
        try:
            self.ser.write(bytes(message.tmcl_cmd))
            self.reply = self.read()
            if(self.is_reply_error(message,self.reply)):
                self.error[str(message.tmcl_cmd)] = str(self.reply.tmcl_cmd)
        except:
            self.error["Send/read"] = "Could not send or read message"

    def read(self) -> Message_rx:
        if(self.ser.readable()):
            read_message = list(self.ser.read(9))
            return Message_rx(read_message)
        return Message_rx([])

    status_code = { 100:  "OK",
                    101:  "Loaded into EEPROM",
                    1  :  "Wrong checksum",
                    2  :  "Invalid command",
                    3  :  "Wrong type",
                    4  :  "Invalid value",
                    5  :  "Configuration EEPROM locked",
                    6  :  "Command not available"}       
    
    def is_reply_error(self,message_tx:Message_tx, message_rx:Message_rx):
        if(message_rx.status == 100 and message_rx.cmd_n == message_tx.cmd_n):
            return False
        else:
            return True