import tkinter as tk
import cv2
from PIL import Image,ImageTk
import serial.tools.list_ports

class WebcamApp:
    def __init__(self,window):
        self.window = window
        self.window.title("WebcamApp")

        self.video_capture = cv2.VideoCapture(0)

        self.current_image = None

        self.canvas = tk.Canvas(window,width=640,height=480)
        self.canvas.pack()

        self.update_webcam()

    def update_webcam(self):
        ret, frame = self.video_capture.read()

        if ret:
            self.current_image = Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))

            self.photo = ImageTk.PhotoImage(image=self.current_image)

            self.canvas.create_image(0,0,image=self.photo,anchor=tk.NW)

            self.window.after(15,self.update_webcam)

class Usb:
    def __init__(self):
        self.devices = None

    def print_devices(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            # Check if the port is a USB serial port
            if "USB" in port.description:
                print("Port:", port.device)
                print("  - Description:", port.description)
                print("  - Hardware ID:", port.hwid)
                print("  - Manufacturer:", port.manufacturer)
                print("  - Product:", port.product)
                print("  - Serial Number:", port.serial_number)
                print()

usb_con = Usb()
usb_con.print_devices()

# root = tk.Tk()

# app = WebcamApp(root)

# root.mainloop()