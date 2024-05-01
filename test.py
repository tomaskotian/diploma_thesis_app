import tkinter as tk

app = tk.Tk()

def click(event):
    print(var.get())

var = tk.StringVar()
ent = tk.Entry(app,textvariable=var)
ent.pack(side='right')
app.bind("<Button-1>",click)



app.mainloop()