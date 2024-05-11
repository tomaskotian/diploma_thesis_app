import tkinter as tk

root = tk.Tk() 
root.geometry("640x480") 

camera_canvas = tk.Canvas(root,width=50,height=50,bg="red")
camera_canvas.grid(row=0,column=0)
img_cam = tk.PhotoImage(file="D:/skola/Ing/Dimplomka/SW/diploma_thesis_app/icons/camera.png")
camera_canvas.create_image(0,0,image=img_cam,anchor="nw")

root.mainloop() 
