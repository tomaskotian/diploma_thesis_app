import tkinter as tk
from tkinter import scrolledtext
import cv2
from PIL import Image,ImageTk
import TMCLcommand as tmc
import time
import numpy as np
import json


class Gui(tk.Tk):
    def __init__(self):
        super().__init__()

        self.menubar = tk.Menu(self)

        self.menu_file = tk.Menu(self.menubar,tearoff=0)

        self.menubar.add_cascade(label="Settings",menu=self.menu_file)
        self.menu_file.add_checkbutton(label="active shortcuts")
        self.menu_file.add_command(label="Shortcuts",command=self.set_shortcuts)
        self.config(menu=self.menubar)
        
        self.magnification_deg = {0.7:0, 0.8:13, 0.9:27, 1:40, 1.1:48, 1.2:56, 1.3:64, 1.4:72, 
                                  1.5:80, 1.6:84, 1.7:88, 1.8:92, 1.9:96,
                                  2:100, 2.1:106, 2.2:112, 2.3:118, 2.4:124, 
                                  2.5:130, 2.6:134, 2.7:138, 2.8:152, 2.9:156,
                                  3:150, 3.1:156, 3.2:162, 3.3:168, 3.4:174, 
                                  3.5:180, 3.6:184, 3.7:188, 3.8:192, 3.9:196,
                                  4:200, 4.1:206, 4.2:212, 4.3:218, 4.4:224, 
                                  4.5:230, 4.6:234, 4.7:238, 4.8:242, 4.9:246,
                                  5:250, 5.1:255, 5.2:260, 5.3:265, 5.4:270, 5.5:275, 5.6:280}
        self.focus_distance = {0.7:0, 1:40, 1.5:80, 2:100, 2.5:130, 3:150, 3.5:180, 4:200, 4.5:230, 5:250, 5.6:280}
        self.positions = []
        self.shortcuts_dict = {}
        self.shortcuts_dict_new = {}
        self.chip_size_pixel = []
        self.row_list = []
        self.led_intensity_target = 0
        self.led_intensity_var = 0 
        self.unit = "mm"
        self.tmcm = tmc.TMCLcmd()
        self.tmcm_ports = [f"{com}: {self.tmcm.get_ports()[com]}" for com in self.tmcm.get_ports().keys()]

        cam_ports = self.find_available_cameras()
        self.load_shortcuts(original=False)

        self.title("Semiconductor chip testing application")
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        self.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        # self.geometry(f"{1100}x{580}")
        self.state('zoomed') 

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        self.bind("<Key>",self.key_pressed)
        self.bind("<MouseWheel>",self.wheel)
        self.bind("<Button-3>",self.change_unit)

        self.sidebar_frame = tk.Frame(self,padx=10,pady=10,bg="#383838")
        self.sidebar_frame.grid(row=0,column=0,rowspan=2,sticky="nsew")
        self.sidebar_frame.grid_rowconfigure((0,1,2,3,4,5,6,7,8,9),weight=1)

        self.camera_frame = tk.Frame(self,padx=200,pady=20,bg="#8A8A8A")
        self.camera_frame.grid(row=0,column=1,sticky="nsew")

        self.downbar_frame = tk.Frame(self,padx=10,pady=5)
        self.downbar_frame.grid(row=1,column=1,rowspan=1,sticky="nsew")
        self.downbar_frame.grid_columnconfigure((0,1),weight=1)

        self.var_tmcm = tk.StringVar(self.sidebar_frame,self.tmcm.connection)
        self.tmcm_options = tk.OptionMenu(self.sidebar_frame,self.var_tmcm,*self.tmcm_ports,command=self.connect_tmcm)
        self.tmcm_options.config(width=15)
        self.tmcm_options.grid(row=0,column=0,padx=5)

        self.var_cam = tk.StringVar(self.sidebar_frame,'0')
        self.cam_options = tk.OptionMenu(self.sidebar_frame,self.var_cam,*cam_ports,command=self.connect_cam)
        self.cam_options.config(width=15)
        self.cam_options.grid(row=0,column=1,padx=5)

        self.video_capture = None
        self.current_image = None
        

        self.stop_button = tk.Button(self.sidebar_frame,text=f"STOP <{self.shortcuts_dict['stop']}>",bg="red",width=30,height=4,command=self.stop_tmcm)
        self.stop_button.grid(row=1,column=0,columnspan=2,padx=5,pady=5)

        self.position_frame = tk.Frame(self.sidebar_frame)
        self.position_frame.grid(row=2,column=0,columnspan=2,sticky="nsew")

        self.position_label = tk.Label(self.position_frame,text="Positions",bg="#8A8A8A")
        self.position_label.grid(row=0,column=0,columnspan=3,sticky="nsew")

        self.position_x = tk.Label(self.position_frame,text="axis X",width=10)
        self.position_x.grid(row=1,column=0)
        self.position_x_val = tk.Label(self.position_frame,text="0",width=20)
        self.position_x_val.grid(row=1,column=1)
        self.position_x_unit = tk.Label(self.position_frame,text="um",width=10)
        self.position_x_unit.grid(row=1,column=2,sticky="nsew")

        self.position_y = tk.Label(self.position_frame,text="axis Y",width=10)
        self.position_y.grid(row=2,column=0)
        self.position_y_val = tk.Label(self.position_frame,text="0",width=20)
        self.position_y_val.grid(row=2,column=1)
        self.position_y_unit = tk.Label(self.position_frame,text="um",width=10)
        self.position_y_unit.grid(row=2,column=2,sticky="nsew")

        self.position_cam_z = tk.Label(self.position_frame,text="camera Z",width=10)
        self.position_cam_z.grid(row=3,column=0)
        self.position_cam_z_val = tk.Label(self.position_frame,text="0",width=20)
        self.position_cam_z_val.grid(row=3,column=1)
        self.position_cam_z_unit = tk.Label(self.position_frame,text="um",width=10)
        self.position_cam_z_unit.grid(row=3,column=2,sticky="nsew")

        self.position_probe_z = tk.Label(self.position_frame,text="probe Z",width=10)
        self.position_probe_z.grid(row=4,column=0)
        self.position_probe_z_val = tk.Label(self.position_frame,text="0",width=20)
        self.position_probe_z_val.grid(row=4,column=1)
        self.position_probe_z_unit = tk.Label(self.position_frame,text="um",width=10)
        self.position_probe_z_unit.grid(row=4,column=2,sticky="nsew")

        self.position_table_angle = tk.Label(self.position_frame,text="table angle",width=10)
        self.position_table_angle.grid(row=5,column=0)
        self.position_table_angle_val = tk.Label(self.position_frame,text="0",width=20)
        self.position_table_angle_val.grid(row=5,column=1)
        self.position_table_angle_unit = tk.Label(self.position_frame,text="°",width=10)
        self.position_table_angle_unit.grid(row=5,column=2,sticky="nsew")

        self.led_frame = tk.Frame(self.sidebar_frame)
        self.led_frame.grid(row=3,column=0,columnspan=2,sticky="nsew",pady=10)

        self.led_label = tk.Label(self.led_frame,text="Led intensity",bg="#8A8A8A")
        self.led_label.grid(row=0,column=0,sticky="nsew")

        self.intesity_led_var = tk.IntVar(self.led_frame)
        self.led_bar = tk.Scale(self.led_frame,variable=self.intesity_led_var, from_=0, to=100,resolution=4,length=300, orient=tk.HORIZONTAL)
        self.led_bar.grid(row=1,column=0,columnspan=2)

        self.led_bar_key_p = tk.Label(self.led_frame,text=f"<{self.shortcuts_dict['LED intesity minus']}>")
        self.led_bar_key_p.grid(row=2,column=0,sticky="w")
        self.led_bar_key_m = tk.Label(self.led_frame,text=f"<{self.shortcuts_dict['LED intesity plus']}>")
        self.led_bar_key_m.grid(row=2,column=1,sticky="e")
        
        
        self.led_auto_var = tk.BooleanVar(self.led_frame,True)
        self.led_auto = tk.Checkbutton(self.led_frame,text=f"Automatic <{self.shortcuts_dict['LED automatic']}>",variable=self.led_auto_var)
        self.led_auto.grid(row=0,column=1,padx=5)
        self.led_auto.select()

        self.camera_setting_frame = tk.Frame(self.sidebar_frame)
        self.camera_setting_frame.grid(row=4,column=0,columnspan=2,sticky="nsew")

        self.camera_label = tk.Label(self.camera_setting_frame,text="Camera settings",bg="#8A8A8A")
        self.camera_label.grid(row=0,column=0,columnspan=4,sticky="nsew")

        self.camera_mag_var = tk.DoubleVar(self.camera_setting_frame,0.7) 
        self.camera_mag = tk.Scale(self.camera_setting_frame,variable=self.camera_mag_var, from_=0.7, to=5.6, resolution=0.1, orient=tk.HORIZONTAL)
        self.camera_mag.grid(row=1,column=0,columnspan=2,sticky="nswe")

        self.camera_mag_p = tk.Label(self.camera_setting_frame,text=f"<{self.shortcuts_dict['magnification minus']}>")
        self.camera_mag_p.grid(row=2,column=0,sticky="w")
        self.camera_mag_m = tk.Label(self.camera_setting_frame,text=f"<{self.shortcuts_dict['magnification plus']}>")
        self.camera_mag_m.grid(row=2,column=1,sticky="e")

        self.camera_mag_label = tk.Label(self.camera_setting_frame,text="Magnification")
        self.camera_mag_label.grid(row=1,column=2,rowspan=2)

        self.camera_up = tk.Button(self.camera_setting_frame,text=f"up<{self.shortcuts_dict['camera up']}>",command=self.move_camera_up)
        self.camera_up.grid(row=3,column=0)

        self.camera_down = tk.Button(self.camera_setting_frame,text=f"down <{self.shortcuts_dict['camera down']}>",command=self.move_camera_down)
        self.camera_down.grid(row=4,column=0)

        self.camera_canvas = tk.Canvas(self.camera_setting_frame,width=50,height=50)
        self.camera_canvas.grid(row=3,column=1,rowspan=2)

        self.camera_focus_var = tk.BooleanVar(self.camera_setting_frame,value=True)
        self.camera_auto = tk.Checkbutton(self.camera_setting_frame,text=f"Automatic focus <{self.shortcuts_dict['camera automatic focus']}>",variable=self.camera_focus_var)
        self.camera_auto.grid(row=3,column=2,rowspan=2,padx=5)

        self.step_frame = tk.Frame(self.sidebar_frame)
        self.step_frame.grid(row=6,column=0,columnspan=2,sticky="nsew",pady=10)

        self.step_um = tk.Checkbutton(self.step_frame,text=f"um <{self.shortcuts_dict['step um']}>",command=self.set_step_um)
        self.step_um.grid(row=0,column=0,padx=5)
        
        self.step_mm = tk.Checkbutton(self.step_frame,text=f"mm <{self.shortcuts_dict['step mm']}>",command=self.set_step_mm)
        self.step_mm.grid(row=0,column=1,padx=5)
        self.step_mm.select()

        self.step_var = tk.IntVar()
        self.step_slider = tk.Scale(self.step_frame,variable=self.step_var, from_=1, to=500,resolution=1,length=300, orient=tk.HORIZONTAL)
        self.step_slider.grid(row=1,column=0,columnspan=2)

        self.step_p = tk.Label(self.step_frame,text=f"<{self.shortcuts_dict['step minus']}>")
        self.step_p.grid(row=2,column=0,sticky="w")
        self.step_m = tk.Label(self.step_frame,text=f"<{self.shortcuts_dict['step plus']}>")
        self.step_m.grid(row=2,column=1,sticky="e")


        self.joystick_frame = tk.Frame(self.sidebar_frame)
        self.joystick_frame.grid(row=7,column=0,columnspan=3,sticky="nsew",pady=10)

        self.joystick_table = tk.Label(self.joystick_frame,text="Table",bg="#8A8A8A")
        self.joystick_table.grid(row=0,column=0,columnspan=3,sticky="nsew")

        self.table_r = tk.Button(self.joystick_frame,text=f"r <{self.shortcuts_dict['rotate right']}>",command=self.rotate_right)
        self.table_r.grid(row=1,column=0)

        self.table_up = tk.Button(self.joystick_frame,text=f"up <{self.shortcuts_dict['table forward']}>",command=self.move_x_plus)
        self.table_up.grid(row=1,column=1)

        self.table_l = tk.Button(self.joystick_frame,text=f"l <{self.shortcuts_dict['rotate left']}>",command=self.rotate_left)
        self.table_l.grid(row=1,column=2)

        self.probe_up = tk.Button(self.joystick_frame,text=f"p_up <{self.shortcuts_dict['probe up']}>",command=self.move_probe_up)
        self.probe_up.grid(row=1,column=3)

        self.table_left = tk.Button(self.joystick_frame,text=f"left <{self.shortcuts_dict['table left']}>",command=self.move_y_plus)
        self.table_left.grid(row=2,column=0)
        
        self.table_canvas = tk.Canvas(self.joystick_frame,width=50,height=50)
        self.table_canvas.grid(row=2,column=1)

        self.table_right = tk.Button(self.joystick_frame,text=f"right <{self.shortcuts_dict['table right']}>",command=self.move_y_minus)
        self.table_right.grid(row=2,column=2)

        self.probe_canvas = tk.Canvas(self.joystick_frame,width=50,height=50)
        self.probe_canvas.grid(row=2,column=3)

        self.table_down = tk.Button(self.joystick_frame,text=f"down <{self.shortcuts_dict['table backward']}>",command=self.move_x_minus)
        self.table_down.grid(row=3,column=1)

        self.probe_down = tk.Button(self.joystick_frame,text=f"p_down <{self.shortcuts_dict['probe down']}>",command=self.move_probe_down)
        self.probe_down.grid(row=3,column=3)

        self.function_frame  = tk.Frame(self.downbar_frame)
        self.function_frame.grid(row=0,column=0,sticky="nswe",padx=5,pady=5)
        self.function_frame.grid_columnconfigure((0,1,2,3),weight=1)

        self.function_home = tk.Button(self.function_frame,width=15,height=2,text=f"Home <{self.shortcuts_dict['home']}>",command=self.find_home).grid(column=0,row=0)
        self.function_center = tk.Button(self.function_frame,width=15,height=2,text=f"Center <{self.shortcuts_dict['center']}>",command=self.find_center).grid(column=1,row=0)
        self.function_find_chip = tk.Button(self.function_frame,width=15,height=2,text=f"Center chip <{self.shortcuts_dict['center chip']}>",command=self.center_chip).grid(column=2,row=0)

        self.function_click_move_var = tk.BooleanVar(self.function_frame,False)
        self.function_click_move = tk.Checkbutton(self.function_frame,variable=self.function_click_move_var,text=f"Click and move <{self.shortcuts_dict['click and move']}>")
        self.function_click_move.grid(column=3,row=0)

        self.messages = tk.Message(self.function_frame,text="hello\n\n\n\n",anchor="e",bg="white")
        self.messages.grid(row=1,column=0,columnspan=4,pady=5,padx=5,sticky="nswe")


        self.find_chip_frame = tk.Frame(self.downbar_frame)
        self.find_chip_frame.grid(column=1,row=0,padx=5,pady=5,sticky="nsew")
        self.find_chip_frame.grid_columnconfigure(1,weight=1)

        self.find_chip_var = tk.BooleanVar(self.find_chip_frame,False)
        self.function_find_chip = tk.Checkbutton(self.find_chip_frame,variable=self.find_chip_var,text=f"Find chip <{self.shortcuts_dict['find chip']}>",bg="#8A8A8A")
        self.function_find_chip.grid(column=0,row=0,columnspan=2,sticky="nsew")

        self.th1_l = tk .Label(self.find_chip_frame,text="th1")
        self.th1_l.grid(row=2,column=0)
        self.th1_var = tk.IntVar(self.find_chip_frame,120)
        self.th1 = tk.Scale(self.find_chip_frame,variable=self.th1_var, from_=0, to=255,resolution=4,length=300, orient=tk.HORIZONTAL)
        self.th1.grid(row=2,column=1,sticky="nswe",pady=5,padx=5)
        
        self.th2_l = tk .Label(self.find_chip_frame,text="th2")
        self.th2_l.grid(row=3,column=0)
        self.th2_var = tk.IntVar(self.find_chip_frame,100)
        self.th2 = tk.Scale(self.find_chip_frame,variable=self.th2_var, from_=0, to=255,resolution=4,length=300, orient=tk.HORIZONTAL)
        self.th2.grid(row=3,column=1,sticky="nswe",pady=5,padx=5)
    

        self.th3_l = tk .Label(self.find_chip_frame,text="th3")
        self.th3_l.grid(row=4,column=0)
        self.th3_var = tk.IntVar(self.find_chip_frame,2000)
        self.th3 = tk.Scale(self.find_chip_frame,variable=self.th3_var, from_=0, to=100000,resolution=4,length=300, orient=tk.HORIZONTAL)
        self.th3.grid(row=4,column=1,sticky="nswe",pady=5,padx=5)

        self.find_param = tk.Checkbutton(self.find_chip_frame,text="Fixed parametres")
        self.find_param.grid(row=1,column=0,padx=5,pady=5,sticky="nswe")
        self.find_param.select()
        
        self.tmcm.find_all_references()
        self.canvas = tk.Canvas(self.camera_frame,width=640,height=480)
        self.canvas.bind('<Button-1>',self.cordinates)
        self.canvas.pack(anchor=tk.CENTER)
        if(len(cam_ports)):
            self.connect_cam(0)
        if(self.video_capture != None):
            self.update_webcam()
        
        self.update_positon()
        self.timer_100ms()
        self.timer_20ms()


#----------------------------------------------------------------------------------------------------
    def wheel(self,event):
        if(event.delta == -120):
            self.step_var.set(self.step_var.get()+1)
            if(self.step_var.get() == 500):
                self.step_var.set(1)
        else:
            self.step_var.set(self.step_var.get()-1)
            if(self.step_var.get() == 1):
                self.step_var.set(500)

    def change_unit(self,event):
        if(self.unit == "mm"):
            self.unit = "um"
            self.step_um.select()
            self.step_mm.deselect()
        elif(self.unit == "um"):
            self.unit = "mm"
            self.step_mm.select()
            self.step_um.deselect()

    def key_pressed(self,event):
        print("Key pressed:", event.keysym)
        if(event.keysym == self.shortcuts_dict["stop"]):
            self.stop_tmcm()
        elif(event.keysym == self.shortcuts_dict["LED intesity plus"]):
            self.intesity_led_var.set(self.intesity_led_var.get()+4)
            if(self.intesity_led_var.get() == 100):
                self.intesity_led_var.set(0) 
        elif(event.keysym == self.shortcuts_dict["LED intesity minus"]):
            self.intesity_led_var.set(self.intesity_led_var.get()-4)
            if(self.intesity_led_var.get() == 0):
                self.intesity_led_var.set(100) 
        elif(event.keysym == self.shortcuts_dict["LED automatic"]):
            if(self.led_auto_var.get()):
                self.led_auto_var.set(False)
            else:
                self.led_auto_var.set(True)
        elif(event.keysym == self.shortcuts_dict["magnification plus"]):
            self.camera_mag_var.set(round(self.camera_mag_var.get()+0.1,1))
            if(self.camera_mag_var.get() == 5.6):
                self.camera_mag_var.set(0.7) 
        elif(event.keysym == self.shortcuts_dict["magnification minus"]):
            self.camera_mag_var.set(round(self.camera_mag_var.get()-0.1,1))
            if(self.camera_mag_var.get() == 0.7):
                self.camera_mag_var.set(5.6) 
        elif(event.keysym == self.shortcuts_dict["camera automatic focus"]):
            if(self.camera_focus_var.get()):
                self.camera_focus_var.set(False)
            else:
                self.camera_focus_var.set(True)
        elif(event.keysym == self.shortcuts_dict["camera up"]):
            self.move_camera_up()
        elif(event.keysym == self.shortcuts_dict["camera down"]):
            self.move_camera_down()
        elif(event.keysym == self.shortcuts_dict["rotate right"]):
            self.rotate_right()
        elif(event.keysym == self.shortcuts_dict["table forward"]):
            self.move_x_plus()
        elif(event.keysym == self.shortcuts_dict["rotate left"]):
            self.rotate_left()
        elif(event.keysym == self.shortcuts_dict["table backward"]):
            self.move_x_minus()
        elif(event.keysym == self.shortcuts_dict["table left"]):
            self.move_y_plus()
        elif(event.keysym == self.shortcuts_dict["table right"]):
            self.move_y_minus()
        elif(event.keysym == self.shortcuts_dict["probe up"]):
            self.move_probe_up()
        elif(event.keysym == self.shortcuts_dict["probe down"]):
            self.move_probe_down()

    
    def timer_20ms(self):
        if(self.led_auto_var.get()):
            target = int(20/4)
        else:
            target = int(self.intesity_led_var.get()/4)
        self.tmcm.set_output(3,2,0)
        time.sleep(0.005)
        if(self.led_intensity_var != target):
            self.tmcm.set_output(3,2,1)
            self.led_intensity_var += 1
            if(self.led_intensity_var >=26):
                self.led_intensity_var = 0

        self.after(15,self.timer_20ms)    

    def cordinates(self,event):
        print(event.x)
        print(event.y)
        if(self.function_click_move_var.get()):
            if(event.x >= 480):
                if(event.y >= 360):
                    self.move_x_minus()
                    self.move_y_minus()
                elif(event.y >= 120):
                    self.move_y_minus()
                else:
                    self.move_x_plus()
                    self.move_y_minus()
            elif(event.x >= 160):
                if(event.y >= 360):
                    self.move_x_minus()
                elif(event.y <= 120):
                    self.move_x_plus()
            else:
                if(event.y >= 360):
                    self.move_x_minus()
                    self.move_y_plus()
                elif(event.y >= 120):
                    self.move_y_plus()
                else:
                    self.move_x_plus()
                    self.move_y_plus()
    
    def set_shortcuts(self):
        secondary_window = tk.Toplevel()
        secondary_window.title("Secondary Window")
        secondary_window.config(width=300, height=200)
        first_col = tk.Label(master=secondary_window,text="Command")
        first_col.grid(row=0,column=0)
        second_col = tk.Label(master=secondary_window,text="Shortcut")
        second_col.grid(row=0,column=1)

        self.row_list = []
        row_c = 1
        for key in self.shortcuts_dict.keys():
            name, shortcut ,var = self.get_shortcuts_line(secondary_window,key)
            name.grid(row=row_c,column=0)
            shortcut.grid(row=row_c,column=1)
            self.row_list.append([name,shortcut,var])
            row_c += 1
        
        save_button = tk.Button(master=secondary_window,text="Save",command=self.save)
        save_button.grid(row=row_c,column=0)
        reset_button = tk.Button(master=secondary_window,text="Reset",command=self.reset)
        reset_button.grid(row=row_c,column=1)

    def save(self):
        for shorcut in self.row_list:
            self.shortcuts_dict_new[shorcut[0].cget("text")] = shorcut[2].get()

        with open("user_shortcuts.json","w") as FW:
            FW.write(json.dumps(self.shortcuts_dict_new,indent=1))
        self.shortcuts_dict = self.shortcuts_dict_new.copy()

    def reset(self):
        self.load_shortcuts(True)
        with open("user_shortcuts.json","w") as FW:
            FW.write(json.dumps(self.shortcuts_dict,indent=1))
        for shorcut in self.row_list:
            shorcut[2].set(self.shortcuts_dict[shorcut[0].cget("text")])

    def get_shortcuts_line(self,master,key):
        name = tk.Label(master=master,text=key)
        var = tk.StringVar(master=master)
        shortcut = tk.Entry(master=master,textvariable=var)
        shortcut.insert(0,self.shortcuts_dict[key])
        return name,shortcut,var

        
    def load_shortcuts(self,original:bool):
        if(original):
            with open("original_shortcuts.json","r") as FR:
                self.shortcuts_dict = json.load(FR)
        else:
            with open("user_shortcuts.json","r") as FR:
                self.shortcuts_dict = json.load(FR)   

    def center_chip(self):
        y = int((self.chip_size_pixel[0]-(640/2-self.chip_size_pixel[2]/2))/0.1) + self.positions[1]
        x = int((self.chip_size_pixel[1]-(480/2-self.chip_size_pixel[3]/2))/0.1) + self.positions[0]
        print("----")
        print(self.chip_size_pixel[2])
        print(self.chip_size_pixel[3])
        print(self.chip_size_pixel[0])
        print(self.chip_size_pixel[1])
        print(x)
        print(y)
        self.tmcm.move_to_abs(0,x)
        self.tmcm.move_to_abs(1,y)

    def find_center(self):
        self.tmcm.move_to_abs(0,41300)
        self.tmcm.move_to_abs(1,48800)

    def set_step_um(self):
        self.tmcm.unit = "um"
        self.unit = "um"
        self.step_mm.deselect()

    def set_step_mm(self):
        self.tmcm.unit = "mm"
        self.unit = "mm"
        self.step_um.deselect()

    
    def timer_100ms(self):
        target = self.magnification_deg[self.camera_mag_var.get()]
        self.tmcm.move_to_abs(4,target)
        if(self.camera_focus_var.get()):
            self.tmcm.move_to_abs(2,self.calculate_camera_position())
        self.after(1000,self.timer_100ms)

    def move_x_plus(self):
        if(self.unit == "mm"):
            target = self.positions[0] + self.step_var.get()*1000
        else:
            target = self.positions[0] + self.step_var.get()
        print(f"target; {target}")
        if(self.is_target_reachable(0,target)):
            self.tmcm.move_to_abs(0,target)
    
    def move_x_minus(self):
        if(self.unit == "mm"):
            target = self.positions[0] - self.step_var.get()*1000
        else:
            target = self.positions[0] - self.step_var.get()
        print(f"target; {target}")
        if(self.is_target_reachable(0,target)):
            self.tmcm.move_to_abs(0,target)

    def move_y_plus(self):
        if(self.unit == "mm"):
            target = self.positions[1] + self.step_var.get()*1000
        else:
            target = self.positions[1] + self.step_var.get()
        print(f"target; {target}")
        if(self.is_target_reachable(1,target)):
            self.tmcm.move_to_abs(1,target)
    
    def move_y_minus(self):
        if(self.unit == "mm"):
            target = self.positions[1] - self.step_var.get()*1000
        else:
            target = self.positions[1] - self.step_var.get()
        print(f"target; {target}")
        if(self.is_target_reachable(1,target)):
            self.tmcm.move_to_abs(1,target)

    def move_probe_up(self):
        if(self.unit == "mm"):
            target = self.positions[3] - self.step_var.get()*1000
        else:
            target = self.positions[3] - self.step_var.get()
        print(f"target; {target}")
        if(self.is_target_reachable(3,target)):
            self.tmcm.move_to_abs(3,target)

    def move_probe_down(self):
        if(self.unit == "mm"):
            target = self.positions[3] + self.step_var.get()*1000
        else:
            target = self.positions[3] + self.step_var.get()
        print(f"target; {target}")
        if(self.is_target_reachable(3,target)):
            self.tmcm.move_to_abs(3,target)


    def rotate_left(self):
        if(self.unit == "mm"):
            target = self.positions[5] - self.step_var.get()
        else:
            target = self.positions[5] - self.step_var.get()
        print(f"target; {target}")
        if(self.is_target_reachable(5,target)):
            self.tmcm.move_to_abs(5,target)

    def rotate_right(self):
        if(self.unit == "mm"):
            target = self.positions[5] + self.step_var.get()
        else:
            target = self.positions[5] + self.step_var.get()
        print(f"target; {target}")
        if(self.is_target_reachable(5,target)):
            self.tmcm.move_to_abs(5,target)

    def move_camera_down(self):
        if(self.unit == "mm"):
            target = self.positions[2] + self.step_var.get()*1000
        else:
            target = self.positions[2] + self.step_var.get()
        print(f"target; {target}")
        if(self.is_target_reachable(2,target)):
            self.tmcm.move_to_abs(2,target)

    def move_camera_up(self):
        if(self.unit == "mm"):
            target = self.positions[2] - self.step_var.get()*1000
        else:
            target = self.positions[2] - self.step_var.get()
        print(f"target; {target}")
        if(self.is_target_reachable(2,target)):
            self.tmcm.move_to_abs(2,target)

    def calculate_camera_position(self): 
        magnification = self.camera_mag_var.get()
        if(magnification == 5.6):
            focus_distance = 44700   
        elif(magnification >= 5):
            focus_distance = 44600
        elif(magnification >= 4):
            focus_distance = 44500
        elif(magnification >= 3):
            focus_distance = 44000 + int(500*(magnification-3))
        elif(magnification >= 2):
            focus_distance = 43000 + int(1000*(magnification-2))
        elif(magnification >= 1.5):
            focus_distance = 42000 + int(1000*(magnification-1.5))
        elif(magnification >= 1):
            focus_distance = 39000 + int(3000*(magnification-1))
        else:
            focus_distance = 31000 + int(8000*(magnification-0.7))

        return focus_distance

    def connect_tmcm(self,var):
        #call comand to connect port
        self.var_tmcm.set(var)
        print(f"{self.var_tmcm.get()} {9600}")
        self.tmcm.connect(self.var_tmcm.get(),9600)
        

    def connect_cam(self,var):
        #call comand to connect cam
        self.var_cam.set(var)
        self.video_capture = cv2.VideoCapture(int(self.var_cam.get()))

    def led_intensity_plus(self):
        self.tmcm.set_output(3,2,1)
        self.tmcm.set_output(3,2,0)

    def stop_tmcm(self):
        print("motors stop")
        for i in range(6):
            self.tmcm.motor_stop(i)
        
    def find_home(self):
        self.tmcm.find_all_references()

    def find_available_cameras(self):
        available_cameras = []
        index = 0
        while True:
            cap = cv2.VideoCapture(index)
            if not cap.isOpened():
                break
            available_cameras.append(index)
            cap.release()
            index += 1
        return available_cameras

    def update_webcam(self):
        ret, frame = self.video_capture.read()
        if ret:
            imgConter = frame.copy()
            if(self.find_chip_var.get()):
                imgBlur = cv2.GaussianBlur(frame,(7,7),1)
                imgGray = cv2.cvtColor(imgBlur,cv2.COLOR_BGR2GRAY)
                imgCanny = cv2.Canny(imgGray,self.th1_var.get(),self.th2_var.get())
                kernel = np.ones((5,5))
                imgDil = cv2.dilate(imgCanny,kernel,iterations=1)
                self.getConters(imgDil,imgConter,self.th3_var.get())
            self.current_image = Image.fromarray(imgConter)

            self.photo = ImageTk.PhotoImage(image=self.current_image) 
            self.canvas.create_image(0,0,image=self.photo,anchor=tk.NW)
            self.after(15,self.update_webcam)
    
    def getConters(self,img,imgConters,th):
        conters,hierarchy = cv2.findContours(img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        for cnt in conters:
            area = cv2.contourArea(cnt)
            if(area >= th):
                cv2.drawContours(imgConters,cnt,-1,(255,0,255),7)
                peri = cv2.arcLength(cnt,True)
                approx =  cv2.approxPolyDP(cnt,0.02*peri,True)
                # print(approx)
                x,y,w,h = cv2.boundingRect(approx)
                self.chip_size_pixel = [x,y,w,h]
                # print(f"{x} {y}")
                # print(approx.item((0,0,0)))
                # print("----")
                # print(f"{x},{y},{w},{h}")
                cv2.rectangle(imgConters,(x,y),(x+w,y+h),(0,255,0),5)

    def update_positon(self):
        self.tmcm.get_actual_positions()
        self.positions = self.tmcm.actual_positions
        
        self.position_x_val.config(text=str(self.positions[0]))
        self.position_y_val.config(text=str(self.positions[1]))
        self.position_cam_z_val.config(text=str(self.positions[2]))
        self.position_probe_z_val.config(text=str(self.positions[3]))
        self.position_table_angle_val.config(text=str(self.positions[5]))
        
        self.after(100,self.update_positon)

    def is_target_reachable(self,motor,distance):
        if(motor == 0):
            return self.is_distance_ok(target=distance,max_distance=96000) 
        elif(motor == 1):
            return self.is_distance_ok(target=distance,max_distance=86000) 
        elif(motor == 2):
            return self.is_distance_ok(target=distance,max_distance=70000) 
        elif(motor == 3):
            return self.is_distance_ok(target=distance,max_distance=50000) 
        elif(motor == 5):
            return self.is_distance_ok(target=distance,max_distance=270) 
        
    def is_distance_ok(self,target,max_distance):
        if(target >= max_distance):
            return 0
        elif(target <= 0):
            return 0
        else:
            return 1

gui = Gui()
gui.mainloop()
