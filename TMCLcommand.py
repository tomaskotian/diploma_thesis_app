import USBmessage as usb

class TMCLcmd:
    def __init__(self):
        self.ser = usb.Serial_comunication()
        self.autoconnect()

    def autoconnect(self):
        connection_flag = False
        for port in self.ser.ports_dict.keys():
            if(self.ser.ports_dict[port] == 'TMCSTEP'):
                self.ser.connect(port=port)
                connection_flag = True
                break
        
        if(not(connection_flag)):
            print("Autoconnect cannot found TMCM-6110")
        
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



com = TMCLcmd()

# com.set_param(type_n=6,motor=0,value_32b=)

#function for set motor params
for motor in range(4):
    #com.set_param(type_n=4,motor=motor,value_32b=1000) # maximum speed positioning in eeprom
    #com.set_param(type_n=5,motor=motor,value_32b=500)  # maximum acceleration positioning in eeprom
    com.set_param(type_n=6,motor=motor,value_32b=150)  # maximum current for motor    
    com.set_param(type_n=7,motor=motor,value_32b=10)  # standby current for motor   
    com.set_param(type_n=140,motor=motor,value_32b=8)  # microsteps for motor 8=256
    com.set_param(type_n=193,motor=motor,value_32b=1)  # reference search mode
    com.set_param(type_n=194,motor=motor,value_32b=1500)  # reference search speed
    com.set_param(type_n=195,motor=motor,value_32b=100)  # reference search switch speed
    
for motor in range(4,6):
    #com.set_param(type_n=4,motor=motor,value_32b=1000) # maximum speed positioning in eeprom
    #com.set_param(type_n=5,motor=motor,value_32b=500)  # maximum acceleration positioning in eeprom
    com.set_param(type_n=6,motor=motor,value_32b=10)  # maximum current for motor    
    com.set_param(type_n=7,motor=motor,value_32b=1)  # standby current for motor
    com.set_param(type_n=140,motor=motor,value_32b=8)  # microsteps for motor 8=256
    com.set_param(type_n=193,motor=motor,value_32b=1)  # reference search mode
    com.set_param(type_n=194,motor=motor,value_32b=1500)  # reference search speed
    com.set_param(type_n=195,motor=motor,value_32b=100)  # reference search switch speed


    
#functions to find reference
# com.ref_search(type_n=0,motor=0)
# com.ref_search(type_n=0,motor=1)
# com.ref_search(type_n=0,motor=2)
# com.ref_search(type_n=0,motor=3)
# com.ref_search(type_n=0,motor=4)  #i=10,is=1,speed search pluss 500  2000
# com.ref_search(type_n=0,motor=5)  #i=10,is=1, speed search pluss 500 1000


# com.set_param(type_n=4,motor=0,value_32b=69)



