import customtkinter as ctk
import time
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Create App
app = ctk.CTk()
app.title("PYNQ SoC Builder")
app.geometry("500x240")

row_0_frame = ctk.CTkFrame(app, width=500, height=30)
row_1_frame = ctk.CTkFrame(app, width=500, height=30)
row_2_frame = ctk.CTkFrame(app, width=500, height=30)
row_last_frame = ctk.CTkFrame(app, width=500, height=30)

row_0_frame.grid(row=0)
row_1_frame.grid(row=1)
row_2_frame.grid(row=2)
row_last_frame.grid(row=3)

## Row 0
# Title Label
title_font = ("Segoe UI", 20, "bold") # Title font
title_label = ctk.CTkLabel(row_0_frame, text="PYNQ SoC Builder", font=title_font, padx=10)
title_label.grid(row=0, column=0, columnspan=2, pady=5)

## Row 1
# File path entry and browse button
def browse_files():
    file_path = ctk.filedialog.askopenfilename(filetypes=[("HDLGen Files", "*.hdlgen")])
    entry_path.delete(0, ctk.END)
    entry_path.insert(0, file_path)
entry_path = ctk.CTkEntry(row_1_frame, width=360)
browse_button = ctk.CTkButton(row_1_frame, text="Browse", command=browse_files, width=100)
entry_path.grid(row=1, column=0, padx=10, pady=5)
browse_button.grid(row=1, column=1, padx=10, pady=5)

## Row 2
# Select Mode
mode_font = ("Segoe UI", 16)
mode_label = ctk.CTkLabel(row_2_frame, text="Mode", font=mode_font, pady=5, width=20)

mode_menu_options = ["Run All", "Generate Tcl", "Run Vivado", "Copy Bitstream", "Gen JNB /w Testplan", "Gen JNB w/o Testplan"]
mode_menu_var = ctk.StringVar(app)
mode_menu_var.set(mode_menu_options[0])

def on_mode_dropdown(choice):
    print("Selected option: ", choice)

mode_dropdown = ctk.CTkOptionMenu(row_2_frame, variable=mode_menu_var, values=mode_menu_options, command=on_mode_dropdown, width=150)
mode_label.grid(row=2, column=0, pady=5, padx=10)
mode_dropdown.grid(row=2, column=1, pady=5, padx=10)

## Last Row
def on_run_button():
    print(entry_path.get())
    print(mode_menu_var.get())

# Go Button
run_button = ctk.CTkButton(row_last_frame, text="Run", command=on_run_button)
run_button.grid(row=0, column=0, pady=5)

# Place








app.mainloop()