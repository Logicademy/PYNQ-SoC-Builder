import customtkinter as ctk

class ConfigTabView(ctk.CTkTabview):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        window_height = parent.parent.app.get_window_height()
        window_width = parent.parent.app.get_window_width()

        # self.configure(width=window_width-290, height=(window_height/2))
        
        # Set size of tabs
        dummy_label = ctk.CTkLabel(self, text="dummy")
        default_font = dummy_label.cget("font")

        tab_font = (default_font, 20)
        text_font = (default_font, 20)
        bold_text_font = (default_font, 24, 'bold')


        self._segmented_button.configure(font=tab_font)

        # Create tabs
        self.add("Build Status")
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

        self.buildstatuspage = BuildStatusTab(self.tab("Build Status"))
        self.buildstatuspage.pack()


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
    
        # Vivado Settings
        self.vivado_settings_var = ctk.StringVar(value="on")
        self.vivado_settings_lbl = ctk.CTkLabel(self.RHS_switch_frame, text="Vivado Settings", font=bold_text_font)
        # self.vivado_settings_lbl.grid(row=0, column=1, padx=5, pady=5)    # No need to pack these because the resize() call handles it.

        self.open_viv_var = ctk.StringVar(value="on")
        self.open_viv_sw = ctk.CTkSwitch(self.RHS_switch_frame, text="Open Vivado GUI", 
                                        variable=self.open_viv_var, onvalue="on", offvalue="off", font=text_font)
        # self.open_viv_sw.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        self.keep_viv_open_var = ctk.StringVar(value="on")
        self.keep_viv_open_sw = ctk.CTkSwitch(self.RHS_switch_frame, text="Keep Vivado Open", 
                                        variable=self.keep_viv_open_var, onvalue="on", offvalue="off", font=text_font)
        # self.keep_viv_open_sw.grid(row=2, column=1, padx=5, pady=5, sticky="w")
    
        self.always_regen_bd_var = ctk.StringVar(value="on")
        self.always_regen_bd_sw = ctk.CTkSwitch(self.RHS_switch_frame, text="Always Regenerate Block Design", 
                                        variable=self.always_regen_bd_var, onvalue="on", offvalue="off", font=text_font)
        # self.always_regen_bd_sw.grid(row=3, column=1, padx=5, pady=5, sticky="w")



        # Jupyter Notebook Settings
        self.jupyter_settings_lbl = ctk.CTkLabel(self.RHS_switch_frame, text="Jupyter Notebook Settings", font=bold_text_font)
        # self.jupyter_settings_lbl.grid(row=0, column=2, padx=5, pady=5)

        self.gen_when_build_var = ctk.StringVar(value="on")
        self.gen_when_build_sw = ctk.CTkSwitch(self.RHS_switch_frame, text="Generate when Building", 
                                        variable=self.gen_when_build_var, onvalue="on", offvalue="off", font=text_font)
        # self.gen_when_build_sw.grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.gen_tst_var = ctk.StringVar(value="on")
        self.gen_tst_sw = ctk.CTkSwitch(self.RHS_switch_frame, text="Generate using Testplan", 
                                        variable=self.gen_tst_var, onvalue="on", offvalue="off", font=text_font)
        # self.gen_tst_sw.grid(row=2, column=2, padx=5, pady=5, sticky="w")

        # PYNQ Board Settings
        self.pynq_board_settings_lbl = ctk.CTkLabel(self.RHS_switch_frame, text="PYNQ Board Settings", font=bold_text_font)
        # self.pynq_board_settings_lbl.grid(row=0, column=3, padx=5, pady=5)

        self.gen_io_var = ctk.StringVar(value="on")
        self.gen_io_sw = ctk.CTkSwitch(self.RHS_switch_frame, text="Make Connections to Board I/O", 
                                        variable=self.gen_io_var, onvalue="on", offvalue="off", font=text_font)
        # self.gen_io_sw.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        self.RHS_switch_frame.grid()

        # Set tab
        self.set("Project Config")

    def resize(self, event):
        # Default
        self.buildstatuspage.resize(event)
        # self.LHS_explaination_frame.configure(width=(event.width-310)/2)
        self.LHS_explaination_frame.configure(width=(event.width/2)-280)
        self.LHS_explaination_frame.grid(row=0, column=0, rowspan=100, padx=5, sticky="news")

        if (event.width-310)/2 > 685:
            # Vivado Settings
            self.vivado_settings_lbl.grid(row=0, column=1, padx=5, pady=5, sticky="news")
            self.open_viv_sw.grid(row=1, column=1, padx=5, pady=5, sticky="w")
            self.keep_viv_open_sw.grid(row=2, column=1, padx=5, pady=5, sticky="w")
            self.always_regen_bd_sw.grid(row=3, column=1, padx=5, pady=5, sticky="w")
            # Jupyter Notebook Settings
            self.jupyter_settings_lbl.grid(row=0, column=2, padx=5, pady=5, sticky="news")
            self.gen_when_build_sw.grid(row=1, column=2, padx=5, pady=5, sticky="w")
            self.gen_tst_sw.grid(row=2, column=2, padx=5, pady=5, sticky="w")
            # PYNQ Board Settings
            self.pynq_board_settings_lbl.grid(row=4, column=1, padx=5, pady=5, sticky="news")
            self.gen_io_sw.grid(row=5, column=1, padx=5, pady=5, sticky="w")     
        elif (event.width-310)/2 > 425:
            # Vivado Settings
            self.vivado_settings_lbl.grid(row=0, column=1, padx=5, pady=5, sticky="news")
            self.open_viv_sw.grid(row=1, column=1, padx=5, pady=5, sticky="w")
            self.keep_viv_open_sw.grid(row=2, column=1, padx=5, pady=5, sticky="w")
            self.always_regen_bd_sw.grid(row=3, column=1, padx=5, pady=5, sticky="w")
            # Jupyter Notebook Settings
            self.jupyter_settings_lbl.grid(row=4, column=1, padx=5, pady=5, sticky="news")
            self.gen_when_build_sw.grid(row=5, column=1, padx=5, pady=5, sticky="w")
            self.gen_tst_sw.grid(row=6, column=1, padx=5, pady=5, sticky="w")
            # PYNQ Board Settings
            self.pynq_board_settings_lbl.grid(row=7, column=1, padx=5, pady=5, sticky="news")
            self.gen_io_sw.grid(row=8, column=1, padx=5, pady=5, sticky="w")
        else:
            # In this event, we just wanna have everything on top and make it get as wide as it needs.
            self.LHS_explaination_frame.configure(width=(event.width-330))
            self.LHS_explaination_frame.grid(row=110, column=0, padx=5, pady=5, sticky="news")

            # Vivado Settings
            self.vivado_settings_lbl.grid(row=101, column=0, padx=5, pady=5, sticky="news")
            self.open_viv_sw.grid(row=102, column=0, padx=5, pady=5, sticky="w")
            self.keep_viv_open_sw.grid(row=103, column=0, padx=5, pady=5, sticky="w")
            self.always_regen_bd_sw.grid(row=104, column=0, padx=5, pady=5, sticky="w")
            # Jupyter Notebook Settings
            self.jupyter_settings_lbl.grid(row=105, column=0, padx=5, pady=5, sticky="news")
            self.gen_when_build_sw.grid(row=106, column=0, padx=5, pady=5, sticky="w")
            self.gen_tst_sw.grid(row=107, column=0, padx=5, pady=5, sticky="w")
            # PYNQ Board Settings
            self.pynq_board_settings_lbl.grid(row=108, column=0, padx=5, pady=5, sticky="news")
            self.gen_io_sw.grid(row=109, column=0, padx=5, pady=5, sticky="w")

class BuildStatusTab(ctk.CTkScrollableFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self._scrollbar.configure(height=0)

        dummy_label = ctk.CTkLabel(self, text="dummy")
        default_font = dummy_label.cget("font")

        est_font = (default_font, 16)
        time_font = (default_font, 16)
        name_font = (default_font, 20, 'bold')
        sub_name_font = (default_font, 16)
        
        ### Generate Tcl
        self.gen_tcl_frame = ctk.CTkFrame(self)
        self.gen_tcl_est_lbl = ctk.CTkLabel(self.gen_tcl_frame, text="Est. <5 seconds", font=est_font, width=160)
        self.gen_tcl_time_lbl = ctk.CTkLabel(self.gen_tcl_frame, text="00:00", font=time_font, width=50)
        self.gen_tcl_statusbar = ctk.CTkProgressBar(self.gen_tcl_frame, width=50, mode='indeterminate', determinate_speed=1)
        self.gen_tcl_name_lbl = ctk.CTkLabel(self.gen_tcl_frame, text="Generate Tcl Script for Vivado", font=name_font)
        self.gen_tcl_est_lbl.grid(row=0, column=0, padx=5, pady=5)
        self.gen_tcl_time_lbl.grid(row=0, column=1, padx=5, pady=5)
        self.gen_tcl_statusbar.grid(row=0, column=2, padx=5, pady=5)
        self.gen_tcl_name_lbl.grid(row=0, column=3, padx=5, pady=5)

        ### Run Vivado
        self.run_viv_frame = ctk.CTkFrame(self)
        self.run_viv_est_lbl = ctk.CTkLabel(self.run_viv_frame, text="Est. ~10 minutes", font=est_font, width=160)
        self.run_viv_time_lbl = ctk.CTkLabel(self.run_viv_frame, text="00:00", font=time_font, width=50)
        self.run_viv_statusbar = ctk.CTkProgressBar(self.run_viv_frame, width=50, mode='indeterminate', determinate_speed=1)
        self.run_viv_name_lbl = ctk.CTkLabel(self.run_viv_frame, text="Execute Vivado", font=name_font)
        self.run_viv_est_lbl.grid(row=0, padx=5, pady=5, column=0)
        self.run_viv_time_lbl.grid(row=0, padx=5, pady=5, column=1)
        self.run_viv_statusbar.grid(row=0, padx=5, pady=5, column=2)
        self.run_viv_name_lbl.grid(row=0, padx=5, pady=5, column=3)

        # Sub Viv
        self.run_viv0_frame = ctk.CTkFrame(self)
        self.run_viv0_est_lbl = ctk.CTkLabel(self.run_viv0_frame, text="", font=est_font, width=200)
        self.run_viv0_time_lbl = ctk.CTkLabel(self.run_viv0_frame, text="00:00", font=time_font, width=50)
        self.run_viv0_statusbar = ctk.CTkProgressBar(self.run_viv0_frame, width=50, mode='indeterminate', determinate_speed=1)
        self.run_viv0_name_lbl = ctk.CTkLabel(self.run_viv0_frame, text="Open Project", font=sub_name_font)
        self.run_viv0_est_lbl.grid(row=0, padx=5, pady=5, column=0)
        self.run_viv0_time_lbl.grid(row=0, padx=5, pady=5, column=1)
        self.run_viv0_statusbar.grid(row=0, padx=5, pady=5, column=2)
        self.run_viv0_name_lbl.grid(row=0, padx=5, pady=5, column=3)
        # Sub Viv
        self.run_viv1_frame = ctk.CTkFrame(self)
        self.run_viv1_est_lbl = ctk.CTkLabel(self.run_viv1_frame, text="", font=est_font, width=200)
        self.run_viv1_time_lbl = ctk.CTkLabel(self.run_viv1_frame, text="00:00", font=time_font, width=50)
        self.run_viv1_statusbar = ctk.CTkProgressBar(self.run_viv1_frame, width=50, mode='indeterminate', determinate_speed=1)
        self.run_viv1_name_lbl = ctk.CTkLabel(self.run_viv1_frame, text="Build Block Design", font=sub_name_font)
        self.run_viv1_est_lbl.grid(row=0, padx=5, pady=5, column=0)
        self.run_viv1_time_lbl.grid(row=0, padx=5, pady=5, column=1)
        self.run_viv1_statusbar.grid(row=0, padx=5, pady=5, column=2)
        self.run_viv1_name_lbl.grid(row=0, padx=5, pady=5, column=3)
        # Sub Viv
        self.run_viv2_frame = ctk.CTkFrame(self)
        self.run_viv2_est_lbl = ctk.CTkLabel(self.run_viv2_frame, text="", font=est_font, width=200)
        self.run_viv2_time_lbl = ctk.CTkLabel(self.run_viv2_frame, text="00:00", font=time_font, width=50)
        self.run_viv2_statusbar = ctk.CTkProgressBar(self.run_viv2_frame, width=50, mode='indeterminate', determinate_speed=1)
        self.run_viv2_name_lbl = ctk.CTkLabel(self.run_viv2_frame, text="Run Synthesis", font=sub_name_font)
        self.run_viv2_est_lbl.grid(row=0, padx=5, pady=5, column=0)
        self.run_viv2_time_lbl.grid(row=0, padx=5, pady=5, column=1)
        self.run_viv2_statusbar.grid(row=0, padx=5, pady=5, column=2)
        self.run_viv2_name_lbl.grid(row=0, padx=5, pady=5, column=3)
        # Sub Viv     
        self.run_viv3_frame = ctk.CTkFrame(self)    
        self.run_viv3_est_lbl = ctk.CTkLabel(self.run_viv3_frame, text="", font=est_font, width=200)
        self.run_viv3_time_lbl = ctk.CTkLabel(self.run_viv3_frame, text="00:00", font=time_font, width=50)
        self.run_viv3_statusbar = ctk.CTkProgressBar(self.run_viv3_frame, width=50, mode='indeterminate', determinate_speed=1)
        self.run_viv3_name_lbl = ctk.CTkLabel(self.run_viv3_frame, text="Run Implementation", font=sub_name_font)
        self.run_viv3_est_lbl.grid(row=0, padx=5, pady=5, column=0)
        self.run_viv3_time_lbl.grid(row=0, padx=5, pady=5, column=1)
        self.run_viv3_statusbar.grid(row=0, padx=5, pady=5, column=2)
        self.run_viv3_name_lbl.grid(row=0, padx=5, pady=5, column=3)
        # Sub Viv      
        self.run_viv4_frame = ctk.CTkFrame(self)
        self.run_viv4_est_lbl = ctk.CTkLabel(self.run_viv4_frame, text="", font=est_font, width=200)
        self.run_viv4_time_lbl = ctk.CTkLabel(self.run_viv4_frame, text="00:00", font=time_font, width=50)
        self.run_viv4_statusbar = ctk.CTkProgressBar(self.run_viv4_frame, width=50, mode='indeterminate', determinate_speed=1)
        self.run_viv4_name_lbl = ctk.CTkLabel(self.run_viv4_frame, text="Generate Bitstream", font=sub_name_font)
        self.run_viv4_est_lbl.grid(row=0, padx=5, pady=5, column=0)
        self.run_viv4_time_lbl.grid(row=0, padx=5, pady=5, column=1)
        self.run_viv4_statusbar.grid(row=0, padx=5, pady=5, column=2)
        self.run_viv4_name_lbl.grid(row=0, padx=5, pady=5, column=3)
        ### Gen JNB
        self.gen_jnb_frame = ctk.CTkFrame(self)
        self.gen_jnb_est_lbl = ctk.CTkLabel(self.gen_jnb_frame, text="Est. <5 seconds", font=est_font, width=160)
        self.gen_jnb_time_lbl = ctk.CTkLabel(self.gen_jnb_frame, text="00:00", font=time_font, width=50)
        self.gen_jnb_statusbar = ctk.CTkProgressBar(self.gen_jnb_frame, width=50, mode='indeterminate', determinate_speed=1)
        self.gen_jnb_name_lbl = ctk.CTkLabel(self.gen_jnb_frame, text="Generate Jupyter Notebook", font=name_font)
        self.gen_jnb_est_lbl.grid(row=0, padx=5, pady=5, column=0)
        self.gen_jnb_time_lbl.grid(row=0, padx=5, pady=5, column=1)
        self.gen_jnb_statusbar.grid(row=0, padx=5, pady=5, column=2)
        self.gen_jnb_name_lbl.grid(row=0, padx=5, pady=5, column=3)
        ### Cpy Out
        self.cpy_dir_frame = ctk.CTkFrame(self)
        self.cpy_dir_est_lbl = ctk.CTkLabel(self.cpy_dir_frame, text="Est. <1 seconds", font=est_font, width=160)
        self.cpy_dir_time_lbl = ctk.CTkLabel(self.cpy_dir_frame, text="00:00", font=time_font, width=50)
        self.cpy_dir_statusbar = ctk.CTkProgressBar(self.cpy_dir_frame, width=50, mode='indeterminate', determinate_speed=1)
        self.cpy_dir_name_lbl = ctk.CTkLabel(self.cpy_dir_frame, text="Copy Output", font=name_font)
        self.cpy_dir_est_lbl.grid(row=0, column=0,padx=5, pady=5)
        self.cpy_dir_time_lbl.grid(row=0, column=1, padx=5, pady=5)
        self.cpy_dir_statusbar.grid(row=0, column=2, padx=5, pady=5)
        self.cpy_dir_name_lbl.grid(row=0, column=3, padx=5, pady=5)

        # Place all frames now
        self.gen_tcl_frame.grid(row=0, column=0, sticky='w')
        self.run_viv_frame.grid(row=1, column=0, sticky='w')
        self.run_viv0_frame.grid(row=2, column=0, sticky='w')
        self.run_viv1_frame.grid(row=3, column=0, sticky='w')
        self.run_viv2_frame.grid(row=4, column=0, sticky='w')
        self.run_viv3_frame.grid(row=5, column=0, sticky='w')
        self.run_viv4_frame.grid(row=6, column=0, sticky='w')
        self.gen_jnb_frame.grid(row=7, column=0, sticky='w')
        self.cpy_dir_frame.grid(row=8, column=0, sticky='w')


    def resize(self, event):
        # Resize event handler.
        self.configure(width=event.width-330, height=event.height/2-80)
        # self.configure(width=event.width-20, height=(event.height/2)-20)

class ConfigMenu(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        window_height = parent.app.get_window_height()
        window_width = parent.app.get_window_width()

        self.configure(width=window_width-10, height=window_height/2)