"""
File: gui.py
Author: Tomas Kotian
Date: 15.5.2024
Description: Main file for application for Semiconductor chip testing machine
"""

import tkinter as tk
import cv2
from PIL import Image, ImageTk
import libs.TMCLcommand as tmc
import time
import numpy as np
import json
import libs.CamValues as cam


class Gui(tk.Tk, cam.Cam_values):
    def __init__(self):
        super().__init__()

        #Create menu
        self.menubar = tk.Menu(self)
        self.menu_file = tk.Menu(self.menubar, tearoff=0)

        #Add option into menu
        self.menubar.add_cascade(label="Settings", menu=self.menu_file)
        self.menu_file.add_checkbutton(label="active shortcuts")
        self.menu_file.add_command(label="Shortcuts", command=self.set_shortcuts)
        self.config(menu=self.menubar)

        #Application variables
        self.positions = []
        self.shortcuts_dict = {}
        self.shortcuts_dict_new = {}
        self.chip_size_pixel = []
        self.row_list = []
        self.led_intensity_target = 0
        self.led_intensity_var = 0
        self.unit = "mm"
        self.tmcm = tmc.TMCLcmd() #auto connect to TMCM-6110
        self.tmcm_ports = [
            f"{com}: {self.tmcm.get_ports()[com]}"
            for com in self.tmcm.get_ports().keys()
        ] # find all connected devices to USB ports
        cam_ports = self.find_available_cameras() 
        self.load_shortcuts(original=False)

        #Set up GUI window
        self.title("Semiconductor chip testing application")
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        self.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        self.state("zoomed")

        #Set up main grid 2X2 depedency of resizing
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        #Connect mouse an keyboard to commands
        self.bind("<Key>", self.key_pressed)
        self.bind("<MouseWheel>", self.wheel)
        self.bind("<Button-3>", self.change_unit)

        #Create sidebar frame
        self.sidebar_frame = tk.Frame(self, padx=10, pady=10, bg="#383838")
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9), weight=1)

        #Create camera frame
        self.camera_frame = tk.Frame(self, padx=200, pady=20, bg="#8A8A8A")
        self.camera_frame.grid(row=0, column=1, sticky="nsew")

        #Create downbar frame
        self.downbar_frame = tk.Frame(self, padx=10, pady=5)
        self.downbar_frame.grid(row=1, column=1, rowspan=1, sticky="nsew")
        self.downbar_frame.grid_columnconfigure((0, 1), weight=1)

        #Connections to TMCM-6110
        self.var_tmcm = tk.StringVar(self.sidebar_frame, self.tmcm.connection)
        self.tmcm_options = tk.OptionMenu(
            self.sidebar_frame,
            self.var_tmcm,
            *self.tmcm_ports,
            command=self.connect_tmcm,
        )
        self.tmcm_options.config(width=15)
        self.tmcm_options.grid(row=0, column=0, padx=5)

         #Connections to camera
        self.var_cam = tk.StringVar(self.sidebar_frame, "0")
        self.cam_options = tk.OptionMenu(
            self.sidebar_frame, self.var_cam, *cam_ports, command=self.connect_cam
        )
        self.cam_options.config(width=10)
        self.cam_options.grid(row=0, column=1, padx=5)

        #Variables camera proccesing
        self.video_capture = None
        self.current_image = None

        #Stop button
        self.stop_button = tk.Button(
            self.sidebar_frame,
            text=f"STOP <{self.shortcuts_dict['stop']}>",
            bg="red",
            width=30,
            height=4,
            command=self.stop_tmcm,
        )
        self.stop_button.grid(
            row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew"
        )

        #Create frame for positions
        self.position_frame = tk.Frame(self.sidebar_frame)
        self.position_frame.grid(row=2, column=0, columnspan=2)

        self.position_label = tk.Label(
            self.position_frame, text="Positions", bg="#8A8A8A"
        )
        self.position_label.grid(row=0, column=0, columnspan=3, sticky="nsew")

        #Position X
        self.position_x = tk.Label(self.position_frame, text="axis X", width=10)
        self.position_x.grid(row=1, column=0)
        self.position_x_val = tk.Label(self.position_frame, text="0", width=20)
        self.position_x_val.grid(row=1, column=1)
        self.position_x_unit = tk.Label(self.position_frame, text="um", width=10)
        self.position_x_unit.grid(row=1, column=2, sticky="nsew")

        #Position Y
        self.position_y = tk.Label(self.position_frame, text="axis Y", width=10)
        self.position_y.grid(row=2, column=0)
        self.position_y_val = tk.Label(self.position_frame, text="0", width=20)
        self.position_y_val.grid(row=2, column=1)
        self.position_y_unit = tk.Label(self.position_frame, text="um", width=10)
        self.position_y_unit.grid(row=2, column=2, sticky="nsew")

        #Position Z camera
        self.position_cam_z = tk.Label(self.position_frame, text="camera Z", width=10)
        self.position_cam_z.grid(row=3, column=0)
        self.position_cam_z_val = tk.Label(self.position_frame, text="0", width=20)
        self.position_cam_z_val.grid(row=3, column=1)
        self.position_cam_z_unit = tk.Label(self.position_frame, text="um", width=10)
        self.position_cam_z_unit.grid(row=3, column=2, sticky="nsew")

        #Position Z probe
        self.position_probe_z = tk.Label(self.position_frame, text="probe Z", width=10)
        self.position_probe_z.grid(row=4, column=0)
        self.position_probe_z_val = tk.Label(self.position_frame, text="0", width=20)
        self.position_probe_z_val.grid(row=4, column=1)
        self.position_probe_z_unit = tk.Label(self.position_frame, text="um", width=10)
        self.position_probe_z_unit.grid(row=4, column=2, sticky="nsew")

        #Position table angle
        self.position_table_angle = tk.Label(
            self.position_frame, text="table angle", width=10
        )
        self.position_table_angle.grid(row=5, column=0)
        self.position_table_angle_val = tk.Label(
            self.position_frame, text="0", width=20
        )
        self.position_table_angle_val.grid(row=5, column=1)
        self.position_table_angle_unit = tk.Label(
            self.position_frame, text="°", width=10
        )
        self.position_table_angle_unit.grid(row=5, column=2, sticky="nsew")

        #Create LED setting frame
        self.led_frame = tk.Frame(self.sidebar_frame)
        self.led_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=10)

        self.led_label = tk.Label(self.led_frame, text="Led intensity", bg="#8A8A8A")
        self.led_label.grid(row=0, column=0, sticky="nsew")

        self.intesity_led_var = tk.IntVar(self.led_frame)
        self.led_bar = tk.Scale(
            self.led_frame,
            variable=self.intesity_led_var,
            from_=0,
            to=100,
            resolution=4,
            length=300,
            orient=tk.HORIZONTAL,
        )
        self.led_bar.grid(row=1, column=0, columnspan=2)

        #LED settings buttons
        self.led_bar_key_p = tk.Label(
            self.led_frame, text=f"<{self.shortcuts_dict['LED intesity minus']}>"
        )
        self.led_bar_key_p.grid(row=2, column=0, sticky="w")
        self.led_bar_key_m = tk.Label(
            self.led_frame, text=f"<{self.shortcuts_dict['LED intesity plus']}>"
        )
        self.led_bar_key_m.grid(row=2, column=1, sticky="e")

        self.led_auto_var = tk.BooleanVar(self.led_frame, True)
        self.led_auto = tk.Checkbutton(
            self.led_frame,
            text=f"Automatic <{self.shortcuts_dict['LED automatic']}>",
            variable=self.led_auto_var,
        )
        self.led_auto.grid(row=0, column=1, padx=5)
        self.led_auto.select()

        #Create camera settings frame
        self.camera_setting_frame = tk.Frame(self.sidebar_frame)
        self.camera_setting_frame.grid(row=4, column=0, columnspan=2, sticky="nsew")

        self.camera_label = tk.Label(
            self.camera_setting_frame, text="Camera settings", bg="#8A8A8A"
        )
        self.camera_label.grid(row=0, column=0, columnspan=6, sticky="nsew")

        #Camera settings slider
        self.camera_mag_var = tk.DoubleVar(self.camera_setting_frame, 0.7)
        self.camera_mag = tk.Scale(
            self.camera_setting_frame,
            variable=self.camera_mag_var,
            from_=0.7,
            to=5.6,
            resolution=0.1,
            orient=tk.HORIZONTAL,
        )
        self.camera_mag.grid(row=1, column=0, columnspan=2, sticky="nswe")

        #Camera settings buttons
        self.camera_mag_p = tk.Label(
            self.camera_setting_frame,
            text=f"<{self.shortcuts_dict['magnification minus']}>",
        )
        self.camera_mag_p.grid(row=2, column=0, sticky="w")
        self.camera_mag_m = tk.Label(
            self.camera_setting_frame,
            text=f"<{self.shortcuts_dict['magnification plus']}>",
        )
        self.camera_mag_m.grid(row=2, column=1, sticky="e")

        self.camera_mag_label = tk.Label(
            self.camera_setting_frame, text="Magnification"
        )
        self.camera_mag_label.grid(row=1, column=2, rowspan=2)

        self.camera_up = tk.Button(
            self.camera_setting_frame,
            text=f"up<{self.shortcuts_dict['camera up']}>",
            command=self.move_camera_up,
        )
        self.camera_up.grid(row=3, column=0)

        self.camera_down = tk.Button(
            self.camera_setting_frame,
            text=f"down <{self.shortcuts_dict['camera down']}>",
            command=self.move_camera_down,
        )
        self.camera_down.grid(row=4, column=0)

        self.camera_focus_var = tk.BooleanVar(self.camera_setting_frame, value=True)
        self.camera_auto = tk.Checkbutton(
            self.camera_setting_frame,
            text=f"Automatic focus <{self.shortcuts_dict['camera automatic focus']}>",
            variable=self.camera_focus_var,
        )
        self.camera_auto.grid(row=3, column=2, rowspan=2, padx=5)

        #Image of camera on machine
        self.camera_canvas = tk.Canvas(
            self.camera_setting_frame,
            width=50,
            height=50,
        )
        self.camera_canvas.grid(row=3, column=1, rowspan=2)
        self.img_cam = tk.PhotoImage(
            file="sources/icons/camera.png"
        )
        self.camera_canvas.create_image(0, 0, image=self.img_cam, anchor="nw")

        #Create step frame
        self.step_frame = tk.Frame(self.sidebar_frame)
        self.step_frame.grid(row=6, column=0, columnspan=2, sticky="nsew", pady=10)

        self.step_um = tk.Checkbutton(
            self.step_frame,
            text=f"um <{self.shortcuts_dict['step um']}>",
            command=self.set_step_um,
        )
        self.step_um.grid(row=0, column=0, padx=5)

        self.step_mm = tk.Checkbutton(
            self.step_frame,
            text=f"mm <{self.shortcuts_dict['step mm']}>",
            command=self.set_step_mm,
        )
        self.step_mm.grid(row=0, column=1, padx=5)
        self.step_mm.select()

        self.step_var = tk.IntVar()
        self.step_slider = tk.Scale(
            self.step_frame,
            variable=self.step_var,
            from_=1,
            to=500,
            resolution=1,
            length=300,
            orient=tk.HORIZONTAL,
        )
        self.step_slider.grid(row=1, column=0, columnspan=2)

        self.step_p = tk.Label(
            self.step_frame, text=f"<{self.shortcuts_dict['step minus']}>"
        )
        self.step_p.grid(row=2, column=0, sticky="w")
        self.step_m = tk.Label(
            self.step_frame, text=f"<{self.shortcuts_dict['step plus']}>"
        )
        self.step_m.grid(row=2, column=1, sticky="e")

        #Create joystick frame
        self.joystick_frame = tk.Frame(self.sidebar_frame)
        self.joystick_frame.grid(row=7, column=0, columnspan=3, sticky="nsew", pady=10)

        self.joystick_table = tk.Label(self.joystick_frame, text="Table", bg="#8A8A8A")
        self.joystick_table.grid(row=0, column=0, columnspan=4, sticky="nsew")

        #joystick buttons
        self.table_r = tk.Button(
            self.joystick_frame,
            text=f"r <{self.shortcuts_dict['rotate right']}>",
            command=self.rotate_right,
        )
        self.table_r.grid(row=1, column=0)

        self.table_up = tk.Button(
            self.joystick_frame,
            text=f"up <{self.shortcuts_dict['table forward']}>",
            command=self.move_x_plus,
        )
        self.table_up.grid(row=1, column=1)

        self.table_l = tk.Button(
            self.joystick_frame,
            text=f"l <{self.shortcuts_dict['rotate left']}>",
            command=self.rotate_left,
        )
        self.table_l.grid(row=1, column=2)

        self.probe_up = tk.Button(
            self.joystick_frame,
            text=f"p_up <{self.shortcuts_dict['probe up']}>",
            command=self.move_probe_up,
        )
        self.probe_up.grid(row=1, column=3)

        self.table_left = tk.Button(
            self.joystick_frame,
            text=f"left <{self.shortcuts_dict['table left']}>",
            command=self.move_y_plus,
        )
        self.table_left.grid(row=2, column=0)

        #image of table on machine
        self.table_canvas = tk.Canvas(self.joystick_frame, width=50, height=50)
        self.table_canvas.grid(row=2, column=1)
        self.img_table = tk.PhotoImage(
            file="sources/icons/table.png"
        )
        self.table_canvas.create_image(0, 0, image=self.img_table, anchor="nw")

        self.table_right = tk.Button(
            self.joystick_frame,
            text=f"right <{self.shortcuts_dict['table right']}>",
            command=self.move_y_minus,
        )
        self.table_right.grid(row=2, column=2)

        #image of probe head on machine
        self.probe_canvas = tk.Canvas(self.joystick_frame, width=50, height=50)
        self.probe_canvas.grid(row=2, column=3)
        self.img_probe = tk.PhotoImage(
            file="sources/icons/probe_head.png"
        )
        self.probe_canvas.create_image(0, 0, image=self.img_probe, anchor="nw")

        self.table_down = tk.Button(
            self.joystick_frame,
            text=f"down <{self.shortcuts_dict['table backward']}>",
            command=self.move_x_minus,
        )
        self.table_down.grid(row=3, column=1)

        self.probe_down = tk.Button(
            self.joystick_frame,
            text=f"p_down <{self.shortcuts_dict['probe down']}>",
            command=self.move_probe_down,
        )
        self.probe_down.grid(row=3, column=3)

        #Create function frame
        self.function_frame = tk.Frame(self.downbar_frame)
        self.function_frame.grid(row=0, column=0, sticky="nswe", padx=5, pady=5)
        self.function_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        #fuction buttons
        self.function_home = tk.Button(
            self.function_frame,
            width=15,
            height=2,
            text=f"Home <{self.shortcuts_dict['home']}>",
            command=self.find_home,
        ).grid(column=0, row=0)
        self.function_center = tk.Button(
            self.function_frame,
            width=15,
            height=2,
            text=f"Center <{self.shortcuts_dict['center']}>",
            command=self.find_center,
        ).grid(column=1, row=0)
        self.function_find_chip = tk.Button(
            self.function_frame,
            width=15,
            height=2,
            text=f"Center chip <{self.shortcuts_dict['center chip']}>",
            command=self.center_chip,
        ).grid(column=2, row=0)

        self.function_click_move_var = tk.BooleanVar(self.function_frame, False)
        self.function_click_move = tk.Checkbutton(
            self.function_frame,
            variable=self.function_click_move_var,
            text=f"Click and move <{self.shortcuts_dict['click and move']}>",
        )
        self.function_click_move.grid(column=3, row=0)

        #Error massage box
        self.messages = tk.Message(
            self.function_frame, text="", anchor="e", bg="white", aspect=20000
        )
        self.messages.grid(row=1, column=0, columnspan=4, pady=5, padx=5, sticky="nswe")

        #Create find chip frame
        self.find_chip_frame = tk.Frame(self.downbar_frame)
        self.find_chip_frame.grid(column=1, row=0, padx=5, pady=5, sticky="nsew")
        self.find_chip_frame.grid_columnconfigure(1, weight=1)

        self.find_chip_var = tk.BooleanVar(self.find_chip_frame, False)
        self.function_find_chip = tk.Checkbutton(
            self.find_chip_frame,
            variable=self.find_chip_var,
            text=f"Find chip <{self.shortcuts_dict['find chip']}>",
            bg="#8A8A8A",
        )
        self.function_find_chip.grid(column=0, row=0, columnspan=2, sticky="nsew")

        #Scale for min. gradient for detection edge
        self.th1_l = tk.Label(self.find_chip_frame, text="min. gradient")
        self.th1_l.grid(row=2, column=0)
        self.th1_var = tk.IntVar(self.find_chip_frame, 120)
        self.th1 = tk.Scale(
            self.find_chip_frame,
            variable=self.th1_var,
            from_=0,
            to=255,
            resolution=4,
            length=300,
            orient=tk.HORIZONTAL,
        )
        self.th1.grid(row=2, column=1, sticky="nswe", pady=5, padx=5)

        #Scale for max. gradient for detection edge
        self.th2_l = tk.Label(self.find_chip_frame, text="max. gradient")
        self.th2_l.grid(row=3, column=0)
        self.th2_var = tk.IntVar(self.find_chip_frame, 100)
        self.th2 = tk.Scale(
            self.find_chip_frame,
            variable=self.th2_var,
            from_=0,
            to=255,
            resolution=4,
            length=300,
            orient=tk.HORIZONTAL,
        )
        self.th2.grid(row=3, column=1, sticky="nswe", pady=5, padx=5)

        #Scale for min. area to detect chip
        self.th3_l = tk.Label(self.find_chip_frame, text="min. area")
        self.th3_l.grid(row=4, column=0)
        self.th3_var = tk.IntVar(self.find_chip_frame, 2000)
        self.th3 = tk.Scale(
            self.find_chip_frame,
            variable=self.th3_var,
            from_=0,
            to=100000,
            resolution=4,
            length=300,
            orient=tk.HORIZONTAL,
        )
        self.th3.grid(row=4, column=1, sticky="nswe", pady=5, padx=5)

        self.find_param_var = tk.BooleanVar(self.find_chip_frame)
        self.find_param = tk.Checkbutton(
            self.find_chip_frame,
            text="Fixed parametres",
            variable=self.find_param_var,
            command=self.toggle_find_param,
        )
        self.find_param.grid(row=1, column=0, padx=5, pady=5, sticky="nswe")
        self.find_param.select()

        self.tmcm.find_all_references() #Find to initial posiotion
        self.toggle_find_param() #Set initial value for find chip parameter 

        self.canvas = tk.Canvas(self.camera_frame, width=640, height=480)   #Camera image
        self.canvas.bind("<Button-1>", self.coordinates) #Bind click for click and move function
        self.canvas.pack(anchor=tk.CENTER)

        #Camera update image condition
        if len(cam_ports):
            self.connect_cam(0)
        if self.video_capture != None:
            self.update_webcam()

        # Timer dependent funciton
        self.update_position()
        self.timer_100ms()
        self.timer_20ms()

    # ----------------------------------------------------------------------------------------------------
    # Methodes
    # ----------------------------------------------------------------------------------------------------

    def toggle_find_param(self):
        """
        Toggles the state of the find_param_var variable.
        If find_param_var is True, disables th1, th2, and th3.
        If find_param_var is False, enables th1, th2, and th3.
        """
        if self.find_param_var.get():
            self.th1.configure(state=tk.DISABLED)
            self.th2.configure(state=tk.DISABLED)
            self.th3.configure(state=tk.DISABLED)
        else:
            self.th1.configure(state=tk.NORMAL)
            self.th2.configure(state=tk.NORMAL)
            self.th3.configure(state=tk.NORMAL)

    def wheel(self, event):
        """
        Handles the mouse wheel event.
        Increments or decrements the step_var variable based on the direction of the mouse wheel.
        Limits the step_var value between 1 and 500.
        """
        if event.delta == -120:
            self.step_var.set(self.step_var.get() + 1)
            if self.step_var.get() == 500:
                self.step_var.set(1)
        else:
            self.step_var.set(self.step_var.get() - 1)
            if self.step_var.get() == 1:
                self.step_var.set(500)

    def change_unit(self, event):
        """
        Changes the unit between millimeters ("mm") and micrometers ("um").
        Updates the UI accordingly by selecting the appropriate radio button.
        """
        if self.unit == "mm":
            self.unit = "um"
            self.step_um.select()
            self.step_mm.deselect()
        elif self.unit == "um":
            self.unit = "mm"
            self.step_mm.select()
            self.step_um.deselect()


    def key_pressed(self, event):
        """
        Handles key press events and performs corresponding actions.
        Actions are connected via shortcuts settings.

        Args:
            event (tk.Event): The key press event.
        """
        print("Key pressed:", event.keysym)
        if event.keysym == self.shortcuts_dict["stop"]:
            self.stop_tmcm()
        elif event.keysym == self.shortcuts_dict["LED intesity plus"]:
            self.intesity_led_var.set(self.intesity_led_var.get() + 4)
            if self.intesity_led_var.get() == 100:
                self.intesity_led_var.set(0)
        elif event.keysym == self.shortcuts_dict["LED intesity minus"]:
            self.intesity_led_var.set(self.intesity_led_var.get() - 4)
            if self.intesity_led_var.get() == 0:
                self.intesity_led_var.set(100)
        elif event.keysym == self.shortcuts_dict["LED automatic"]:
            if self.led_auto_var.get():
                self.led_auto_var.set(False)
            else:
                self.led_auto_var.set(True)
        elif event.keysym == self.shortcuts_dict["magnification plus"]:
            self.camera_mag_var.set(round(self.camera_mag_var.get() + 0.1, 1))
            if self.camera_mag_var.get() == 5.6:
                self.camera_mag_var.set(0.7)
        elif event.keysym == self.shortcuts_dict["magnification minus"]:
            self.camera_mag_var.set(round(self.camera_mag_var.get() - 0.1, 1))
            if self.camera_mag_var.get() == 0.7:
                self.camera_mag_var.set(5.6)
        elif event.keysym == self.shortcuts_dict["camera automatic focus"]:
            if self.camera_focus_var.get():
                self.camera_focus_var.set(False)
            else:
                self.camera_focus_var.set(True)
        elif event.keysym == self.shortcuts_dict["camera up"]:
            self.move_camera_up()
        elif event.keysym == self.shortcuts_dict["camera down"]:
            self.move_camera_down()
        elif event.keysym == self.shortcuts_dict["rotate right"]:
            self.rotate_right()
        elif event.keysym == self.shortcuts_dict["table forward"]:
            self.move_x_plus()
        elif event.keysym == self.shortcuts_dict["rotate left"]:
            self.rotate_left()
        elif event.keysym == self.shortcuts_dict["table backward"]:
            self.move_x_minus()
        elif event.keysym == self.shortcuts_dict["table left"]:
            self.move_y_plus()
        elif event.keysym == self.shortcuts_dict["table right"]:
            self.move_y_minus()
        elif event.keysym == self.shortcuts_dict["probe up"]:
            self.move_probe_up()
        elif event.keysym == self.shortcuts_dict["probe down"]:
            self.move_probe_down()
        elif event.keysym == self.shortcuts_dict["home"]:
            self.find_home()
        elif event.keysym == self.shortcuts_dict["center"]:
            self.find_center()
        elif event.keysym == self.shortcuts_dict["center chip"]:
            self.center_chip()
        elif event.keysym == self.shortcuts_dict["click and move"]:
            if self.function_click_move_var.get():
                self.function_click_move_var.set(False)
            else:
                self.function_click_move_var.set(True)
        elif event.keysym == self.shortcuts_dict["find chip"]:
            if self.find_chip_var.get():
                self.find_chip_var.set(False)
            else:
                self.find_chip_var.set(True)

    def timer_20ms(self):
        """
        Handles a timer event occurring every 20 milliseconds.
        Adjusts LED intensity based on settings and updates error messages.

        """
        if self.led_auto_var.get():
            target = int(20 / 4)
        else:
            target = int(self.intesity_led_var.get() / 4)
        self.tmcm.set_output(3, 2, 0)
        time.sleep(0.005)
        if self.led_intensity_var != target:
            self.tmcm.set_output(3, 2, 1)
            self.led_intensity_var += 1
            if self.led_intensity_var >= 26:
                self.led_intensity_var = 0

        if len(self.tmcm.erros_list):
            print(self.tmcm.erros_list)
            new_text = ""
            try:
                for err in self.tmcm.erros_list:
                    new_text += str(err) + "\n"
            except:
                pass
            print(new_text)
            self.tmcm.erros_list.clear()
            self.messages.configure(text=new_text)

        self.after(15, self.timer_20ms)

    def coordinates(self, event):
        """
        Handles mouse click events and moves the system according to the clicked position.
        """
        print(event.x)
        print(event.y)
        if self.function_click_move_var.get():
            if event.x >= 480:
                if event.y >= 360:
                    self.move_x_minus()
                    self.move_y_minus()
                elif event.y >= 120:
                    self.move_y_minus()
                else:
                    self.move_x_plus()
                    self.move_y_minus()
            elif event.x >= 160:
                if event.y >= 360:
                    self.move_x_minus()
                elif event.y <= 120:
                    self.move_x_plus()
            else:
                if event.y >= 360:
                    self.move_x_minus()
                    self.move_y_plus()
                elif event.y >= 120:
                    self.move_y_plus()
                else:
                    self.move_x_plus()
                    self.move_y_plus()

    def set_shortcuts(self):
        """
        Opens a secondary window to allow users to set shortcuts.
        """
        secondary_window = tk.Toplevel()
        secondary_window.title("Secondary Window")
        secondary_window.config(width=300, height=200)
        first_col = tk.Label(master=secondary_window, text="Command")
        first_col.grid(row=0, column=0)
        second_col = tk.Label(master=secondary_window, text="Shortcut")
        second_col.grid(row=0, column=1)

        self.row_list = []
        row_c = 1
        for key in self.shortcuts_dict.keys():
            name, shortcut, var = self.get_shortcuts_line(secondary_window, key)
            name.grid(row=row_c, column=0)
            shortcut.grid(row=row_c, column=1)
            self.row_list.append([name, shortcut, var])
            row_c += 1

        save_button = tk.Button(master=secondary_window, text="Save", command=self.save)
        save_button.grid(row=row_c, column=0)
        reset_button = tk.Button(
            master=secondary_window, text="Reset", command=self.reset
        )
        reset_button.grid(row=row_c, column=1)

    def save(self):
        """
        Saves the user-defined shortcuts to a JSON file.
        """
        for shorcut in self.row_list:
            self.shortcuts_dict_new[shorcut[0].cget("text")] = shorcut[2].get()

        with open("sources/user/user_shortcuts.json", "w") as FW:
            FW.write(json.dumps(self.shortcuts_dict_new, indent=1))
        self.shortcuts_dict = self.shortcuts_dict_new.copy()

    def reset(self):
        """
        Resets the shortcuts to their default values.
        """
        self.load_shortcuts(True)
        with open("sources/user/user_shortcuts.json", "w") as FW:
            FW.write(json.dumps(self.shortcuts_dict, indent=1))
        for shorcut in self.row_list:
            shorcut[2].set(self.shortcuts_dict[shorcut[0].cget("text")])

    def get_shortcuts_line(self, master, key):
        """
        Returns a line of shortcuts for the secondary window.

        Args:
            master: The master window.
            key: The shortcut key.

        Returns:
            name: Label containing the command name.
            shortcut: Entry containing the shortcut.
            var: StringVar containing the shortcut value.
        """
        name = tk.Label(master=master, text=key)
        var = tk.StringVar(master=master)
        shortcut = tk.Entry(master=master, textvariable=var)
        shortcut.insert(0, self.shortcuts_dict[key])
        return name, shortcut, var

    def load_shortcuts(self, original: bool):
        """
        Loads shortcut settings from either original_shortcuts.json or user_shortcuts.json.

        Args:
            original (bool): If True, loads from original_shortcuts.json, else from user_shortcuts.json.
        """
        if original:
            with open("sources/libs/original_shortcuts.json", "r") as FR:
                self.shortcuts_dict = json.load(FR)
        else:
            with open("sources/user/user_shortcuts.json", "r") as FR:
                self.shortcuts_dict = json.load(FR)

    def center_chip(self):
        """
        Moves chip to center based on its size and position from find chip function.
        """
        y = (
            int((self.chip_size_pixel[0] - (640 / 2 - self.chip_size_pixel[2] / 2)) / 0.1)
            + self.positions[1]
        )
        x = (
            int((self.chip_size_pixel[1] - (480 / 2 - self.chip_size_pixel[3] / 2)) / 0.1)
            + self.positions[0]
        )
        print("----")
        print(self.chip_size_pixel[2])
        print(self.chip_size_pixel[3])
        print(self.chip_size_pixel[0])
        print(self.chip_size_pixel[1])
        print(x)
        print(y)
        self.tmcm.move_to_abs(0, x)
        self.tmcm.move_to_abs(1, y)

    def find_center(self):
        """
        Moves the system to find the center position.
        """
        self.tmcm.move_to_abs(0, 41300)
        self.tmcm.move_to_abs(1, 48800)
        self.tmcm.move_to_abs(5, 185)

    def set_step_um(self):
        """
        Sets the step unit to micrometers (um).
        """
        self.tmcm.unit = "um"
        self.unit = "um"
        self.step_mm.deselect()

    def set_step_mm(self):
        """
        Sets the step unit to millimeters (mm).
        """
        self.tmcm.unit = "mm"
        self.unit = "mm"
        self.step_um.deselect()

    def timer_100ms(self):
        """
        Handles a timer event occurring every 100 milliseconds.
        Moves the system to the target magnification and camera position if automatic focus is enabled.
        """
        target = self.magnification_deg[self.camera_mag_var.get()]
        self.tmcm.move_to_abs(4, target)
        if self.camera_focus_var.get():
            self.tmcm.move_to_abs(2, self.calculate_camera_position())
        self.after(1000, self.timer_100ms)


    def move_x_plus(self):
        """
        Moves the system along the X-axis in the positive direction by the step size.

        Checks if the target position is reachable before moving.
        """
        if self.unit == "mm":
            target = self.positions[0] + self.step_var.get() * 1000
        else:
            target = self.positions[0] + self.step_var.get()
        print(f"target; {target}")
        if self.is_target_reachable(0, target):
            self.tmcm.move_to_abs(0, target)

    def move_x_minus(self):
        """
        Moves the system along the X-axis in the negative direction by the step size.

        Checks if the target position is reachable before moving.
        """
        if self.unit == "mm":
            target = self.positions[0] - self.step_var.get() * 1000
        else:
            target = self.positions[0] - self.step_var.get()
        print(f"target; {target}")
        if self.is_target_reachable(0, target):
            self.tmcm.move_to_abs(0, target)

    def move_y_plus(self):
        """
        Moves the system along the Y-axis in the positive direction by the step size.

        Checks if the target position is reachable before moving.
        """
        if self.unit == "mm":
            target = self.positions[1] + self.step_var.get() * 1000
        else:
            target = self.positions[1] + self.step_var.get()
        print(f"target; {target}")
        if self.is_target_reachable(1, target):
            self.tmcm.move_to_abs(1, target)

    def move_y_minus(self):
        """
        Moves the system along the Y-axis in the negative direction by the step size.

        Checks if the target position is reachable before moving.
        """
        if self.unit == "mm":
            target = self.positions[1] - self.step_var.get() * 1000
        else:
            target = self.positions[1] - self.step_var.get()
        print(f"target; {target}")
        if self.is_target_reachable(1, target):
            self.tmcm.move_to_abs(1, target)

    def move_probe_up(self):
        """
        Moves the probe upwards by the step size.

        Checks if the target position is reachable before moving.
        """
        if self.unit == "mm":
            target = self.positions[3] - self.step_var.get() * 1000
        else:
            target = self.positions[3] - self.step_var.get()
        print(f"target; {target}")
        if self.is_target_reachable(3, target):
            self.tmcm.move_to_abs(3, target)

    def move_probe_down(self):
        """
        Moves the probe downwards by the step size.

        Checks if the target position is reachable before moving.
        """
        if self.unit == "mm":
            target = self.positions[3] + self.step_var.get() * 1000
        else:
            target = self.positions[3] + self.step_var.get()
        print(f"target; {target}")
        if self.is_target_reachable(3, target):
            self.tmcm.move_to_abs(3, target)

    def rotate_left(self):
        """
        Rotates the system to the left by the step size.

        Checks if the target position is reachable before rotating.
        """
        if self.unit == "mm":
            target = self.positions[5] - self.step_var.get()
        else:
            target = self.positions[5] - self.step_var.get()
        print(f"target; {target}")
        if self.is_target_reachable(5, target):
            self.tmcm.move_to_abs(5, target)

    def rotate_right(self):
        """
        Rotates the system to the right by the step size.

        Checks if the target position is reachable before rotating.
        """
        if self.unit == "mm":
            target = self.positions[5] + self.step_var.get()
        else:
            target = self.positions[5] + self.step_var.get()
        print(f"target; {target}")
        if self.is_target_reachable(5, target):
            self.tmcm.move_to_abs(5, target)

    def move_camera_down(self):
        """
        Moves the camera down by the step size.

        Checks if the target position is reachable before moving.
        """
        if self.unit == "mm":
            target = self.positions[2] + self.step_var.get() * 1000
        else:
            target = self.positions[2] + self.step_var.get()
        print(f"target; {target}")
        if self.is_target_reachable(2, target):
            self.tmcm.move_to_abs(2, target)

    def move_camera_up(self):
        """
        Moves the camera up by the step size.

        Checks if the target position is reachable before moving.
        """
        if self.unit == "mm":
            target = self.positions[2] - self.step_var.get() * 1000
        else:
            target = self.positions[2] - self.step_var.get()
        print(f"target; {target}")
        if self.is_target_reachable(2, target):
            self.tmcm.move_to_abs(2, target)

    def calculate_camera_position(self):
        """
        Calculates the focus distance for the camera based on the selected magnification.

        Returns:
            int: The calculated focus distance.
        """
        magnification = self.camera_mag_var.get()
        if magnification == 5.6:
            focus_distance = 44700
        elif magnification >= 5:
            focus_distance = 44600
        elif magnification >= 4:
            focus_distance = 44500
        elif magnification >= 3:
            focus_distance = 44000 + int(500 * (magnification - 3))
        elif magnification >= 2:
            focus_distance = 43000 + int(1000 * (magnification - 2))
        elif magnification >= 1.5:
            focus_distance = 42000 + int(1000 * (magnification - 1.5))
        elif magnification >= 1:
            focus_distance = 39000 + int(3000 * (magnification - 1))
        else:
            focus_distance = 31000 + int(8000 * (magnification - 0.7))

        return focus_distance

    def connect_tmcm(self, var):
        """
        Connects to the TMCM controller using the specified port.

        Args:
            var: The port to connect to.
        """
        self.var_tmcm.set(var)
        print(f"{self.var_tmcm.get()} {9600}")
        self.tmcm.connect(self.var_tmcm.get(), 9600)

    def connect_cam(self, var):
        """
        Connects to the camera using the specified port.

        Args:
            var: The port to connect to.
        """
        self.var_cam.set(var)
        self.video_capture = cv2.VideoCapture(int(self.var_cam.get()))

    def led_intensity_plus(self):
        """
        Increases the LED intensity by setting the LED output on and then off.

        This method effectively increments the LED intensity setting.
        """
        self.tmcm.set_output(3, 2, 1)
        self.tmcm.set_output(3, 2, 0)

    def stop_tmcm(self):
        """
        Stops all motors connected to the TMCM controller.

        This method sends a command to stop each motor individually.
        """
        print("motors stop")
        for i in range(6):
            self.tmcm.motor_stop(i)

    def find_home(self):
        """
        Initiates the process to find the home position for all axes.

        This method sends a command to the TMCM controller to find the home position
        for all axes connected to the system.
        """
        self.tmcm.find_all_references()

    def find_available_cameras(self):
        """
        Finds available camera devices connected to the system.

        Returns:
        list: A list of indices representing available camera devices.
        """
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
        """
        Updates the displayed webcam image and performs contour detection if enabled.

        This method reads a frame from the video capture device, applies contour detection if
        the 'find_chip_var' variable is set, updates the displayed image on the canvas, and
        schedules itself to run again after a delay.

        The contour detection process is performed recursively with a delay of 15 milliseconds.

        Note: This method assumes 'self.video_capture' is a valid VideoCapture object.

        """
        ret, frame = self.video_capture.read()  # Read a frame from the video capture device
        if ret:  # If the frame is successfully read
            imgConter = frame.copy()  # Create a copy of the frame
            if self.find_chip_var.get():  # Check if contour detection is enabled
                imgBlur = cv2.GaussianBlur(frame, (7, 7), 1)  # Apply Gaussian blur
                imgGray = cv2.cvtColor(imgBlur, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
                imgCanny = cv2.Canny(imgGray, self.th1_var.get(), self.th2_var.get())  # Apply Canny edge detection
                kernel = np.ones((5, 5))  # Define a kernel for dilation
                imgDil = cv2.dilate(imgCanny, kernel, iterations=1)  # Perform dilation
                self.getConters(imgDil, imgConter, self.th3_var.get())  # Perform contour detection
            self.current_image = Image.fromarray(imgConter)  # Convert the processed frame to Image format

            self.photo = ImageTk.PhotoImage(image=self.current_image)  # Convert Image to PhotoImage for displaying on the canvas
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)  # Display the image on the canvas
            self.after(15, self.update_webcam)  # Schedule the method to run again after a delay

    def getConters(self, img, imgConters, th):
        """
        Performs contour detection on the provided image.

        Args:
            img: The image to perform contour detection on.
            imgConters: The image on which contours will be drawn.
            th: The threshold value for contour area.

        This method finds contours in the provided image and draws them on 'imgConters' if
        their area is greater than or equal to the specified threshold value.

        """
        conters, hierarchy = cv2.findContours(  # Find contours in the image
            img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
        )
        for cnt in conters:  # Iterate through the detected contours
            area = cv2.contourArea(cnt)  # Calculate the area of the contour
            if area >= th:  # If the area is greater than or equal to the threshold
                cv2.drawContours(imgConters, cnt, -1, (255, 0, 255), 7)  # Draw the contour on 'imgConters'
                peri = cv2.arcLength(cnt, True)  # Calculate the perimeter of the contour
                approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)  # Approximate the contour with a polygon
                x, y, w, h = cv2.boundingRect(approx)  # Get the bounding box coordinates
                self.chip_size_pixel = [x, y, w, h]  # Update the chip size information
                cv2.rectangle(imgConters, (x, y), (x + w, y + h), (0, 255, 0), 5)  # Draw the bounding box

    def update_position(self):
        """
        Updates the displayed positions of various components.

        This method retrieves the actual positions from the TMCM controller,
        updates the GUI elements displaying these positions, and schedules
        itself to run again after a delay.

        The positions are updated recursively with a delay of 100 milliseconds.

        Note: This method assumes 'self.tmcm' is a valid TMCM controller object.

        """
        self.tmcm.get_actual_positions()  
        self.positions = self.tmcm.actual_positions  

        self.position_x_val.config(text=str(self.positions[0]))
        self.position_y_val.config(text=str(self.positions[1]))
        self.position_cam_z_val.config(text=str(self.positions[2]))
        self.position_probe_z_val.config(text=str(self.positions[3]))
        self.position_table_angle_val.config(text=str(self.positions[5]))

        self.after(100, self.update_position)  

    def is_target_reachable(self, motor, distance):
        """
        Checks if the target distance is reachable for the specified motor.

        Args:
            motor (int): The motor index.
            distance (int): The target distance.

        Returns:
            int: 1 if the target distance is reachable, 0 otherwise.

        This method checks if the target distance is within the reachable range
        for the specified motor.

        """
        if motor == 0:
            return self.is_distance_ok(target=distance, max_distance=96000)
        elif motor == 1:
            return self.is_distance_ok(target=distance, max_distance=86000)
        elif motor == 2:
            return self.is_distance_ok(target=distance, max_distance=45000)
        elif motor == 3:
            return self.is_distance_ok(target=distance, max_distance=53000)
        elif motor == 5:
            return self.is_distance_ok(target=distance, max_distance=270)

    def is_distance_ok(self, target, max_distance):
        """
        Checks if the target distance is within the reachable range.

        Args:
            target (int): The target distance.
            max_distance (int): The maximum reachable distance.

        Returns:
            int: 1 if the target distance is within the reachable range, 0 otherwise.

        This method checks if the target distance is within the reachable range
        defined by the maximum distance.

        """
        if target >= max_distance:  
            return 0 
        elif target <= 0:  
            return 0  
        else:  
            return 1  


# ----------------------------------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------------------------------

gui = Gui()
gui.mainloop()
