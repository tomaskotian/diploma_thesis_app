import USBmessage as usb

class TMCLcmd:
    def __init__(self):
        self.erros_list = []
        self.blocked = False #for block all commands
        self.unit = "mm"
        self.actual_positions = [0,0,0,0,0,0]
        self.connection = None

        self.ser = usb.Serial_comunication()
        self.__autoconnect()

    def __autoconnect(self):
        for port in self.ser.ports_dict.keys():
            if(self.ser.ports_dict[port] == 'TMCSTEP'):
                self.ser.connect(port=port,baudrate=9600)
                self.connection = f"{port}: TMCSTEP"
                break
        
        if(self.connection == None):
            print("Autoconnect cannot found TMCM-6110")
            return
        self.set_motor_parametres()
        
    def connect(self,port:str,baudrate:int):
        self.ser.connect(port,baudrate)
        self.set_motor_parametres()

    def get_ports(self) -> dict:
        self.ser.find_ports()
        return self.ser.ports_dict

    def motor_stop(self,motor:int):
        self.ser.send(usb.Message_tx(1,3,0,motor,0))
    
    def move_to_abs(self,motor:int,position:int):
        if(self.ignore_cmd(motor=motor)):
            return
        self.ser.send(usb.Message_tx(1,4,0,motor,self._distance2steps(motor=motor,position=position)))
    
    def _distance2steps(self,motor,position):
        pitch = 5
        if(motor == 3):
            pitch = 10
        distance_step = (pitch*1000)/51200


        if(motor == 4):
            # motor 4  270deg = 393750 steps 1deg  = 1458.33 steps
            if(position == 0):
                return int(0.1 * 1458.33)
            return int(position * 1458.33)
        elif(motor == 5):
            # motor 5 rotation small gear 525000 steps 270deg = 2953125 steps 1 deg = 10937.5 step
            return int(position * 10937.5)
        else:
            # for all others motors 0-3
            return int(position / distance_step)

    def _steps2distance(self,motor,steps):
        pitch = 5
        if(motor == 3):
            pitch = 10
        
        distance_step = (pitch*1000)/51200

        if(motor == 4):
            # motor 4  270deg = 393750 steps 1deg  = 1458.33 steps
            return int(steps / 1458.33)
        elif(motor == 5):
            # motor 5 rotation small gear 525000 steps 270deg = 2953125 steps 1 deg = 10937.5 step
            return int(steps / 10937.5)
        else:
            # for all others motors 0-3
            return int(steps * distance_step)
        

    def set_param(self,type_n:int, motor:int, value_32b:int):
        self.ser.send(usb.Message_tx(1,5,type_n, motor, value_32b))
        self._get_errors()

    def _get_errors(self):
        if(len(self.ser.error)):
            self.erros_list.append(self.ser.error.copy())

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

    def reach_flag(self,motor:int):
        self.ser.send(usb.Message_tx(1,6,8,motor,0))   

    def _set_block(self):
        if(len(self.erros_list)):
            self.blocked = True
    
    def _print_eerors(self):
        print(f"Errors: {self.erros_list}")

    def set_motor_parametres(self):
        for motor in range(4):
            self.set_param(type_n=4,motor=motor,value_32b=1677)     # maximum speed positioning in eeprom
            self.set_param(type_n=5,motor=motor,value_32b=200)      # maximum acceleration positioning in eeprom
            self.set_param(type_n=6,motor=motor,value_32b=150)      # maximum current for motor   
            self.set_param(type_n=7,motor=motor,value_32b=10)       # standby current for motor
            if(motor == 3):
                self.set_param(type_n=4,motor=motor,value_32b=419)  # maximum speed positioning in eeprom
                self.set_param(type_n=7,motor=motor,value_32b=100)  # standby current for motor
            self.set_param(type_n=13,motor=motor,value_32b=0)       # aktivation left end switch
            self.set_param(type_n=140,motor=motor,value_32b=8)      # microsteps resolution 8=256
            self.set_param(type_n=153,motor=motor,value_32b=7)      # ramp divisor 
            self.set_param(type_n=154,motor=motor,value_32b=2)      # pulse divisor 
            self.set_param(type_n=193,motor=motor,value_32b=1)      # reference search mode
            self.set_param(type_n=194,motor=motor,value_32b=1677)   # reference search speed 
            self.set_param(type_n=195,motor=motor,value_32b=100)    # reference search switch speed
            self.set_param(type_n=214,motor=motor,value_32b=10)     # delay after command in 10ms
            
        for motor in range(4,6):
            self.set_param(type_n=4,motor=motor,value_32b=2000)     # maximum speed positioning in eeprom
            self.set_param(type_n=5,motor=motor,value_32b=500)      # maximum acceleration positioning in eeprom
            self.set_param(type_n=6,motor=motor,value_32b=10)       # maximum current for motor    
            self.set_param(type_n=7,motor=motor,value_32b=1)        # standby current for motor
            self.set_param(type_n=13,motor=motor,value_32b=0)       # aktivation left end switch
            self.set_param(type_n=140,motor=motor,value_32b=8)      # microsteps resolution 8=256
            self.set_param(type_n=153,motor=motor,value_32b=7)      # ramp divisor 
            self.set_param(type_n=154,motor=motor,value_32b=2)      # pulse divisor 
            self.set_param(type_n=193,motor=motor,value_32b=1)      # reference search mode
            self.set_param(type_n=194,motor=motor,value_32b=2000)   # reference search speed
            self.set_param(type_n=195,motor=motor,value_32b=100)    # reference search switch speed
            self.set_param(type_n=214,motor=motor,value_32b=10)     # delay after command in 10ms

        self._set_block()
        self._print_eerors()
        self.erros_list.clear()

    def find_all_references(self):
        for motor in range(6):
            self.ref_search(type_n=0,motor=motor)

    def get_actual_positions(self):
        for motor in range(6):
            self.get_param(type_n=1,motor=motor) #actual position
            self.actual_positions[motor] = self._steps2distance(motor=motor,steps=self.ser.reply.value_32b) 
    
    def ignore_cmd(self,motor):
        self.ref_search(type_n=2,motor=motor)
        if(self.ser.reply.value_32b != 0): # status if 0 finished search
            return True
        
        self.reach_flag(motor=motor) # status if 1 reached position
        if(self.ser.reply.value_32b != 1):
            return True
        
        return False





