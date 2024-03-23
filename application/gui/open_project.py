import customtkinter as ctk
import os

class OpenProjectPage(ctk.CTkFrame):
    def __init__(self, app):
        super().__init__(app.root)
        self.app = app

        dummy_label = ctk.CTkLabel(self, text="dummy")
        default_font = dummy_label.cget("font")

        self.title_font = (default_font, 24, 'bold')
        self.button_font = (default_font, 16, 'bold')
        self.sub_text_font = (default_font, 16)
        self.error_font = (default_font, 14)
        
        inner_frame = ctk.CTkFrame(self)

        self.title_text = ctk.CTkLabel(inner_frame, text="PYNQ SoC Builder", font=self.title_font)
        self.sub_text = ctk.CTkLabel(inner_frame, text="Open a HDLGen-ChatGPT project to continue.", font=self.sub_text_font)
        self.browse_button = ctk.CTkButton(inner_frame, text="Browse", command=self.browse_projects, font=self.button_font)
        self.help_button = ctk.CTkButton(inner_frame, text="Help", command=self.show_help_popup, font=self.button_font)
        self.file_not_found_lbl = ctk.CTkLabel(inner_frame, text="HDLGen project could not be found.", font=self.sub_text_font, text_color='#e74c3c')
        self.file_not_hdlgen_lbl = ctk.CTkLabel(inner_frame, text="File is not a HDLGen (.hdlgen) project file.", font=self.sub_text_font, text_color='#e74c3c')

        self.title_text.grid(row=0, column=0, padx=5, pady=5, columnspan=2)
        self.sub_text.grid(row=1, column=0, padx=5, pady=5, columnspan=2)
        self.browse_button.grid(row=2, column=0, padx=5, pady=5)
        self.help_button.grid(row=2, column=1, padx=5, pady=5)

        inner_frame.pack()

    def show_help_popup(self):
        # This API might be the exact same as the help button inside project menu. 
        # API call will be at higher level (application level) 
        print("Help Button Pressed")

    def browse_projects(self):
        file_path = ctk.filedialog.askopenfilename(filetypes=[("HDLGen Files", "*.hdlgen")])
        # print(file_path)
        # 1. Check the project exists
        # 2. If it exists, progress to the next screen
        # 3. Make red text telling user an invalid file was chosen
        file_path = file_path.replace("\\", "/")
        if file_path == "":
            pass    # User clicked cancel, don't need to do anything
        elif file_path.endswith(".hdlgen") and os.path.exists(file_path):
            # Path Exists, proceed - Also grid forget red warning text if its there.
            # This is because if user closes project returning to main menus
            self.file_not_found_lbl.grid_forget()
            self.file_not_hdlgen_lbl.grid_forget()
            self.app.hdlgen_path = file_path            # Assign shared variable
            self.app.show_page(self.app.page1)               # Proceed to main menu
        elif os.path.exists(file_path):
            self.file_not_hdlgen_lbl.grid(row=3, column=0, padx=5, pady=5, columnspan=2)
        else:
            self.file_not_found_lbl.grid(row=3, column=0, padx=5, pady=5, columnspan=2)

    def resize(self, event):
        self.configure(width=event.width, height=event.height)

    def show(self):
        # self.configure(width=1200, height=800)
        self.pack(expand=True)
        self.app.root.minsize(400, 200)
        self.app.root.geometry("400x200")
        # self.app.root.configure(bg_color="gray")

    def hide(self):
        self.pack_forget()