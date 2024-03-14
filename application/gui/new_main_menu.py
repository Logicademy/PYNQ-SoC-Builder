import customtkinter as ctk
import os
import time


ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class ConfigMenu(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        window_height = parent.app.get_window_height()
        window_width = parent.app.get_window_width()

        self.configure(width=window_width-10, height=window_height/2)



class Menu(ctk.CTkScrollableFrame):
    def __init__(self, parent):
        super().__init__(parent)

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

        self.build_button = ctk.CTkButton(self, text="Remote FPGA", width=225, height=40, font=button_font)
        self.build_button.grid(row=3, column=0, pady=10)
        self.build_button = ctk.CTkButton(self, text="Local FPGA", width=225, height=40, font=button_font)
        self.build_button.grid(row=4, column=0, pady=10)
        
        self.build_button = ctk.CTkButton(
            self,
            text="Close Project", 
            width=225, 
            height=40, 
            font=button_font,
            fg_color=red_fg_clr,
            hover_color=red_hv_clr        
        )
        self.build_button.grid(row=5, column=0, pady=10)

    def resize(self, event):
        print(event)
        print("We are configured")
        self.configure(height=(event.height/2))

class ConfigTabs(ctk.CTkTabview):
    def __init__(self, parent):
        super().__init__(parent)

        self.configure(width=1200-290, height=(800/2))
        
        # Set size of tabs
        custom_font = ('abc', 20)

        dummy_label = ctk.CTkLabel(self, text="dummy")
        default_font = dummy_label.cget("font")

        tab_font = (default_font, 20, "bold")

        self._segmented_button.configure(font=tab_font)

        # Create tabs
        self.add("Project Config")
        self.add("I/O Config")
        self.add("App Preferences")

        # Justify to the LEFT
        self.configure(anchor='nw')

        # Add widgets to each tab?
        self.label = ctk.CTkLabel(master=self.tab("Project Config"), text="Project Config Area")
        self.label.pack()

        self.label = ctk.CTkLabel(master=self.tab("I/O Config"), text="I/O Config Area")
        self.label.pack()

        self.label = ctk.CTkLabel(master=self.tab("App Preferences"), text="App Preferences Area")
        self.label.pack()

class LogTabs(ctk.CTkTabview):
    def __init__(self, parent):
        super().__init__(parent)

        self.configure(width=1180, height=(800/2)-20)
        
        # Set size of tabs
        custom_font = ('abc', 20)
        self._segmented_button.configure(font=custom_font)

        # Create tabs
        self.add("Log")
        self.add("Synthesis Log")
        self.add("Implementation Log")

        # Justify to the LEFT
        self.configure(anchor='nw')

        # Add widgets to each tab?
        self.label = ctk.CTkLabel(master=self.tab("Log"), text="Main Logging Area")
        self.label.pack()

        self.label = ctk.CTkLabel(master=self.tab("Synthesis Log"), text="Synthesis Logging Area")
        self.label.pack()

        self.label = ctk.CTkLabel(master=self.tab("Implementation Log"), text="Implementation Logging Area")
        self.label.pack()

class ConfigMenu(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        window_height = parent.app.get_window_height()
        window_width = parent.app.get_window_width()

        self.configure(width=window_width-290, height=window_height/2)


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

        # self.label = ctk.CTkLabel(self, text="Project Config Area", font=title_font, width=250)
        # self.label.grid(row=0, column=0, pady=10)

        # self.build_button = ctk.CTkButton(
        #     self, 
        #     text="Config the project", 
        #     width=225, 
        #     height=40, 
        #     font=button_font,
        #     fg_color=green_fg_clr,
        #     hover_color=green_hv_clr
        # )
        # self.build_button.grid(row=1, column=0, pady=10)

        self.tab_view = ConfigTabs(self)
        self.tab_view.grid(row=0, column=0, padx=10, pady=5)


class LogMenu(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        window_height = parent.app.get_window_height()
        window_width = parent.app.get_window_width()

        self.configure(width=window_width, height=window_height/2)


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

        # self.label = ctk.CTkLabel(self, text="Project Config Area", font=title_font, width=250)
        # self.label.grid(row=0, column=0, pady=10)

        # self.build_button = ctk.CTkButton(
        #     self, 
        #     text="Config the project", 
        #     width=225, 
        #     height=40, 
        #     font=button_font,
        #     fg_color=green_fg_clr,
        #     hover_color=green_hv_clr
        # )
        # self.build_button.grid(row=1, column=0, pady=10)

        self.tab_view = LogTabs(self)
        self.tab_view.grid(row=0, column=0, padx=10, pady=5)



class MainPage(ctk.CTkFrame):
    def __init__(self, app):
        ctk.CTkFrame.__init__(self, app.root)
        self.app = app

        self.configure(
            height=self.app.get_window_height(),
            width=self.app.get_window_width()
        )

        # def resize(event):
        #     print(event)
        #     self.configure(width=event.width, height=event.height)



        self.columnconfigure(1, weight=1)

        self.menu = Menu(self)
        self.menu.grid(row=0, column=0, sticky='news')

        self.configMenu = ConfigMenu(self)
        self.configMenu.grid(row=0, column=1, sticky='news')

        self.logMenu = LogMenu(self)
        self.logMenu.grid(row=1, column=0, sticky='news', columnspan=2)
        # print(self.app.get_window_dimensions()[0])
        # self.configure(width=self.app.get_window_dimensions()[0], height=self.app.get_window_dimensions()[1])

        # menu = Menu(self)           # Instanciate Menu Frame and pack it NW
        # menu.pack(anchor='nw')

        # Bind the resize event to the frame
        self.bind("<Configure>", self.menu.resize)


    def show(self):
        self.pack(fill="both", expand=True)
        self.pack_propagate(False)  # Prevent frame from resizing to fit its contents 
    
    def hide(self):
        self.pack_forget()














class Application:

    def __init__(self, root):

        # Set root and title
        self.root = root
        self.root.title("PYNQ SoC Builder")
        self.root.geometry("1200x800")

        self.root.minsize(800, 500)
        # self.root.resizable(False, False) # Dont let the window be resizable
        # self.root.protocol("WM_DELETE_WINDOW", self.on_close) # Set function to handle close

        self.page1 = MainPage(self)
        # self.page2 = etc(self)


        self.show_page(self.page1)

    def get_window_height(self):
        # Wait for the window to be displayed and its size to be finalized
        self.root.update_idletasks()
        self.root.update()
        # Return geometry
        return self.root.winfo_height()
    
    def get_window_width(self):
        # Wait for the window to be displayed and its size to be finalized
        self.root.update_idletasks()
        self.root.update()
        # Return geometry
        return self.root.winfo_width()

    def show_page(self, page):
        # Hide all existing pages
        # Possible we should make this iterate thru all pages to hide (more dynamic)
        # Should be ok for this small application
        self.page1.hide()
        # self.page2.hide()
        # self.page3.hide()
        page.show() # Show requested page.

if __name__ == "__main__":
    root = ctk.CTk()
    app = Application(root)
    root.mainloop()