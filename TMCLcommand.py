import USBmessage as usb

class TMCLcmd:
    def __init__(self):
        self.ser = usb.Serial_comunication()

    def connect(self,port:str,baudrate:int):
        self.ser.connect(port,baudrate)

    def get_ports(self) -> dict:
        return self.ser.ports_dict

    def motor_stop(self,motor:int):
        self.ser.send(usb.Message_tx(1,3,0,motor,0))
    
    def move_to_abs(self,motor:int,steps:int):
        self.ser.send(usb.Message_tx(1,4,0,motor,steps))
    
    def set_param(self,type_n:int, motor:int, value_32b:int):
        self.ser.send(usb.Message_tx(1,5,type_n, motor, value_32b))

    def get_param(self,type_n:int, motor:int):
        self.ser.send(usb.Message_tx(1,6,type_n, motor, 0))
    
    def write_eeprom(self,type_n:int, motor:int, value_32b:int):
        """
        Write to EEPROM
        """
        self.ser.send(usb.Message_tx(1,7,type_n, motor, value_32b))
    
    def read_eeprom(self,type_n:int, motor:int):
        """
        Read from EEPROM
        """
        self.ser.send(usb.Message_tx(1,8,type_n, motor, 0))
    
    def ref_search(self,type_n:int, motor:int):
        self.ser.send(usb.Message_tx(1,13,type_n, motor, 0))
        
    def set_output(self,port_number:int, bank:int, value_32b:int):
        self.ser.send(usb.Message_tx(1,14,port_number, bank, value_32b))

# com = TMCLcmd()
# com.ser.connect("COM8",9600)

# com.set_param(4,0,69)



