python import tkinter as tk

def call_me_when_button_is_pressed(*args){
    print("Button pressed")
}

if KANDY_MAIN:
    root = tk.Tk()
    root.geometry("240x400")
    label = tk.Label(root, text="VivaKandyScript")
    label.pack()
    button = tk.Button(root, text="Button",
                       command=call_me_when_button_is_pressed)
    button.pack()
    root.mainloop()