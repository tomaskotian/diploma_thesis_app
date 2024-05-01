import tkinter as tk
import time


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.clicked = False
        self.rectangle_position = []

        self.frame = tk.Frame(self,bg='red',width=500,height=500)
        self.frame.grid(row=0,column=0,sticky="nswe")

        self.canva = tk.Canvas(self.frame,width=500,height=500)
        self.canva.pack(fill="both")
        self.canva.bind("<Button-1>",self.click)
        self.canva.bind("<B1-Motion>",self.draw_rectangle)
        self.myrectangle = self.canva.create_rectangle(0,0,0,0)

    def draw_rectangle(self,event):
        if(self.clicked):
            self.rectangle_position =[event.x,event.y]
            self.clicked = False

        self.canva.coords(self.myrectangle,self.rectangle_position[0],self.rectangle_position[1],event.x,event.y)


    def click(self,event):
        if(self.clicked):
            self.clicked = False
        else:
            self.clicked = True

        
        



app = App()

app.mainloop()

    