import customtkinter as ctk

class Alert_Window(ctk.CTkToplevel):
    def __init__(self, app):
        ctk.CTkToplevel.__init__(self, app.root)
        self.app = app
        # self.attributes('-topmost', 'true')
        self.title("Alert")
        self.grab_set() # This makes the pop-up the primary window and doesn't allow interaction with main menu
        self.geometry("300x100")
        icon_font = ("Segoe Fluent Icons Regular", 80)
        self.resizable(False, False) # Dont let the window be resizable
        
        self.left_frame = ctk.CTkFrame(self, width=100, height=100)
        self.right_frame = ctk.CTkFrame(self, width=200, height=100)

        self.label = ctk.CTkLabel(self.left_frame, text="\uedae", font=icon_font, width=100, height=100)
        self.label.pack()

        self.error_text = "\n"+self.app.top_level_message
        self.msglabel = ctk.CTkLabel(self.right_frame, text=self.error_text, width=200, height=100, wraplength=180, anchor="n")
        self.msglabel.pack()
        
        self.left_frame.grid(column=0, row=0)
        self.right_frame.grid(column=1, row=0)


class Dialog_Window(ctk.CTkToplevel):
    def __init__(self, app):
        ctk.CTkToplevel.__init__(self, app.root)
        self.app = app
        self.title("Dialog")
        self.grab_set() # This makes the pop-up the primary window and doesn't allow interaction with main menu
        self.geometry("300x140")
        icon_font = ("Segoe Fluent Icons Regular", 80)
        self.resizable(False, False) # Dont let the window be resizable
        
        self.left_frame = ctk.CTkFrame(self, width=100, height=100)
        self.right_frame = ctk.CTkFrame(self, width=200, height=100)
        self.button_frame = ctk.CTkFrame(self, width=300, height=50)

        self.label = ctk.CTkLabel(self.left_frame, text="\uf142", font=icon_font, width=100, height=100)
        self.label.pack()

        self.question = "\n"+self.app.top_level_message
        self.msglabel = ctk.CTkLabel(self.right_frame, text=self.question, width=200, height=100, wraplength=180, anchor="n")
        self.msglabel.pack()
        

        def _on_yes_button():
            # set var
            # close window
            self.app.dialog_response = "yes"
            self.destroy()

        def _on_no_button():
            # set var
            # close window
            self.app.dialog_response = "no"
            self.destroy()  

        self.button_frame = ctk.CTkFrame(self, width=300, height=50)
        self.yes_button = ctk.CTkButton(self.button_frame, text="Yes", command=_on_yes_button)
        self.yes_button.grid(row=0, column=0, pady=5, padx=5)
        self.no_button = ctk.CTkButton(self.button_frame, text="No", command=_on_no_button)
        self.no_button.grid(row=0, column=1, pady=5, padx=5)

        self.left_frame.grid(column=0, row=0)
        self.right_frame.grid(column=1, row=0)
        self.button_frame.grid(column=0, row=1, columnspan=2)