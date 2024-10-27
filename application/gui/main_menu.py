import customtkinter as ctk
import os
import time
import application.gui.project_config_menu as pcm
import application.gui.log_menu as logm
import application.hdlgen_project as hdlgenprj
import webbrowser
import application.file_manager as fm
from application.config import * 
from PIL import Image
from application.builder_utils import *

ctk.set_appearance_mode("Dark")       # 'Light' 'Dark' or 'System
ctk.set_default_color_theme("blue")

#######################################################################
##### Sidebar Menu (Build, Gen, Launch FPGA, Help, Close Project) #####
#######################################################################
class SidebarMenu(ctk.CTkScrollableFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        # set the height of the internal scrollbar to zero
        # # then it will be expanded vertically to the configured height of "frame"
        self._scrollbar.configure(height=0)

        window_height = parent.app.get_window_height()

        self.configure(width=250, height=window_height/2)
        print(window_height/2)

        dummy_label = ctk.CTkLabel(self, text="dummy")
        default_font = dummy_label.cget("font")

        title_font = (default_font, 24, "bold")
        button_font = (default_font, 16, 'bold')

        # Green foreground and hover colours 
        green_fg_clr = "#1D8348"
        green_hv_clr = "#145a32"
        

        # Blue foreground and hover colours
        blue_fg_clr = "#2471A3"
        blue_hv_clr = "#1A5276"

        # Red foreground and hover colours
        red_fg_clr = "#CB4335"
        red_hv_clr = "#943126"

        # Yellow foreground and hover colours
        yellow_fg_clr = "#b7950b"
        yellow_hv_clr = "#7d6608"

        # Load the PNG with transparent areas
        current_mode = ctk.get_appearance_mode()
        print("Current appearance mode:", current_mode)
        if (current_mode == "Light"):
            
            image_path = get_resource_path('docs/images/pynq_title_app_light.png', os.path.abspath(__file__))
        else:
            image_path = get_resource_path('docs/images/pynq_title_app_dark.png', os.path.abspath(__file__))
        image = Image.open(image_path)

        # Convert the image to a format Tkinter can use
        tk_image = ctk.CTkImage(image, size=(250, 35))

        self.label = ctk.CTkLabel(self, text="", image=tk_image, font=title_font, width=250)
        self.label.grid(row=0, column=0, pady=10)

        self.build_button = ctk.CTkButton(
            self, 
            text="Build Project", 
            width=225, 
            height=40, 
            font=button_font,
            fg_color=green_fg_clr,
            hover_color=green_hv_clr,
            command=self.run_build
        )
        self.build_button.grid(row=1, column=0, pady=10)

        self.gen_jnb_button = ctk.CTkButton(
            self, 
            text="Create Jupyter Notebook", 
            width=225, 
            height=40, 
            font=button_font,
            fg_color=green_fg_clr,
            hover_color=green_hv_clr,
            command=self.run_notebook
        )
        self.gen_jnb_button.grid(row=2, column=0, pady=10)

        self.fpga_button = ctk.CTkButton(
            self,
            text="Launch FPGA",
            width=225,
            height=40,
            font=button_font,
            command=self.launch_fpga
        )
        
        if SHOW_LAUNCH_FPGA_BUTTON:
            self.fpga_button.grid(row=3, column=0, pady=10)

        self.open_dir_button = ctk.CTkButton(
            self,
            text="Open Project Directory",
            width=225,
            height=40,
            font=button_font,
            command=self.open_project_in_file_explorer
        )
        self.open_dir_button.grid(row=4, column=0, pady=10)

        self.help_button = ctk.CTkButton(
            self,
            text="Help", 
            width=225, 
            height=40, 
            font=button_font,
            fg_color=yellow_fg_clr,
            hover_color=yellow_hv_clr, 
            command=self.open_help   
        )
        self.help_button.grid(row=5, column=0, pady=10)

        self.close_button = ctk.CTkButton(
            self,
            text="Quit", 
            width=225, 
            height=40, 
            font=button_font,
            fg_color=red_fg_clr,
            hover_color=red_hv_clr,
            command=self.parent.app.close_application   # This can be changed to close_project another time.
        )
        self.close_button.grid(row=7, column=0, pady=10)

    def launch_fpga(self):
        # fm.upload_output_folder_to_direct_connect_pynq(self.hdlgen_prj)
        self.parent.app.open_fpga_popup()


    def resize(self, event):
        # print("SidebarMenu Menu is called")
        self.configure(height=(event.height/2))

    def open_help(self):
        self.parent.app.path_to_markdown = "README.md"
        self.parent.app.open_markdown()

    def load_project(self):
        self.hdlgen_prj = self.parent.hdlgen_prj
        self.hdlgen_prj.set_sidebar_lock_function(self.lock_build)
        self.hdlgen_prj.set_sidebar_unlock_function(self.unlock_build)

    def lock_build(self):
        self.build_button.configure(state='disabled')
        self.gen_jnb_button.configure(state='disabled')

    def unlock_build(self):
        self.build_button.configure(state='normal')
        self.gen_jnb_button.configure(state='normal')

    def run_build(self):
        # Check the I/O is valid.
        if not self.parent.configMenu.tab_view.ioconfigpage.check_io_is_valid():
            self.parent.app.top_level_message = "A port is connected to more than one board I/O, only one per signal is allowed."
            self.parent.app.open_alert()
            return

        # Call Synthesis Dialog Box
        self.parent.app.top_level_message = "Have you synthesised your project to ensure there are no HDL errors?"
        self.parent.app.open_dialog()
        # Wait for the user to click their response
        self.parent.app.toplevel_window.wait_window()

        if self.parent.app.dialog_response == "no":
            self.hdlgen_prj.add_to_build_log("\nCancelled Build Operation due to No response to dialog prompt")
            return
        self.hdlgen_prj.build_project()

    def run_notebook(self):

        self.hdlgen_prj.generate_jnb_solo()

    def open_project_in_file_explorer(self):
        # Find the directory of the project.
        self.open_dir(self.hdlgen_prj.location)
        pass


    def open_dir(self, path):
        if os.path.isdir(path):
            webbrowser.open('file://' + os.path.realpath(path))
        else:
            print("Not a valid directory path")

##########################################
##### Config Menu Frame (Top Config) #####
##########################################
class ConfigMenu(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        window_height = parent.app.get_window_height()
        window_width = parent.app.get_window_width()

        self.configure(width=window_width-290, height=window_height/2)


        dummy_label = ctk.CTkLabel(self, text="dummy")
        default_font = dummy_label.cget("font")

        title_font = (default_font, 24, "bold")
        button_font = (default_font, 16, 'bold')


        self.tab_view = pcm.ConfigTabView(self) # Project Config Menu = pcm
        self.tab_view.grid(row=0, column=0, padx=10, pady=5)

    def resize(self, event): 
        # print("Config Menu is called")
        # Handle how frame gets bigger and smaller.
        self.tab_view.configure(width=event.width-310, height=event.height/2)
        self.tab_view.resize(event)
        self.tab_view.project_config_scrollable.configure(width=event.width-330, height=event.height/2-80)

    def load_project(self):
        self.hdlgen_prj = self.parent.hdlgen_prj

        # set the hdlgen_prj object and then pass onwards to the ConfigTabView
        self.tab_view.load_project()


###################################
##### Log Menu Frame (Bottom) #####
###################################
class LogMenu(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent 

        window_height = parent.app.get_window_height()
        window_width = parent.app.get_window_width()

        self.configure(width=window_width, height=window_height/2)


        dummy_label = ctk.CTkLabel(self, text="dummy")
        default_font = dummy_label.cget("font")

        title_font = (default_font, 24, "bold")
        button_font = (default_font, 16, 'bold')

        self.tab_view = logm.LogTabView(self)
        self.tab_view.grid(row=0, column=0, padx=10, pady=5)

    def resize(self, event):
        # print("Log Menu is called")
        # Handle how frame gets bigger and smaller.
        self.tab_view.configure(width=event.width-20, height=(event.height/2)-20)
        self.tab_view.resize(event)

    def load_project(self):
        self.hdlgen_prj = self.parent.hdlgen_prj
        self.tab_view.load_project()

###############################################
##### Main Page (The Entire Window Frame) #####
###############################################
class MainPage(ctk.CTkFrame):
    def __init__(self, app):
        ctk.CTkFrame.__init__(self, app.root)
        self.app = app

        self.configure(
            height=self.app.get_window_height(),
            width=self.app.get_window_width()
        )

        self.columnconfigure(1, weight=1)
        
        # Initalise Sidebar Menu and Grid place
        self.sidebarMenu = SidebarMenu(self)
        self.sidebarMenu.grid(row=0, column=0, sticky='news')
        # Initalise Config Menu and Grid place
        self.configMenu = ConfigMenu(self)
        self.configMenu.grid(row=0, column=1, sticky='news')
        # Initalise Log Menu and Grid place
        self.logMenu = LogMenu(self)
        self.logMenu.grid(row=1, column=0, sticky='news', columnspan=2)

        # Bind the resize event to the frame
        # Left side menu bind 
        self.bind("<Configure>", self.sidebarMenu.resize)
        # Config Menu Bind
        self.bind("<Configure>", self.configMenu.resize)
        # Logging Area 
        self.bind("<Configure>", self.logMenu.resize)

    def close_project(self):
        self.app.hdlgen_path = None             # Reset HDLGen Proj variable
        self.app.show_page(self.app.page2)      # Show main menu again
        # This will require more checks in future

    def show(self):
        self.pack(fill="both", expand=True)
        self.pack_propagate(False)
        self.app.root.geometry("1200x800")
        self.app.root.minsize(800, 500)
        self.load_project()

    def load_project(self):
        # This is called when a project has been loaded.
        self.hdlgen_path = self.app.hdlgen_path # Make the HDLGen path available locally - Might also make this hdlgenproject.py
        self.app.hdlgen_prj = hdlgenprj.HdlgenProject(self.hdlgen_path)
        self.hdlgen_prj = self.app.hdlgen_prj
    
        # The following other classes need to be informed and passed the object:
        # 1) Log Tabs
        # 2) Config Tabs
        # 3) Sidebar Menu

        self.logMenu.load_project()
        self.configMenu.load_project()
        self.sidebarMenu.load_project()

        # Assuming all has been run to load the project, I can now call the function to write to log box
        # self.hdlgen_prj.add_to_build_log("Add a load project message running through the hdlgenprj object!!\n")

    def hide(self):
        self.pack_forget()
