import customtkinter as ctk
import time
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Create App
app = ctk.CTk()
app.title("PYNQ SoC Builder")
app.geometry("500x240")


## Row 0
# Title Label
title_font = ("Segoe UI", 20, "bold") # Title font
title_label = ctk.CTkLabel(app, text="PYNQ SoC Builder", font=title_font)

## Row 1
# File path entry and browse button
def browse_files():
    file_path = ctk.filedialog.askopenfilename(filetypes=[("HDLGen Files", "*.hdlgen")])
    entry_path.delete(0, ctk.END)
    entry_path.insert(0, file_path)

entry_path = ctk.CTkEntry(app, width=360)
browse_button = ctk.CTkButton(app, text="Browse", command=browse_files, width=100)

## Row 2
mode_font = ("Segoe UI", 16)
mode_label = ctk.CTkLabel(app, text="Mode", font=mode_font, pady=5, width=20)

mode_menu_options = ["Run All", "Generate Tcl", "Run Vivado", "Copy Bitstream", "Create JNB /w Testplan", "Create JNB w/o Testplan"]
mode_menu_var = ctk.StringVar(app)
mode_menu_var.set(mode_menu_options[0])

def on_mode_dropdown(choice):
    print("Selected option: ", choice)

mode_dropdown = ctk.CTkOptionMenu(app, variable=mode_menu_var, values=mode_menu_options, command=on_mode_dropdown, width=150)


title_label.grid(row=0, column=0, columnspan=2, pady=5)
entry_path.grid(row=1, column=0, padx=10, pady=5)
browse_button.grid(row=1, column=1, padx=10, pady=5)
mode_label.grid(row=2, column=0, pady=5, padx=10)
mode_dropdown.grid(row=2, column=1, pady=5, padx=10)

# def button_function():
#     print("Button Pressed")

# button = ctk.CTkButton(master=app, text="ExButton",command=button_function)
# button.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

# entry_path = ctk.CTkEntry(app, width=150)
# entry_path.place(relx=0.5, rely=0.1, anchor=ctk.CENTER)

app.mainloop()