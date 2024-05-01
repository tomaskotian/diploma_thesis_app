import tkinter as tk
import cv2
from PIL import Image,ImageTk
import serial.tools.list_ports
import numpy as np
import math

class WebcamApp:
    def __init__(self,window):
        self.window = window
        self.window.title("WebcamApp")

        self.th1_var = tk.IntVar(self.window,105) 
        self.th1 = tk.Scale(self.window,variable=self.th1_var, from_=0, to=255, resolution=1, orient=tk.HORIZONTAL)
        self.th1.grid(row=0,column=0)

        self.th2_var = tk.IntVar(self.window,80) 
        self.th2 = tk.Scale(self.window,variable=self.th2_var, from_=0, to=255, resolution=1, orient=tk.HORIZONTAL)
        self.th2.grid(row=1,column=0)

        self.th3_var = tk.IntVar(self.window,5000) 
        self.th3 = tk.Scale(self.window,variable=self.th3_var, from_=1, to=100000, resolution=1000, orient=tk.HORIZONTAL)
        self.th3.grid(row=2,column=0)


        #---camera----#
        self.video_capture = cv2.VideoCapture(0)
        self.current_image = None
        self.canvas = tk.Canvas(window,width=640,height=480)
        self.canvas.grid(row=3,column=0)
        self.update_webcam()
        #---camera----#

    #---camera----#
    def update_webcam(self):
        ret, frame = self.video_capture.read()
        if ret:
            imgConter = frame.copy()

            imgBlur = cv2.GaussianBlur(frame,(7,7),1)
            imgGray = cv2.cvtColor(imgBlur,cv2.COLOR_BGR2GRAY)

            imgCanny = cv2.Canny(imgGray,self.th1_var.get(),self.th2_var.get())
            
            kernel = np.ones((5,5))
            imgDil = cv2.dilate(imgCanny,kernel,iterations=1)

            self.getConters(imgDil,imgConter,self.th3_var.get())

            self.current_image = Image.fromarray(imgConter)
            self.photo = ImageTk.PhotoImage(image=self.current_image)
            self.canvas.create_image(0,0,image=self.photo,anchor=tk.NW)
            self.window.after(100,self.update_webcam)

    def getConters(self,img,imgConters,th):
        counters,hierarchy = cv2.findContours(img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        for cnt in counters:
            area = cv2.contourArea(cnt)
            if(area >= th):
                cv2.drawContours(imgConters,cnt,-1,(255,0,255),7)
                peri = cv2.arcLength(cnt,True)
                approx =  cv2.approxPolyDP(cnt,0.02*peri,True)
                print(approx)
                x,y,w,h = cv2.boundingRect(approx)
                print(f"{x} {y}")
                print(approx.item((0,0,0)))
                cv2.circle(imgConters, (x,y), radius=0, color=(0, 0, 255), thickness=10) #blue
                print("----")
                print(f"{x},{y},{w},{h}")
                cv2.rectangle(imgConters,(x,y),(x+w,y+h),(0,255,0),5)


root = tk.Tk()

app = WebcamApp(root)

root.mainloop()