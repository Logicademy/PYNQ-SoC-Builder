import customtkinter as ctk
import os 
import threading
import time
import application.pynq_manager as pm
import pyperclip
import xml.dom.minidom
from tktooltip import ToolTip

import application.gui.io_toplevel as io_toplevel
import application.gui.main_menu as main_menu
import application.gui.in_progress_page as in_progress
import application.gui.io_config_page as io_config_page
import application.gui.popups as popups


ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class Application:

    def __init__(self, root):

        # Set root and title
        self.root = root
        self.root.title("PYNQ SoC Builder")
        self.root.geometry("500x240")
        self.root.resizable(False, False) # Dont let the window be resizable
        self.root.protocol("WM_DELETE_WINDOW", self.on_close) # Set function to handle close

        ## Shared variables (shared between pages)
        self.mode = None
        self.hdlgen_path = None
        self.checkbox_values = None

        # Shared Variables for Messages
        self.top_level_message = None
        self.dialog_response = None

        # Build Status Flags
        self.build_running = False              # If build process is running, this flag will be True
        self.vivado_force_quit_event = threading.Event()

        self.io_configuration = {
            "led0":"None",
            "led1":"None",
            "led2":"None",
            "led3":"None",
            "led4_b":"None",
            "led4_g":"None",
            "led4_r":"None",
            "led5_b":"None",
            "led5_g":"None",
            "led5_r":"None"
        }

        # Shared Tcl Generator Flags
        self.skip_board_config = False

        # Initalise app pages
        self.page1 = main_menu.Main_Menu(self)        # Main Menu
        self.page2 = in_progress.In_Progress_Page(self)        # Page Showing progress
        self.page3 = io_config_page.IO_Config_Page(self)   # IO Config Page
        # self.page4 = Summary_Page(self)        # Possible we create a summary page later 

        # Show Inital Page
        self.show_page(self.page1)

        # Initalise attribute toplevel_window
        self.toplevel_window = None

    def show_page(self, page):
        # Hide all existing pages
        # Possible we should make this iterate thru all pages to hide (more dynamic)
        # Should be ok for this small application
        self.page1.hide()
        self.page2.hide()
        self.page3.hide()
        page.show() # Show requested page.

    def open_alert(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = popups.Alert_Window(self) # Create window if None or destroyed
        else:
            self.toplevel_window.focus() # if window exists focus it.
    
    def open_dialog(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = popups.Dialog_Window(self) # Create window if None or destroyed
        else:
            self.toplevel_window.focus() # if window exists focus it.

    def open_io_led_window(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = io_toplevel.Led_Config_Window(self) # Create window if None or destroyed
        else:
            self.toplevel_window.focus() # if window exists focus it.
        # Wait for the user to close the window
        self.toplevel_window.wait_window()

    # Repeatitive code but this func called directly from button handler where can't pass parameters
    def open_remote_menu(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = popups.Remote_Window(self) # Create window if None or destroyed
        else:
            self.toplevel_window.focus() # if window exists focus it.
        # Wait for the user to close the window
        self.toplevel_window.wait_window()

    # Generic Function where the toplevel window is passed as argument.
    def open_toplevel_window(self, new_toplevel_window):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = new_toplevel_window
        else:
            self.toplevel_window.focus() # if window exists focus it.
        # Wait for the user to close the window
        self.toplevel_window.wait_window()

    
    def on_close(self):
        # find a way to check if there are any threads running...should we set a flag??
        # build_running
        if self.build_running:
            # Prompt user if they are sure:
            self.top_level_message = "A build is currently running, quitting now might cause unexpected results or behaviour. Are you sure?"
            self.open_dialog()

            # Wait for the user to click their response
            self.toplevel_window.wait_window()

            # print(self.dialog_response)
            response = self.dialog_response
            if response == "yes":
                # terminate process, by continuing past this if block
                self.vivado_force_quit_event.set()
                pass
            elif response == "no":
                # leave and take no action
                return
            else:
                print("Invalid response from Dialog, not quitting (default)")
                return
        # Quit behaviour:
        print("Quitting application")
        self.root.destroy() # kill tkinter window
        exit()              # quit app

if __name__ == "__main__":
    root = ctk.CTk()
    app = Application(root)
    root.mainloop()