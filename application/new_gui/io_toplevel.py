import customtkinter as ctk
import xml.dom.minidom
from tktooltip import ToolTip
import application.xml_manager as xmlman

class IO_TopLevel_Functions():
    def __init__(self, top_level):
        self.top_level = top_level
    
    def get_all_signal_names(self, mode=None):

        # if mode = None, return all
        # if mode = "in", return inputs only
        # if mode = "out", return outputs only

        port_map = self.top_level.get_io_ports()    
        port_map_signals_names = []

        for port in port_map:

            gpio_name = port[0]   # GPIO Name
            gpio_mode = port[1]   # GPIO Mode (in/out)
            gpio_type = port[2]   # GPIO Type (single bit/bus/array)
            gpio_width = 0

            if mode==None or mode==gpio_mode:    
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

        return port_map_signals_names

class Led_Config_Window(ctk.CTkToplevel):
    def __init__(self, app):
        self.io_functions = IO_TopLevel_Functions(self)

        ctk.CTkToplevel.__init__(self, app.root)
        self.app = app
        self.title("Configure Board IO")
        self.grab_set() # This makes the pop-up the primary window and doesn't allow interaction with main menu
        self.geometry("600x305")
        header_font = ("Segoe UI", 16, "bold") # Title font
        self.resizable(False, False) # Dont let the window be resizable
        
        # Load IO_Config from the XML
        self.app.io_configuration = xmlman.Xml_Manager(self.app.hdlgen_path).read_io_config()

        
        # Need to learn the I/O thats available - What top level signals can we use.
        # LED0: (dropdown) -> dropdown menu will contain all the signals as
        #                                   count[3]
        #                                   count[2]
        #                                   count[1]
        #                                   count[0]
        #                                   TC
        #                                   ceo

        # port_map = self.get_io_ports()    
        # port_map_signals_names = []

        # for port in port_map:

        #     gpio_name = port[0]   # GPIO Name
        #     gpio_mode = port[1]   # GPIO Mode (in/out)
        #     gpio_type = port[2]   # GPIO Type (single bit/bus/array)
        #     gpio_width = 0

        #     if (gpio_type == "single bit"):
        #         gpio_width = 1
        #         port_map_signals_names.append(gpio_name)
            
        #     elif (gpio_type[:3] == "bus"):
        #         # <type>bus(31 downto 0)</type>     ## Example Type Value
        #         substring = gpio_type[4:]           # substring = '31 downto 0)'
        #         words = substring.split()           # words = ['31', 'downto', '0)']
        #         gpio_width = int(words[0]) + 1           # words[0] = 31
            
        #         for i in range(gpio_width):
        #             port_map_signals_names.append(f"{gpio_name}[{i}]")

        # port_map_signals_name = self.io_functions.get_all_signal_names()

        # Right frame
        self.right_frame = ctk.CTkFrame(self, width=200, height=100) # Right frame will contain manual config of signals

        self.r_top_label = ctk.CTkLabel(self.right_frame, width=200, height=30, text="LEDs", corner_radius=0, font=header_font)
        self.r_top_label.grid(row=0, column=0, columnspan=4, pady=5)


        self.led_0_label = ctk.CTkLabel(self.right_frame, text="LED0", width=140)
        self.led_1_label = ctk.CTkLabel(self.right_frame, text="LED1", width=140)
        self.led_2_label = ctk.CTkLabel(self.right_frame, text="LED2", width=140)
        self.led_3_label = ctk.CTkLabel(self.right_frame, text="LED3", width=140)

        self.led_0_label.grid(row=1, column=0, pady=5, padx=5)
        self.led_1_label.grid(row=2, column=0, pady=5, padx=5)
        self.led_2_label.grid(row=3, column=0, pady=5, padx=5)
        self.led_3_label.grid(row=4, column=0, pady=5, sticky="nsew", padx=5)

        self.led_4b_label = ctk.CTkLabel(self.right_frame, text="LED4b", width=140)
        self.led_4g_label = ctk.CTkLabel(self.right_frame, text="LED4g", width=140)
        self.led_4r_label = ctk.CTkLabel(self.right_frame, text="LED4r", width=140)
        self.led_5b_label = ctk.CTkLabel(self.right_frame, text="LED5b", width=140)
        self.led_5g_label = ctk.CTkLabel(self.right_frame, text="LED5g", width=140)
        self.led_5r_label = ctk.CTkLabel(self.right_frame, text="LED5r", width=140)

        self.led_4b_label.grid(row=1, column=2, pady=5, padx=5)
        self.led_4g_label.grid(row=2, column=2, pady=5, padx=5)
        self.led_4r_label.grid(row=3, column=2, pady=5, padx=5)
        self.led_5b_label.grid(row=4, column=2, pady=5, padx=5)
        self.led_5g_label.grid(row=5, column=2, pady=5, padx=5)
        self.led_5r_label.grid(row=6, column=2, pady=5, padx=5)

        # mode_dropdown = ctk.CTkOptionMenu(self.row_2_frame, variable=mode_menu_var, values=self.mode_menu_options, command=on_mode_dropdown, width=150)
        def _on_io_dropdown(args):
            # handle dropdown event
            pass

        dropdown_options = self.io_functions.get_all_signal_names()
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

        self.led_4b_var = ctk.StringVar(value=self.app.io_configuration["led4_b"]) # self.io_configuration["led0"]
        self.led_4b_dropdown = ctk.CTkOptionMenu(self.right_frame, variable=self.led_4b_var, values=dropdown_options, command=_on_io_dropdown)
        self.led_4g_var = ctk.StringVar(value=self.app.io_configuration["led4_g"])
        self.led_4g_dropdown = ctk.CTkOptionMenu(self.right_frame, variable=self.led_4g_var, values=dropdown_options, command=_on_io_dropdown)
        self.led_4r_var = ctk.StringVar(value=self.app.io_configuration["led4_r"])
        self.led_4r_dropdown = ctk.CTkOptionMenu(self.right_frame, variable=self.led_4r_var, values=dropdown_options, command=_on_io_dropdown)

        self.led_5b_var = ctk.StringVar(value=self.app.io_configuration["led5_b"])
        self.led_5b_dropdown = ctk.CTkOptionMenu(self.right_frame, variable=self.led_5b_var, values=dropdown_options, command=_on_io_dropdown)
        self.led_5g_var = ctk.StringVar(value=self.app.io_configuration["led5_g"])
        self.led_5g_dropdown = ctk.CTkOptionMenu(self.right_frame, variable=self.led_5g_var, values=dropdown_options, command=_on_io_dropdown)
        self.led_5r_var = ctk.StringVar(value=self.app.io_configuration["led5_r"])
        self.led_5r_dropdown = ctk.CTkOptionMenu(self.right_frame, variable=self.led_5r_var, values=dropdown_options, command=_on_io_dropdown)

        self.led_4b_dropdown.grid(row=1, column=3, pady=5, padx=5)
        self.led_4g_dropdown.grid(row=2, column=3, pady=5, padx=5)
        self.led_4r_dropdown.grid(row=3, column=3, pady=5, padx=5)
        self.led_5b_dropdown.grid(row=4, column=3, pady=5, padx=5)
        self.led_5g_dropdown.grid(row=5, column=3, pady=5, padx=5)
        self.led_5r_dropdown.grid(row=6, column=3, pady=5, padx=5)


        # Right frame set up
    	# Button handlers
        def _on_save_button():
            # Set the IO config in shared space
            self.app.io_configuration["led0"] = self.led_0_var.get()
            self.app.io_configuration["led1"] = self.led_1_var.get()
            self.app.io_configuration["led2"] = self.led_2_var.get()
            self.app.io_configuration["led3"] = self.led_3_var.get()
            self.app.io_configuration["led4_b"] = self.led_4b_var.get()
            self.app.io_configuration["led4_g"] = self.led_4g_var.get()
            self.app.io_configuration["led4_r"] = self.led_4r_var.get()
            self.app.io_configuration["led5_b"] = self.led_5b_var.get()
            self.app.io_configuration["led5_g"] = self.led_5g_var.get()
            self.app.io_configuration["led5_r"] = self.led_5r_var.get()

            # Save that that file using XML Manager
            xmlmanager = xmlman.Xml_Manager(self.app.hdlgen_path)
            xmlmanager.write_io_config(self.app.io_configuration)

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