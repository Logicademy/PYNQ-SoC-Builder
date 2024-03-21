import customtkinter as ctk
import os
import time
import application.gui.ConfigPages.project_config_menu as pcm
import application.gui.LogPages.log_menu as logm
import application.hdlgenproject as hdlgenprj

ctk.set_appearance_mode("System")       # 'Light' 'Dark' or 'System
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

        self.label = ctk.CTkLabel(self, text="PYNQ SoC Builder", font=title_font, width=250)
        self.label.grid(row=0, column=0, pady=10)

        self.build_button = ctk.CTkButton(
            self, 
            text="Build Project", 
            width=225, 
            height=40, 
            font=button_font,
            fg_color=green_fg_clr,
            hover_color=green_hv_clr
        )
        self.build_button.grid(row=1, column=0, pady=10)
        self.build_button = ctk.CTkButton(
            self, 
            text="Create Jupyter Notebook", 
            width=225, 
            height=40, 
            font=button_font,
            fg_color=green_fg_clr,
            hover_color=green_hv_clr
        )
        self.build_button.grid(row=2, column=0, pady=10)

        self.build_button = ctk.CTkButton(self, text="Launch FPGA", width=225, height=40, font=button_font)
        self.build_button.grid(row=3, column=0, pady=10)
        # self.build_button = ctk.CTkButton(self, text="Local FPGA", width=225, height=40, font=button_font)
        # self.build_button.grid(row=4, column=0, pady=10)

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

        self.build_button = ctk.CTkButton(
            self,
            text="Close Project", 
            width=225, 
            height=40, 
            font=button_font,
            fg_color=red_fg_clr,
            hover_color=red_hv_clr,
            command=self.parent.close_project
        )
        self.build_button.grid(row=6, column=0, pady=10)

    def resize(self, event):
        # print("SidebarMenu Menu is called")
        self.configure(height=(event.height/2))

    def open_help(self):
        self.parent.app.path_to_markdown = "README.md"
        self.parent.app.open_markdown()



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
        pass

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
        # self.configMenu.load_project()
        # self.sidebarMenu.load_project()


    def hide(self):
        self.pack_forget()
