"""
File: TMCLcommand.py
Author: Tomas Kotian
Date: 15.5.2024
Description: Basic commands fo control TMCM-6110
"""
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

    # ----------------------------------------------------------------------------------------------------
    # Methodes
    # ----------------------------------------------------------------------------------------------------

    def __autoconnect(self):
        """
        Automatically connects to a TMCM-6110 device.

        This method iterates through available ports, attempts to connect
        to the first TMCM-6110 device found, and sets the connection string.
        If no TMCM-6110 device is found, it adds an error message to the
        errors list.

        """
        for port in self.ser.ports_dict.keys():
            if self.ser.ports_dict[port] == 'TMCSTEP':
                self.ser.connect(port=port, baudrate=9600)
                self.connection = f"{port}: TMCSTEP"
                break

        if self.connection is None:
            self.erros_list.append({"connection": "Autoconnect failed cannot find TMCM-6110"})
            return
        self.set_motor_parameters()

    def connect(self, port: str, baudrate: int):
        """
        Connects to a specified port with the given baudrate.

        Args:
            port (str): The port to connect to.
            baudrate (int): The baudrate for the connection.

        This method establishes a connection to the specified port with the
        specified baudrate and sets motor parameters.

        """
        self.ser.connect(port, baudrate)
        self.set_motor_parameters()

    def get_ports(self) -> dict:
        """
        Finds available ports and returns a dictionary of ports.

        Returns:
            dict: A dictionary containing available ports and their descriptions.

        This method searches for available ports and returns a dictionary
        containing the port names and their descriptions.

        """
        self.ser.find_ports()
        return self.ser.ports_dict

    def motor_stop(self, motor: int):
        """
        Stops the specified motor.

        Args:
            motor (int): The index of the motor to stop.

        This method sends a message to the device to stop the specified motor.

        """
        self.ser.send(usb.Message_tx(1, 3, 0, motor, 0))

    def move_to_abs(self, motor: int, position: int):
        """
        Moves the specified motor to the absolute position.

        Args:
            motor (int): The index of the motor to move.
            position (int): The absolute position to move the motor to.

        This method calculates the steps required to move to the specified
        absolute position and sends the corresponding command to the device.

        """
        if self.ignore_cmd(motor=motor):
            return
        self.ser.send(usb.Message_tx(1, 4, 0, motor, self._distance2steps(motor=motor, position=position)))

    
    def _distance2steps(self,motor,position):
        """
        Converts the distance to steps for the specified motor.

        Args:
        motor (int): The index of the motor.
        position (int): The position to convert to steps.

        Returns:
        int: The equivalent steps for the given distance.

        This method calculates the number of steps required to cover the
        specified distance for the given motor.

        """
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
        """
        Converts the steps to distance for the specified motor.

        Args:
            motor (int): The index of the motor.
            steps (int): The steps to convert to distance.

        Returns:
            int: The equivalent distance for the given steps.

        This method calculates the distance covered by the given number of steps
        for the specified motor.

        """
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
        """
        Sets parameter for a specific motor.

        Args:
        type_n (int): Type of parameter to set.
        motor (int): Index of the motor.
        value_32b (int): 32-bit value to set for the parameter.

        This method sends a message to set the parameter for the specified motor.

        """
        self.ser.send(usb.Message_tx(1,5,type_n, motor, value_32b))
        self._get_errors()

    def _get_errors(self):
        """
        Retrieves errors from the serial connection.

        This method checks for errors in the serial connection and appends
        them to the errors list if any are found.

        """
        if(len(self.ser.error)):
            self.erros_list.append(self.ser.error.copy())

    def get_param(self,type_n:int, motor:int):
        """
        Retrieves parameter for a specific motor.

        Args:
            type_n (int): Type of parameter to retrieve.
            motor (int): Index of the motor.

        This method sends a message to retrieve the parameter for the specified motor.

        """
        self.ser.send(usb.Message_tx(1,6,type_n, motor, 0))
    
    def write_eeprom(self,type_n:int, motor:int, value_32b:int):
        """
        Writes to EEPROM.

        Args:
            type_n (int): Type of parameter to write to EEPROM.
            motor (int): Index of the motor.
            value_32b (int): 32-bit value to write to EEPROM.

        This method sends a message to write the specified value to EEPROM.

        """
        self.ser.send(usb.Message_tx(1,7,type_n, motor, value_32b))
    
    def read_eeprom(self,type_n:int, motor:int):
        """
        Reads from EEPROM.

        Args:
            type_n (int): Type of parameter to read from EEPROM.
            motor (int): Index of the motor.

        This method sends a message to read the parameter from EEPROM.

        """
        self.ser.send(usb.Message_tx(1,8,type_n, motor, 0))
    
    def ref_search(self,type_n:int, motor:int):
        """
        Initiates reference search for a specific motor.

        Args:
        type_n (int): Type of reference search.
        motor (int): Index of the motor.

        This method sends a message to initiate reference search for the specified motor.

        """
        self.ser.send(usb.Message_tx(1,13,type_n, motor, 0))
        
    def set_output(self,port_number:int, bank:int, value_32b:int):
        """
        Sets output for a specific port and bank.

        Args:
            port_number (int): Number of the port.
            bank (int): Bank of the port.
            value_32b (int): 32-bit value to set for the output.

        This method sends a message to set the output for the specified port and bank.

        """
        self.ser.send(usb.Message_tx(1,14,port_number, bank, value_32b))

    def reach_flag(self,motor:int):
        """
        Retrieves reach flag for a specific motor.

        Args:
            motor (int): Index of the motor.

        This method sends a message to retrieve the reach flag for the specified motor.

        """
        self.ser.send(usb.Message_tx(1,6,8,motor,0))   

    def _set_block(self):
        """
        Sets block status based on errors.

        This method checks if there are any errors in the errors list
        and sets the blocked status accordingly.

        """
        if(len(self.erros_list)):
            self.blocked = True
    
    def _print_eerors(self):
        """
        Debug methode to print errors in terminal
        """
        print(f"Errors: {self.erros_list}")

    def set_motor_parameters(self):
        for motor in range(4):
            self.set_param(type_n=4,motor=motor,value_32b=1677)     # maximum speed positioning 
            self.set_param(type_n=5,motor=motor,value_32b=200)      # maximum acceleration positioning 
            self.set_param(type_n=6,motor=motor,value_32b=150)      # maximum current for motor   
            self.set_param(type_n=7,motor=motor,value_32b=10)       # standby current for motor
            if(motor == 3):
                self.set_param(type_n=4,motor=motor,value_32b=419)  # maximum speed positioning 
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
            self.set_param(type_n=4,motor=motor,value_32b=2000)     # maximum speed positioning 
            self.set_param(type_n=5,motor=motor,value_32b=500)      # maximum acceleration positioning 
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





