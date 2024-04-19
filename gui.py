import tkinter as tk
#Semiconductor chip testing application
def set_window_to_screen_size(window):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window.geometry(f"{screen_width}x{screen_height}")


root = tk.Tk()

root.title("Semiconductor chip testing application")
set_window_to_screen_size(root)

root.mainloop()