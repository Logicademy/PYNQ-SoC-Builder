import customtkinter as ctk
import csv
import webbrowser

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

class Remote_Window(ctk.CTkToplevel):
    def __init__(self, app):
        ctk.CTkToplevel.__init__(self, app.root)
        self.app = app
        self.title("Open PYNQ Remote Webpages")
        self.grab_set() # This makes the pop-up the primary window and doesn't allow interaction with main menu
        self.geometry("300x100")
        # self.resizable(False, False) # Dont let the window be resizable
        
        # We are going to read from a file which contains the data
        # All the info related to remote servers is now stored in /application/remote.csv
        # This file could be upgraded to a XML file in the future but CSV is fine for now
        csv_file_path = "application/remote.csv"
        csv_data = []
        error_message = None
        try:
            with open(csv_file_path, 'r') as file:
                csv_reader = csv.reader(file)
                
                for row in csv_reader:
                    # Ignore lines starting with #
                    if not row or row[0].startswith('#'):
                        continue
                    csv_data.append(row)
        except FileNotFoundError:
            error_message = "\nFile 'remote.csv' file is missing. Remote servers cannot be listed."

        if csv_data == []:
            # If the CSV data is empty, I want to show error menu
            icon_font = ("Segoe Fluent Icons Regular", 80)
            
            self.left_frame = ctk.CTkFrame(self, width=100, height=100)
            self.right_frame = ctk.CTkFrame(self, width=200, height=100)

            self.label = ctk.CTkLabel(self.left_frame, text="\uedae", font=icon_font, width=100, height=100)
            self.label.pack()
            
            if error_message:
                self.error_text = error_message
            else:
                self.error_text = "\nNo Servers Listed in Config"
            
            self.msglabel = ctk.CTkLabel(self.right_frame, text=self.error_text, width=200, height=100, wraplength=180, anchor="n")
            self.msglabel.pack()
            
            self.left_frame.grid(column=0, row=0)
            self.right_frame.grid(column=1, row=0)
        else:
            header_font = ("Segoe UI", 16, "bold") # Title font
            self.popup_frame = ctk.CTkFrame(self, width=300, height=100) # Main frame to store everything

            self.top_label = ctk.CTkLabel(self.popup_frame, width=200, height=30, text="Open Remote Lab", corner_radius=0, font=header_font)
            self.top_label.grid(row=0, column=0, pady=5)
            # Run a loop for each line in the CSV
            current_row = 1
            for link in csv_data:
                # print(link)
                # link = [name, url]
                button = ctk.CTkButton(self.popup_frame, text=link[0], width=140, command=lambda: self.button_press(link[1]) )
                button.grid(row=current_row, column=0, pady=5, padx=5)
                # Link is gonna be handled by the button handler I suppose.
                current_row = current_row + 1

            # Here we need to add close button
            return_button = ctk.CTkButton(self.popup_frame, text="OK", width=140, command=self.on_return)
            return_button.grid(row=current_row, column=0, padx=5, pady=5)
        
            window_width = 200
            window_height = (len(csv_data) + 1) * 40 + 30
            window_size = f"{str(window_width)}x{str(window_height)}"
            self.geometry(window_size)

        self.popup_frame.pack()

    def button_press(self, url):
        # Make sure to .strip the url because if space, silly Edge opens and bing searches the address
        # instead of opening on the user's default browser
        webbrowser.open(url.strip())

    def on_return(self):
        # On return button we dont need to do anything
        # except to destroy the window
        self.destroy()