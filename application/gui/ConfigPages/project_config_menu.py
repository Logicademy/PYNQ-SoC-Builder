import customtkinter as ctk

class ConfigTabView(ctk.CTkTabview):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        window_height = parent.parent.app.get_window_height()
        window_width = parent.parent.app.get_window_width()

        self.configure(width=window_width-290, height=(window_height/2))
        
        # Set size of tabs
        dummy_label = ctk.CTkLabel(self, text="dummy")
        default_font = dummy_label.cget("font")

        tab_font = (default_font, 20)
        text_font = (default_font, 20)
        bold_text_font = (default_font, 24, 'bold')


        self._segmented_button.configure(font=tab_font)

        # Create tabs
        self.add("Project Config")
        self.add("I/O Config")
        self.add("App Preferences")

        # Justify to the LEFT
        self.configure(anchor='nw')

        # Add widgets to each tab?
        # self.label = ctk.CTkLabel(master=self.tab("Project Config"), text="Project Config Area")
        # self.label.pack()

        self.label = ctk.CTkLabel(master=self.tab("I/O Config"), text="I/O Config Area")
        self.label.pack()

        self.label = ctk.CTkLabel(master=self.tab("App Preferences"), text="App Preferences Area")
        self.label.pack()

        ######## RESIZING NOTES
        # 960 is minimum for 2 column (text and Vivado Settings)
        # 1280 is minimum for 3 columns
        # 1560 is minimum for 4 columns

        # self.label = ctk.CTkLabel(master=self.tab("Project Config"), text="Vivado Settings")
        # self.label.pack()
        self.configure(width=window_width-290, height=(window_height/2))

        self.project_config_scrollable = ctk.CTkScrollableFrame(self.tab("Project Config"), width=window_width-310, height=(window_height/2)-80)
        
        self.project_config_scrollable._scrollbar.configure(height=0)
        
        # self.project_config_scrollable.pack_propagate(0)
        self.project_config_scrollable.pack()

        self.RHS_switch_frame = ctk.CTkFrame(self.project_config_scrollable)
        self.LHS_explaination_frame = ctk.CTkFrame(self.RHS_switch_frame, width=500)
        self.LHS_explaination_frame.grid(row=0, column=0, rowspan=100, padx=5, sticky="news")

        self.switch_var0 = ctk.StringVar(value="on")
    
        # Vivado Settings
        self.vivado_settings_lbl = ctk.CTkLabel(self.RHS_switch_frame, text="Vivado Settings", font=bold_text_font)
        self.vivado_settings_lbl.grid(row=0, column=1, padx=5, pady=5)

        self.open_viv_sw = ctk.CTkSwitch(self.RHS_switch_frame, text="Open Vivado GUI", 
                                        variable=self.switch_var0, onvalue="on", offvalue="off", font=text_font)
        self.open_viv_sw.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        self.keep_viv_open_sw = ctk.CTkSwitch(self.RHS_switch_frame, text="Keep Vivado Open", 
                                        variable=self.switch_var0, onvalue="on", offvalue="off", font=text_font)
        self.keep_viv_open_sw.grid(row=2, column=1, padx=5, pady=5, sticky="w")
    
        self.always_regen_bd_sw = ctk.CTkSwitch(self.RHS_switch_frame, text="Always Regenerate Block Design", 
                                        variable=self.switch_var0, onvalue="on", offvalue="off", font=text_font)
        self.always_regen_bd_sw.grid(row=3, column=1, padx=5, pady=5, sticky="w")

    


        # Jupyter Notebook Settings
        self.jupyter_settings_lbl = ctk.CTkLabel(self.RHS_switch_frame, text="Jupyter Notebook Settings", font=bold_text_font)
        self.jupyter_settings_lbl.grid(row=0, column=2, padx=5, pady=5)

        self.gen_when_build_sw = ctk.CTkSwitch(self.RHS_switch_frame, text="Generate when Building", 
                                        variable=self.switch_var0, onvalue="on", offvalue="off", font=text_font)
        self.gen_when_build_sw.grid(row=1, column=2, padx=5, pady=5, sticky="w")
        
        self.gen_tst_sw = ctk.CTkSwitch(self.RHS_switch_frame, text="Generate using Testplan", 
                                        variable=self.switch_var0, onvalue="on", offvalue="off", font=text_font)
        self.gen_tst_sw.grid(row=2, column=2, padx=5, pady=5, sticky="w")

        # PYNQ Board Settings
        self.pynq_board_settings_lbl = ctk.CTkLabel(self.RHS_switch_frame, text="PYNQ Board Settings", font=bold_text_font)
        self.pynq_board_settings_lbl.grid(row=0, column=3, padx=5, pady=5)

        self.gen_io_sw = ctk.CTkSwitch(self.RHS_switch_frame, text="Generate I/O Connections", 
                                        variable=self.switch_var0, onvalue="on", offvalue="off", font=text_font)
        self.gen_io_sw.grid(row=1, column=3, padx=5, pady=5, sticky="w")


        self.RHS_switch_frame.grid()

    def resize(self, event):
        if event.width > 1760:
            # Pack as normal.
            # Vivado Settings
            self.vivado_settings_lbl.grid(row=0, column=1, padx=5, pady=5)
            self.open_viv_sw.grid(row=1, column=1, padx=5, pady=5, sticky="w")
            self.keep_viv_open_sw.grid(row=2, column=1, padx=5, pady=5, sticky="w")
            self.always_regen_bd_sw.grid(row=3, column=1, padx=5, pady=5, sticky="w")
            # Jupyter Notebook Settings
            self.jupyter_settings_lbl.grid(row=0, column=2, padx=5, pady=5)
            self.gen_when_build_sw.grid(row=1, column=2, padx=5, pady=5, sticky="w")
            self.gen_tst_sw.grid(row=2, column=2, padx=5, pady=5, sticky="w")
            # PYNQ Board Settings
            self.pynq_board_settings_lbl.grid(row=0, column=3, padx=5, pady=5)
            self.gen_io_sw.grid(row=1, column=3, padx=5, pady=5, sticky="w")        
        elif event.width > 1480:
            # Vivado Settings
            self.vivado_settings_lbl.grid(row=0, column=1, padx=5, pady=5)
            self.open_viv_sw.grid(row=1, column=1, padx=5, pady=5, sticky="w")
            self.keep_viv_open_sw.grid(row=2, column=1, padx=5, pady=5, sticky="w")
            self.always_regen_bd_sw.grid(row=3, column=1, padx=5, pady=5, sticky="w")
            # Jupyter Notebook Settings
            self.jupyter_settings_lbl.grid(row=0, column=2, padx=5, pady=5)
            self.gen_when_build_sw.grid(row=1, column=2, padx=5, pady=5, sticky="w")
            self.gen_tst_sw.grid(row=2, column=2, padx=5, pady=5, sticky="w")
            # PYNQ Board Settings
            self.pynq_board_settings_lbl.grid(row=4, column=1, padx=5, pady=5)
            self.gen_io_sw.grid(row=5, column=1, padx=5, pady=5, sticky="w")     
        elif event.width > 1160:
            # Vivado Settings
            self.vivado_settings_lbl.grid(row=0, column=1, padx=5, pady=5)
            self.open_viv_sw.grid(row=1, column=1, padx=5, pady=5, sticky="w")
            self.keep_viv_open_sw.grid(row=2, column=1, padx=5, pady=5, sticky="w")
            self.always_regen_bd_sw.grid(row=3, column=1, padx=5, pady=5, sticky="w")
            # Jupyter Notebook Settings
            self.jupyter_settings_lbl.grid(row=4, column=1, padx=5, pady=5)
            self.gen_when_build_sw.grid(row=5, column=1, padx=5, pady=5, sticky="w")
            self.gen_tst_sw.grid(row=6, column=1, padx=5, pady=5, sticky="w")
            # PYNQ Board Settings
            self.pynq_board_settings_lbl.grid(row=7, column=1, padx=5, pady=5)
            self.gen_io_sw.grid(row=8, column=1, padx=5, pady=5, sticky="w")
        else:  
            # Vivado Settings
            self.vivado_settings_lbl.grid(row=101, column=0, padx=5, pady=5)
            self.open_viv_sw.grid(row=102, column=0, padx=5, pady=5, sticky="w")
            self.keep_viv_open_sw.grid(row=103, column=0, padx=5, pady=5, sticky="w")
            self.always_regen_bd_sw.grid(row=104, column=0, padx=5, pady=5, sticky="w")
            # Jupyter Notebook Settings
            self.jupyter_settings_lbl.grid(row=105, column=0, padx=5, pady=5)
            self.gen_when_build_sw.grid(row=106, column=0, padx=5, pady=5, sticky="w")
            self.gen_tst_sw.grid(row=107, column=0, padx=5, pady=5, sticky="w")
            # PYNQ Board Settings
            self.pynq_board_settings_lbl.grid(row=108, column=0, padx=5, pady=5)
            self.gen_io_sw.grid(row=109, column=0, padx=5, pady=5, sticky="w")

class ConfigMenu(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        window_height = parent.app.get_window_height()
        window_width = parent.app.get_window_width()

        self.configure(width=window_width-10, height=window_height/2)

