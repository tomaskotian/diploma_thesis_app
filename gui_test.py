import tkinter as tk
from tkinter import scrolledtext
import cv2
from PIL import Image,ImageTk
import TMCLcommand as tmc


class Gui(tk.Tk):
    def __init__(self):
        super().__init__()

        self.tmcm = tmc.TMCLcmd()
        tmcm_ports = [f"{com}: {self.tmcm.get_ports()[com]}" for com in self.tmcm.get_ports().keys()]

        cam_ports = self.find_available_cameras()

        self.title("Hello world")
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        self.geometry(f"{self.screen_width}x{self.screen_height}")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self.sidebar_frame = tk.Frame(self,width=200,bg="grey",padx=10,pady=10)
        self.sidebar_frame.grid(row=0,column=0,rowspan=2,sticky="nsew")

        self.camera_frame = tk.Frame(self,width=100,bg="green",padx=200,pady=50)
        self.camera_frame.grid(row=0,column=1,rowspan=1,sticky="nsew")

        self.downbar_frame = tk.Frame(self,width=100,height=200,bg="red",padx=10,pady=5)
        self.downbar_frame.grid(row=1,column=1,rowspan=1,sticky="nsew")

        self.var_tmcm = tk.StringVar(self.sidebar_frame,"Select port")
        self.tmcm_options = tk.OptionMenu(self.sidebar_frame,self.var_tmcm,*tmcm_ports,command=self.connect_tmcm)
        self.tmcm_options.config(width=10)
        self.tmcm_options.grid(row=0,column=0,padx=5)

        self.var_cam = tk.StringVar(self.sidebar_frame,"Select cam")
        self.cam_options = tk.OptionMenu(self.sidebar_frame,self.var_cam,*cam_ports,command=self.connect_cam)
        self.cam_options.config(width=10)
        self.cam_options.grid(row=0,column=1,padx=5)

        self.stop_button = tk.Button(self.sidebar_frame,text="STOP",bg="red",width=30,height=4,command=self.stop_tmcm)
        self.stop_button.grid(row=1,column=0,columnspan=2,padx=5,pady=5)

        self.position_frame = tk.Frame(self.sidebar_frame,bg="white")
        self.position_frame.grid(row=2,column=0,columnspan=2,sticky="nsew")

        self.position_label = tk.Label(self.position_frame,text="Positions")
        self.position_label.grid(row=0,column=0,columnspan=3,sticky="nsew")

        self.position_x = tk.Label(self.position_frame,text="axis X",width=10)
        self.position_x.grid(row=1,column=0)
        self.position_x_val = tk.Label(self.position_frame,text="0",width=20)
        self.position_x_val.grid(row=1,column=1)
        self.position_x_unit = tk.Label(self.position_frame,text="um",width=10)
        self.position_x_unit.grid(row=1,column=2)

        self.position_y = tk.Label(self.position_frame,text="axis Y",width=10)
        self.position_y.grid(row=2,column=0)
        self.position_y_val = tk.Label(self.position_frame,text="0",width=20)
        self.position_y_val.grid(row=2,column=1)
        self.position_y_unit = tk.Label(self.position_frame,text="um",width=10)
        self.position_y_unit.grid(row=2,column=2)

        self.position_cam_z = tk.Label(self.position_frame,text="camera Z",width=10)
        self.position_cam_z.grid(row=3,column=0)
        self.position_cam_z_val = tk.Label(self.position_frame,text="0",width=20)
        self.position_cam_z_val.grid(row=3,column=1)
        self.position_cam_z_unit = tk.Label(self.position_frame,text="um",width=10)
        self.position_cam_z_unit.grid(row=3,column=2)

        self.position_probe_z = tk.Label(self.position_frame,text="probe Z",width=10)
        self.position_probe_z.grid(row=4,column=0)
        self.position_probe_z_val = tk.Label(self.position_frame,text="0",width=20)
        self.position_probe_z_val.grid(row=4,column=1)
        self.position_probe_z_unit = tk.Label(self.position_frame,text="um",width=10)
        self.position_probe_z_unit.grid(row=4,column=2)

        self.position_table_angle = tk.Label(self.position_frame,text="table angle",width=10)
        self.position_table_angle.grid(row=5,column=0)
        self.position_table_angle_val = tk.Label(self.position_frame,text="0",width=20)
        self.position_table_angle_val.grid(row=5,column=1)
        self.position_table_angle_unit = tk.Label(self.position_frame,text="°",width=10)
        self.position_table_angle_unit.grid(row=5,column=2)

        self.led_frame = tk.Frame(self.sidebar_frame,bg="green")
        self.led_frame.grid(row=3,column=0,columnspan=2,sticky="nsew",pady=10)

        self.led_label = tk.Label(self.led_frame,text="Led intensity")
        self.led_label.grid(row=0,column=0,columnspan=2,sticky="nsew")
        
        self.led_var = tk.IntVar()
        self.led_slider = tk.Scale(self.led_frame,variable=self.led_var, from_=0, to=100,resolution=4,length=200, orient=tk.HORIZONTAL)
        self.led_slider.grid(row=1,column=0)

        self.led_auto = tk.Checkbutton(self.led_frame,text="Automatic")
        self.led_auto.grid(row=1,column=1,padx=5)

        self.camera_setting_frame = tk.Frame(self.sidebar_frame,bg="yellow")
        self.camera_setting_frame.grid(row=4,column=0,columnspan=2,sticky="nsew")

        self.camera_label = tk.Label(self.camera_setting_frame,text="Camera settings")
        self.camera_label.grid(row=0,column=0,columnspan=4,sticky="nsew")

        self.camera_mag_var = tk.IntVar() 
        self.camera_mag = tk.Scale(self.camera_setting_frame,variable=self.camera_mag_var, from_=1, to=5.6, resolution=0.1, orient=tk.HORIZONTAL)
        self.camera_mag.grid(row=1,column=0,columnspan=2)

        self.camera_mag_label = tk.Label(self.camera_setting_frame,text="Magnification")
        self.camera_mag_label.grid(row=1,column=2)

        self.camera_up = tk.Button(self.camera_setting_frame,text="up")
        self.camera_up.grid(row=2,column=0)

        self.camera_down = tk.Button(self.camera_setting_frame,text="down")
        self.camera_down.grid(row=3,column=0)

        self.camera_canvas = tk.Canvas(self.camera_setting_frame,width=50,height=50)
        self.camera_canvas.grid(row=2,column=1,rowspan=2)

        self.camera_auto = tk.Checkbutton(self.camera_setting_frame,text="Automatic focus")
        self.camera_auto.grid(row=2,column=2,rowspan=2,padx=5)

        self.step_frame = tk.Frame(self.sidebar_frame,bg="red")
        self.step_frame.grid(row=6,column=0,columnspan=2,sticky="nsew",pady=10)

        self.step_um = tk.Checkbutton(self.step_frame,text="um")
        self.step_um.grid(row=0,column=1,padx=5)

        self.step_mm = tk.Checkbutton(self.step_frame,text="mm")
        self.step_mm.grid(row=0,column=2,padx=5)

        self.step_var = tk.IntVar()
        self.led_slider = tk.Scale(self.step_frame,variable=self.step_var, from_=0, to=500,resolution=1,length=300, orient=tk.HORIZONTAL)
        self.led_slider.grid(row=1,column=0,columnspan=3)

        self.joystick_frame = tk.Frame(self.sidebar_frame,bg="blue")
        self.joystick_frame.grid(row=6,column=0,columnspan=2,sticky="nsew",pady=10)

        self.joystick_table = tk.Label(self.joystick_frame,text="Table")
        self.joystick_table.grid(row=0,column=0,columnspan=3,sticky="nsew")

        self.table_r = tk.Button(self.joystick_frame,text="r")
        self.table_r.grid(row=1,column=0)

        self.table_up = tk.Button(self.joystick_frame,text="up")
        self.table_up.grid(row=1,column=1)

        self.table_l = tk.Button(self.joystick_frame,text="l")
        self.table_l.grid(row=1,column=2)

        self.probe_up = tk.Button(self.joystick_frame,text="p_up")
        self.probe_up.grid(row=1,column=3)

        self.table_left = tk.Button(self.joystick_frame,text="left")
        self.table_left.grid(row=2,column=0)
        
        self.table_canvas = tk.Canvas(self.joystick_frame,width=50,height=50)
        self.table_canvas.grid(row=2,column=1)

        self.table_right = tk.Button(self.joystick_frame,text="right")
        self.table_right.grid(row=2,column=2)

        self.probe_canvas = tk.Canvas(self.joystick_frame,width=50,height=50)
        self.probe_canvas.grid(row=2,column=3)

        self.table_down = tk.Button(self.joystick_frame,text="down")
        self.table_down.grid(row=3,column=1)

        self.probe_down = tk.Button(self.joystick_frame,text="p_down")
        self.probe_down.grid(row=3,column=3)

        self.function_home = tk.Button(self.downbar_frame,width=15,height=2,text="Home").grid(column=0,row=0)
        self.function_center = tk.Button(self.downbar_frame,width=15,height=2,text="Center").grid(column=1,row=0)
        self.function_rotate = tk.Button(self.downbar_frame,width=15,height=2,text="Auto rotate").grid(column=1,row=0)
        self.function_find_obj = tk.Button(self.downbar_frame,width=15,height=2,text="Find object").grid(column=2,row=0)
        self.function_center_obj = tk.Button(self.downbar_frame,width=15,height=2,text="Center object").grid(column=3,row=0)
        self.function_click_move = tk.Button(self.downbar_frame,width=15,height=2,text="Click and move").grid(column=4,row=0)

        self.messages = scrolledtext.ScrolledText(self.downbar_frame,wrap=tk.WORD,width=100,height=10)
        self.messages.bind('<Key>',lambda e: "break")
        self.messages.grid(row=1,column=0,columnspan=5,pady=2)

        # self.video_capture = cv2.VideoCapture(0)
        # self.current_image = None
        self.canvas = tk.Canvas(self.camera_frame,width=640,height=480)
        self.canvas.pack(anchor=tk.CENTER,side="right")
        # self.update_webcam()


    def connect_tmcm(self,var):
        #call comand to connect port
        print(f"{self.var_tmcm.get()}")
        pass

    def connect_cam(self,var):
        #call comand to connect cam
        print(f"{self.var_cam.get()}")
        pass

    def stop_tmcm(self):
        #call commad to stop 
        print("tmcm stop")
        for i in range(6):
            self.tmcm.motor_stop(i)
        pass
        
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
            self.current_image = Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
            self.photo = ImageTk.PhotoImage(image=self.current_image) 
            self.canvas.create_image(0,0,image=self.photo,anchor=tk.NW)
            self.after(15,self.update_webcam)

gui = Gui()
gui.mainloop()
