import customtkinter as ctk
import time
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("400x240")

def button_function():
    print("Button Pressed")

button = ctk.CTkButton(master=app, text="ExButton",command=button_function)
button.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

app.mainloop()