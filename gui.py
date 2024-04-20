import tkinter as tk
import TMCLcommand as tmc
from tkinter import scrolledtext

#Semiconductor chip testing application
#custom tkinters

class Window:
    def __init__(self,window) -> None:
        self.screen_width = window.winfo_screenwidth()
        self.screen_height = window.winfo_screenheight()
        window.geometry(f"{self.screen_width}x{self.screen_height}")

def create_frame(master,row,column,bg,rowspan=1,columnspan=1) -> tk.Frame:
    new_frame = tk.Frame(master,bg=bg,highlightbackground="blue", highlightthickness=2)
    # new_frame.grid_columnconfigure() set resize options
    new_frame.grid(row=row,column=column,rowspan=rowspan,columnspan=columnspan,sticky="nsew")
    return new_frame

def option_menu(master):
    var = tk.StringVar(master,"COM8")
    option_menu = tk.OptionMenu(master,var,var.get(),"1","2","3")
    option_menu.config(width=10)
    option_menu.pack(side="left")
    return option_menu

def create_button(master):
    button = tk.Button(master,text="Connect")
    button.config(width=10)
    button.pack(side="left")
    return button

def create_stop_button(master):
    button = tk.Button(master,text="STOP",bg="red")
    button.config(width=40,height=3)
    button.pack(side="left")
    return button

def create_row_table(master,row,name,unit):
    position_x = tk.Label(master,text=name).grid(row=row,column=0)
    value_x = tk.Label(master,text="1").grid(row=row,column=1)
    unit_x = tk.Label(master,text=unit).grid(row=row,column=2)

    return value_x

def create_check_button(master,name):
    return tk.Checkbutton(master,text=name).pack(side="left")
        
def create_slider(master,min,max):
    v = tk.DoubleVar() 
    slider = tk.Scale(master, variable=v, from_=min, to=max, orient=tk.HORIZONTAL)  
    slider.pack(side="left")  
    return slider

def create_camera_ui(master):
    v = tk.DoubleVar()
    camera_mag_slider = tk.Scale(master, variable=v, from_=1, to=5.6, orient=tk.HORIZONTAL)
    camera_mag_slider.grid(row=0,column=0,columnspan=3)

    camera_button_up =  tk.Button(master,text="up")
    camera_button_up.config(width=5,height=2)
    camera_button_up.grid(row=1,column=0)

    camera_button_down =  tk.Button(master,text="down")
    camera_button_down.config(width=5,height=2)
    camera_button_down.grid(row=2,column=0)

    camera_img = tk.Canvas(master=master, bg="grey",height=50,width=50)
    camera_img.grid(row=1,column=1,rowspan=2)

    camera_focus = tk.Checkbutton(master,text="Automatic")
    camera_focus.grid(row=1,column=2,rowspan=2)

def create_step_settings(master):
    step_mm = tk.Checkbutton(master,text="mm")
    step_mm.grid(row=0,column=0)

    step_um = tk.Checkbutton(master,text="um")
    step_um.grid(row=0,column=1)

    v = tk.DoubleVar()
    camera_mag_slider = tk.Scale(master, variable=v, from_=1, to=100, orient=tk.HORIZONTAL)
    camera_mag_slider.grid(row=1,column=0,columnspan=2)

def create_joistick(master):
    rotate_r = tk.Button(master,text="rot_r")
    rotate_r.config(width=4,height=2)
    rotate_r.grid(row=0,column=0)

    x_up = tk.Button(master,text="x_up")
    x_up.config(width=4,height=2)
    x_up.grid(row=0,column=1)

    x_down = tk.Button(master,text="x_down")
    x_down.config(width=4,height=2)
    x_down.grid(row=2,column=1)

    y_left = tk.Button(master,text="y_left")
    y_left.config(width=4,height=2)
    y_left.grid(row=1,column=0)

    y_right = tk.Button(master,text="y_right")
    y_right.config(width=4,height=2)
    y_right.grid(row=1,column=2)

    table_img = tk.Canvas(master=master, bg="grey",height=50,width=50)
    table_img.grid(row=1,column=1)

    rotate_l = tk.Button(master,text="rot_l")
    rotate_l.config(width=4,height=2)
    rotate_l.grid(row=0,column=2)

    probe_up = tk.Button(master,text="probe_up")
    probe_up.config(width=4,height=2)
    probe_up.grid(row=0,column=3)

    probe_img = tk.Canvas(master=master, bg="grey",height=50,width=50)
    probe_img.grid(row=1,column=3)

    probe_down = tk.Button(master,text="probe_down")
    probe_down.config(width=4,height=2)
    probe_down.grid(row=2,column=3)

#------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------
root = tk.Tk()

root.title("Semiconductor chip testing application")
window = Window(root)

connection_frame = create_frame(root,0,0,bg="red")
stop_frame = create_frame(root,1,0,bg="green")
position_frame = create_frame(root,2,0,bg="grey")
led_frame = create_frame(root,3,0,bg="red")
camera_setting_frame = create_frame(root,4,0,bg="green")
step_frame = create_frame(root,5,0,bg="grey")
joystick_frame = create_frame(root,6,0,bg="red")

camera_frame = create_frame(root,0,1,rowspan=5,bg="green")
functions_frame = create_frame(root,5,1,bg="grey")
messages_frame = create_frame(root,6,1,bg="red")

tmcm_menu = option_menu(connection_frame)
tmcm_button = create_button(connection_frame)
camera_menu = option_menu(connection_frame)
camera_button = create_button(connection_frame)

stop_button = create_stop_button(stop_frame)

position_table_x = create_row_table(position_frame,0,"axis X","um")
position_table_y = create_row_table(position_frame,1,"axis Y","um")
position_table_cam = create_row_table(position_frame,2,"camera Z","um")
position_table_probe = create_row_table(position_frame,3,"probe Z","um")
position_table_table = create_row_table(position_frame,4,"table angle","°")


led_slider = create_slider(led_frame,0,100)
led_automatic = create_check_button(led_frame,"Automatic")

create_camera_ui(camera_setting_frame)

create_step_settings(step_frame)

create_joistick(joystick_frame)



def cordinates(event):
    print(f"x:{event.x} y:{event.y}")

camera = tk.Canvas(camera_frame,width=1920/2,height=1080/2,bg="grey")
camera.bind('<Button-1>',cordinates)
camera.pack()

function_home = tk.Button(functions_frame,width=5,height=2,text="Home").grid(column=0,row=0)
function_center = tk.Button(functions_frame,width=5,height=2,text="Center").grid(column=1,row=0)
function_find_obj = tk.Button(functions_frame,width=15,height=2,text="Find object").grid(column=2,row=0)
function_center_obj = tk.Button(functions_frame,width=15,height=2,text="Center object").grid(column=3,row=0)
function_click_move = tk.Button(functions_frame,width=15,height=2,text="Click and move").grid(column=4,row=0)

messages = scrolledtext.ScrolledText(messages_frame,wrap=tk.WORD,width=100,height=10)
messages.bind('<Key>',lambda e: "break")
messages.pack(side="left")

messages.insert(tk.END,"hello")
#---------------------------------------------------------------------------------
# tmcm = tmc.TMCLcmd()

# tmcm_connection_var = tk.StringVar(root) 
# tmcm_connection_var.set("Select an Option")

# tmcm_con_opt = [f"{com}: {tmcm.get_ports()[com]}" for com in tmcm.get_ports().keys()]

# tmcm_connection = tk.OptionMenu(connection_frame,tmcm_connection_var,*tmcm_con_opt)
# tmcm_connection.config(width=15)
# tmcm_connection.pack(side="left")

# def call_back_tmcm_connection_button():
#     tmcm_connection_button.config(text="Disconnect")

# def call_back_cam_connection_button():
#    cam_connection_button.config(text="Disconnect")

# tmcm_connection_button = tk.Button(connection_frame,text="Connect",command=call_back_tmcm_connection_button)
# tmcm_connection_button.config(width=15)
# tmcm_connection_button.pack(side="left")

# cam_connection = tk.OptionMenu(connection_frame,tmcm_connection_var,*tmcm_con_opt)
# cam_connection.config(width=15)
# cam_connection.pack(side="left")

# cam_connection_button = tk.Button(connection_frame,text="Connect",command=call_back_cam_connection_button)
# cam_connection_button.config(width=15)
# cam_connection_button.pack(side="left")

# cam_frame = tk.Frame(root,highlightbackground="yellow", highlightthickness=2)
# cam_frame.grid(row=0,column=1 ,sticky=tk.E)

# cam_box = tk.Canvas(cam_frame, bg="grey", height=window.screen_height*0.75,width=window.screen_width*0.6)
# cam_box.pack(side="right",anchor=tk.E)

root.resizable(False,False)
root.mainloop()