import customtkinter as ctk
import xml.dom.minidom
from tktooltip import ToolTip

class Led_Config_Window(ctk.CTkToplevel):
    def __init__(self, app):
        ctk.CTkToplevel.__init__(self, app.root)
        self.app = app
        self.title("Configure Board IO")
        self.grab_set() # This makes the pop-up the primary window and doesn't allow interaction with main menu
        self.geometry("300x230")
        # {'family': 'Segoe UI', 'size': 9, 'weight': 'normal', 'slant': 'roman', 'underline': 0, 'overstrike': 0}
        header_font = ("Segoe UI", 16, "bold") # Title font
        self.resizable(False, False) # Dont let the window be resizable
        
        # Need to learn the I/O thats available - What top level signals can we use.
        # LED0: (dropdown) -> dropdown menu will contain all the signals as
        #                                   count[3]
        #                                   count[2]
        #                                   count[1]
        #                                   count[0]
        #                                   TC
        #                                   ceo

        port_map = self.get_io_ports()    
        port_map_signals_names = []

        # # # # Automatic Mode is Disabled for the Moment - Realistically it just adds too much complexicity for only a few LEDs.
        # # # # Ultimately not very scalable either.

        # Left frame
        # self.left_frame = ctk.CTkFrame(self, width=100, height=100)  # Left frame will contain checkbox for yes/no auto scanning + explaination

        # self.l_top_label = ctk.CTkLabel(self.left_frame, width=200, height=30, text="Auto IO")
        # self.l_top_label.grid(row=0, column=0, pady=5)

        # Left frame set up
        # self.auto_io_checkbox = ctk.CTkCheckBox(self.left_frame, text="Auto Detect IO", width=100)
        # self.auto_io_checkbox.grid(row=1, column=0)
        # text="In automatic mode, signals tagged with an IO related suffix (eg '_led') will be assigned to I/O. The suffix mapping is as follows:\n - _led: Any available port\n- _ledx: LEDx only (x=0,1,2,3)"
        # self.auto_io_label = ctk.CTkLabel(self.left_frame, wraplength=100, width=100, anchor="nw", text="\nExplaination of how Auto mode works", height=130, corner_radius=0)
        # self.auto_io_label.grid(row=2, column=0)

        for port in port_map:

            gpio_name = port[0]   # GPIO Name
            gpio_mode = port[1]   # GPIO Mode (in/out)
            gpio_type = port[2]   # GPIO Type (single bit/bus/array)
            gpio_width = 0

            if (gpio_type == "single bit"):
                gpio_width = 1
                port_map_signals_names.append(gpio_name)
            
            elif (gpio_type[:3] == "bus"):
                # <type>bus(31 downto 0)</type>     ## Example Type Value
                substring = gpio_type[4:]           # substring = '31 downto 0)'
                words = substring.split()           # words = ['31', 'downto', '0)']
                gpio_width = int(words[0]) + 1           # words[0] = 31
            
                for i in range(gpio_width):
                    port_map_signals_names.append(f"{gpio_name}[{i}]")


        # Right frame
        self.right_frame = ctk.CTkFrame(self, width=200, height=100) # Right frame will contain manual config of signals

        self.r_top_label = ctk.CTkLabel(self.right_frame, width=200, height=30, text="Configure Board I/O Connections", corner_radius=0, font=header_font)
        self.r_top_label.grid(row=0, column=0, columnspan=2, pady=5)


        self.led_0_label = ctk.CTkLabel(self.right_frame, text="LED0", width=140)
        self.led_1_label = ctk.CTkLabel(self.right_frame, text="LED1", width=140)
        self.led_2_label = ctk.CTkLabel(self.right_frame, text="LED2", width=140)
        self.led_3_label = ctk.CTkLabel(self.right_frame, text="LED3", width=140)

        self.led_0_label.grid(row=1, column=0, pady=5, padx=5)
        self.led_1_label.grid(row=2, column=0, pady=5, padx=5)
        self.led_2_label.grid(row=3, column=0, pady=5, padx=5)
        self.led_3_label.grid(row=4, column=0, pady=5, sticky="nsew", padx=5)

        # mode_dropdown = ctk.CTkOptionMenu(self.row_2_frame, variable=mode_menu_var, values=self.mode_menu_options, command=on_mode_dropdown, width=150)
        def _on_io_dropdown(args):
            # handle dropdown event
            pass

        dropdown_options = port_map_signals_names
        dropdown_options.insert(0, "None")

        self.led_0_var = ctk.StringVar(value=self.app.io_configuration["led0"]) # self.io_configuration["led0"]
        self.led_0_dropdown = ctk.CTkOptionMenu(self.right_frame, variable=self.led_0_var, values=dropdown_options, command=_on_io_dropdown)

        self.led_1_var = ctk.StringVar(value=self.app.io_configuration["led1"])
        self.led_1_dropdown = ctk.CTkOptionMenu(self.right_frame, variable=self.led_1_var, values=dropdown_options, command=_on_io_dropdown)

        self.led_2_var = ctk.StringVar(value=self.app.io_configuration["led2"])
        self.led_2_dropdown = ctk.CTkOptionMenu(self.right_frame, variable=self.led_2_var, values=dropdown_options, command=_on_io_dropdown)

        self.led_3_var = ctk.StringVar(value=self.app.io_configuration["led3"])
        self.led_3_dropdown = ctk.CTkOptionMenu(self.right_frame, variable=self.led_3_var, values=dropdown_options, command=_on_io_dropdown)

        self.led_0_dropdown.grid(row=1, column=1, pady=5, padx=5)
        self.led_1_dropdown.grid(row=2, column=1, pady=5, padx=5)
        self.led_2_dropdown.grid(row=3, column=1, pady=5, padx=5)
        self.led_3_dropdown.grid(row=4, column=1, pady=5, padx=5)


        # Right frame set up
    	# Button handlers
        def _on_save_button():
            # Set the IO config in shared space
            self.app.io_configuration["led0"] = self.led_0_var.get()
            self.app.io_configuration["led1"] = self.led_1_var.get()
            self.app.io_configuration["led2"] = self.led_2_var.get()
            self.app.io_configuration["led3"] = self.led_3_var.get()
            # Close Window
            self.destroy()

        def _on_cancel_button():
            # We don't care about setting any values
            # If cancel pressed, simply close the menu.
            self.destroy()

        self.button_frame = ctk.CTkFrame(self, width=300, height=50) # Button frame will remain the same as Dialog window

        # Button placement
        self.button_frame = ctk.CTkFrame(self, width=300, height=50)
        self.save_button = ctk.CTkButton(self.button_frame, text="Save", command=_on_save_button)
        self.save_button.grid(row=0, column=0, pady=5, padx=5)
        self.cancel_button = ctk.CTkButton(self.button_frame, text="Cancel", command=_on_cancel_button)
        self.cancel_button.grid(row=0, column=1, pady=5, padx=5)

        # self.left_frame.grid(column=0, row=0)
        self.right_frame.grid(column=0, row=0)
        self.button_frame.grid(column=0, row=1) # , columnspan=2

    def get_io_ports(self):
        hdlgen = xml.dom.minidom.parse(self.app.hdlgen_path)
        root = hdlgen.documentElement

        # hdlDesign - entityIOPorts
        hdlDesign = root.getElementsByTagName("hdlDesign")[0]
        entityIOPorts = hdlDesign.getElementsByTagName("entityIOPorts")[0]
        signals = entityIOPorts.getElementsByTagName("signal")

        all_ports = []
        for sig in signals:
            signame = sig.getElementsByTagName("name")[0]
            mode = sig.getElementsByTagName("mode")[0]
            type = sig.getElementsByTagName("type")[0]
            desc = sig.getElementsByTagName("description")[0]
            all_ports.append(
                [signame.firstChild.data, mode.firstChild.data, type.firstChild.data, desc.firstChild.data]
            )
    
        return all_ports