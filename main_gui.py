import customtkinter as ctk
import time
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Create App
app = ctk.CTk()
app.title("PYNQ SoC Builder")
app.geometry("400x240")

# Title Label
title_label = ctk.CTkLabel(app, text="PYNQ SoC Builder")
title_label.pack(pady=10)

# File path entry and browse button
def browse_files():
    file_path = ctk.filedialog.askopenfilename(filetypes=[("HDLGen Files", "*.hdlgen")])
    entry_path.delete(0, ctk.END)
    entry_path.insert(0, file_path)

entry_path = ctk.CTkEntry(app, width=300)
entry_path.pack(pady=5, side=ctk.LEFT)
browse_button = ctk.CTkButton(app, text="Browse", command=browse_files)
browse_button.pack(pady=5, padx=5, side=ctk.LEFT)
# def button_function():
#     print("Button Pressed")

# button = ctk.CTkButton(master=app, text="ExButton",command=button_function)
# button.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

# entry_path = ctk.CTkEntry(app, width=150)
# entry_path.place(relx=0.5, rely=0.1, anchor=ctk.CENTER)

app.mainloop()