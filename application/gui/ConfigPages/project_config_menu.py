import customtkinter as ctk
import application.gui.io_config_page as io_config_page


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
        # self.add("App Preferences")

        # Justify to the LEFT
        self.configure(anchor='nw')

        # Add widgets to each tab?
        # self.label = ctk.CTkLabel(master=self.tab("Project Config"), text="Project Config Area")
        # self.label.pack()

        # self.label = ctk.CTkLabel(master=self.tab("I/O Config"), text="I/O Config Area")
        # self.label.pack()
        self.ioconfigpage = PortConfigTab(self.tab("I/O Config"))  # IOConfigTab
        self.ioconfigpage.pack(expand=True, fill='both', anchor='center')

        self.buildstatuspage = BuildStatusTab(self.tab("Build Status"))
        self.buildstatuspage.pack()


        # self.label = ctk.CTkLabel(master=self.tab("App Preferences"), text="App Preferences Area")
        # self.label.pack()

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
        self.ioconfigpage.resize(event)
        # self.LHS_explaination_frame.configure(width=(event.width-310)/2)
        self.LHS_explaination_frame.configure(width=(event.width/2)-280)
        self.LHS_explaination_frame.grid(row=0, column=0, rowspan=100, padx=5, sticky="news")

        if (event.width-310)/2 > 685:
            ### 2 Columns

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
            # self.pynq_board_settings_lbl.grid(row=4, column=1, padx=5, pady=5, sticky="news")
            # self.gen_io_sw.grid(row=5, column=1, padx=5, pady=5, sticky="w")     
        elif (event.width-310)/2 > 425:
            # This is one column too?
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
            # self.pynq_board_settings_lbl.grid(row=7, column=1, padx=5, pady=5, sticky="news")
            # self.gen_io_sw.grid(row=8, column=1, padx=5, pady=5, sticky="w")
        else:
            # Single Coloumn

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
            # self.pynq_board_settings_lbl.grid(row=108, column=0, padx=5, pady=5, sticky="news")
            # self.gen_io_sw.grid(row=109, column=0, padx=5, pady=5, sticky="w")

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
        
        ### Overall Status:
        self.title_status_frame = ctk.CTkFrame(self)
        self.title_text = ctk.CTkLabel(self.title_status_frame, text="Current State:", font=name_font, width=160)
        self.title_text_val = ctk.CTkLabel(self.title_status_frame, text="Builder is Idle", font=(default_font, 20), width=160)
        self.title_text.grid(row=0, column=0, padx=5, pady=5)
        self.title_text_val.grid(row=0, column=1, padx=5, pady=5, sticky='e')

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
        self.title_status_frame.grid(row=0, column=0, sticky='w')
        self.gen_tcl_frame.grid(row=1, column=0, sticky='w')
        self.run_viv_frame.grid(row=2, column=0, sticky='w')
        self.run_viv0_frame.grid(row=3, column=0, sticky='w')
        self.run_viv1_frame.grid(row=4, column=0, sticky='w')
        self.run_viv2_frame.grid(row=5, column=0, sticky='w')
        self.run_viv3_frame.grid(row=6, column=0, sticky='w')
        self.run_viv4_frame.grid(row=7, column=0, sticky='w')
        self.gen_jnb_frame.grid(row=8, column=0, sticky='w')
        self.cpy_dir_frame.grid(row=9, column=0, sticky='w')

    def resize(self, event):
        # Resize event handler.
        self.configure(width=event.width-330, height=event.height/2-80)
        # self.configure(width=event.width-20, height=(event.height/2)-20)

class PortConfigTab(ctk.CTkScrollableFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self._scrollbar.configure(height=0)

        dummy_label = ctk.CTkLabel(self, text="dummy")
        default_font = dummy_label.cget("font")

        title_font = (default_font, 20, 'bold')
        subtitle_font = (default_font, 16)
        master_switch_font = (default_font, 16, 'bold')
        switch_font = (default_font, 16)

        # Internal Signals Frame
        self.LHS_frame = ctk.CTkFrame(self)
        self.int_signals_lbl = ctk.CTkLabel(self.LHS_frame, text="Connect Internal Signal a Port?", font=title_font)
        self.int_signals_explaination_lbl = ctk.CTkLabel(self.LHS_frame, text="Enabling an internal signal here will connect it to a port on the component, making it accessible by board I/O and in Jupyter Notebook", font=subtitle_font)

        self.sw0 = ctk.CTkSwitch(self.LHS_frame, text="intTC", font=switch_font, width=140)
        self.sw1 = ctk.CTkSwitch(self.LHS_frame, text="NS", font=switch_font, width=140)
        self.sw2 = ctk.CTkSwitch(self.LHS_frame, text="CS", font=switch_font, width=140)
        self.sw3 = ctk.CTkSwitch(self.LHS_frame, text="nextOP", font=switch_font, width=140)
        self.sw4 = ctk.CTkSwitch(self.LHS_frame, text="decoded", font=switch_font, width=140)
        self.sw5 = ctk.CTkSwitch(self.LHS_frame, text="intSelMux", font=switch_font, width=140)

        self.switches = [self.sw0, self.sw1, self.sw2, self.sw3, self.sw4, self.sw5]

        # LED Connections
        self.RHS_frame = ctk.CTkFrame(self)

        self.led_title = ctk.CTkLabel(self.RHS_frame, text="Board LED Configuration", font=title_font)
        self.led_subtext = ctk.CTkLabel(self.RHS_frame, text="Connect ports of component to LEDs on PYNQ Board", font=subtitle_font)

        self.on_off_switch = ctk.CTkSwitch(self.RHS_frame, text="Enable LEDs?", font=master_switch_font)
        self.on_off_subtext = ctk.CTkLabel(self.RHS_frame, text="If enabled, connect component to LEDs\nIf disabled, no LEDs are connected", font=subtitle_font)

        self.led0_lbl = ctk.CTkLabel(self.RHS_frame, text="LED0", width=50, font=switch_font)
        self.led0_dropdown = ctk.CTkOptionMenu(self.RHS_frame, values=["signal1", "signal2", "signal3", "signal4", "signal5"], font=switch_font)
        self.led0_entry = ctk.CTkEntry(self.RHS_frame, placeholder_text="(0-63)", width=50, font=switch_font)
        self.led0_entry_placeholder = ctk.CTkLabel(self.RHS_frame, font=switch_font)

        self.led1_lbl = ctk.CTkLabel(self.RHS_frame, text="LED1", width=50, font=switch_font)
        self.led1_dropdown = ctk.CTkOptionMenu(self.RHS_frame, values=["signal1", "signal2", "signal3", "signal4", "signal5"], font=switch_font)
        self.led1_entry = ctk.CTkEntry(self.RHS_frame, placeholder_text="(0-63)", width=50, font=switch_font)
        self.led1_entry_placeholder = ctk.CTkLabel(self.RHS_frame, text="")

        self.led2_lbl = ctk.CTkLabel(self.RHS_frame, text="LED2", width=50, font=switch_font)
        self.led2_dropdown = ctk.CTkOptionMenu(self.RHS_frame, values=["signal1", "signal2", "signal3", "signal4", "signal5"], font=switch_font)
        self.led2_entry = ctk.CTkEntry(self.RHS_frame, placeholder_text="(0-63)", width=50, font=switch_font)
        self.led2_entry_placeholder = ctk.CTkLabel(self.RHS_frame, text="")

        self.led3_lbl = ctk.CTkLabel(self.RHS_frame, text="LED3", width=50, font=switch_font)
        self.led3_dropdown = ctk.CTkOptionMenu(self.RHS_frame, values=["signal1", "signal2", "signal3", "signal4", "signal5"], font=switch_font)
        self.led3_entry = ctk.CTkEntry(self.RHS_frame, placeholder_text="(0-63)", width=50, font=switch_font)
        self.led3_entry_placeholder = ctk.CTkLabel(self.RHS_frame,text="")



    def resize(self, event):
        # print("Am I getting called")
        frame_width = event.width-330
        frame_height=event.height/2-80

        self.configure(width=frame_width, height=frame_height)

        # 1 at less than 1000
        # 2 COlumn at 1200
        # 3 at 1400
        # 4 at 1800

        number_of_columns = 2   # Default / Failsafe
        if event.width < 1000:
            number_of_columns = 1
        elif event.width < 1350:
            number_of_columns = 2
        elif event.width < 1800:
            number_of_columns = 3
        else:
            number_of_columns = 4



        # Calc number of columns in the LHS frame
        # if event.width < x: # Single Column
        # elif event.width < x: Double Column
        # number_of_columns = 2
        # # else:
        # number_of_columns = 3


        self.LHS_frame.grid(row=0, column=0, sticky='n')
        # 1) Place the widget
        # 2) Set the width and wraplength (and height if need be)
        self.int_signals_lbl.grid(row=0, column=0, padx=5, pady=5, columnspan=number_of_columns)
        self.int_signals_explaination_lbl.grid(row=1, column=0, padx=5, pady=5, columnspan=number_of_columns)
        self.int_signals_lbl.configure(width=frame_width/2-10, wraplength=frame_width/2-10)
        self.int_signals_explaination_lbl.configure(width=frame_width/2-10, wraplength=frame_width/2-10)
        

        for index in range(0, len(self.switches)):
            row = 2 + (index // number_of_columns)          # eg if num_col = 2: (2 is offset for title + explaination cards) Floor divide - 0 = 0, 1 = 0, 2 = 1, 3 = 1, 4 = 2.
            column = index % number_of_columns              # Remainder - 0 = 0, 1 = 1, 2 = 0, 3 = 1, 4 = 0
            self.switches[index].grid(row=row, column=column, padx=5, pady=5)

        self.RHS_frame.grid(row=0, column=1, sticky='n')

        self.led_title.grid(row=0, column=0, padx=5, pady=5, columnspan=3)
        self.led_subtext.grid(row=1, column=0, padx=5, pady=5, columnspan=3)
        self.led_title.configure(width=frame_width/2-10, wraplength=frame_width/2-10)
        self.led_subtext.configure(width=frame_width/2-10, wraplength=frame_width/2-10)

        self.on_off_switch.grid(row=2, column=0, padx=5, pady=5, columnspan=3)
        self.on_off_subtext.grid(row=3, column=0, padx=5, pady=5, columnspan=3)
        self.on_off_subtext.configure(width=frame_width/2-10, wraplength=frame_width/2-10)

        self.led0_lbl.grid(row=4, column=0, padx=5, pady=5, sticky='e')
        self.led0_dropdown.grid(row=4, column=1, padx=5, pady=5)
        self.led0_entry.grid(row=4, column=2, padx=5, pady=5, sticky='w')
        # self.led0_entry_placeholder.grid(row=2, column=3, padx=5, pady=5)

        self.led1_lbl.grid(row=5, column=0, padx=5, pady=5, sticky='e')
        self.led1_dropdown.grid(row=5, column=1, padx=5, pady=5)
        self.led1_entry.grid(row=5, column=2, padx=5, pady=5, sticky='w')
        # self.led1_entry_placeholder.grid(row=3, column=3, padx=5, pady=5)

        self.led2_lbl.grid(row=6, column=0, padx=5, pady=5, sticky='e')
        self.led2_dropdown.grid(row=6, column=1, padx=5, pady=5)
        self.led2_entry.grid(row=6, column=2, padx=5, pady=5, sticky='w')
        # self.led2_entry_placeholder.grid(row=4, column=3, padx=5, pady=5)

        self.led3_lbl.grid(row=7, column=0, padx=5, pady=5, sticky='e')
        self.led3_dropdown.grid(row=7, column=1, padx=5, pady=5)
        self.led3_entry.grid(row=7, column=2, padx=5, pady=5, sticky='w')
        # self.led3_entry_placeholder.grid(row=5, column=3, padx=5, pady=5)

class IOConfigTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent



        ## Row 0
        # Title Label
        self.title_font = ("Segoe UI", 20, "bold") # Title font
        self.title_label = ctk.CTkLabel(self, text="Configure Board I/O Connections", font=self.title_font, padx=10)
        self.title_label.grid(row=0, column=0, columnspan=3, pady=10)


        def config_button_selected():
            pass

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        # self.rowconfigure(0, weight=1)
        # self.rowconfigure(1, weight=1)
        # self.rowconfigure(2, weight=1)
        # self.rowconfigure(3, weight=1)


        # Row 1
        self.led_button = ctk.CTkButton(self, text="LEDs",  width=140) #command=self.app.open_io_led_window,
        self.sw_btn_button = ctk.CTkButton(self, text="Switches+Buttons", command=config_button_selected, width=140)
        self.clk_crypto_button = ctk.CTkButton(self, text="Clock+Crypto", command=config_button_selected, width=140)
        self.led_button.grid(row=1, column=0, padx=10, pady=5)
        self.sw_btn_button.grid(row=1, column=1, padx=10, pady=5)
        self.clk_crypto_button.grid(row=1, column=2, padx=10, pady=5)
        # led_button.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        # sw_btn_button.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")
        # clk_crypto_button.grid(row=1, column=2, padx=10, pady=5, sticky="nsew")

        ## Row 2
        self.arduino_button = ctk.CTkButton(self, text="Arduino", command=config_button_selected, width=140)
        self.raspberry_pi_button = ctk.CTkButton(self, text="Raspberry Pi", command=config_button_selected, width=140)
        self.pmod_button = ctk.CTkButton(self, text="Pmod", command=config_button_selected, width=140)
        self.arduino_button.grid(row=2, column=0, padx=10, pady=5)
        self.raspberry_pi_button.grid(row=2, column=1, padx=10, pady=5)
        self.pmod_button.grid(row=2, column=2, padx=10, pady=5)
        # arduino_button.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        # raspberry_pi_button.grid(row=2, column=1, padx=10, pady=5, sticky="nsew")
        # pmod_button.grid(row=2, column=2, padx=10, pady=5, sticky="nsew")

        # Row 3
        self.hdmi_button = ctk.CTkButton(self, text="HDMI", command=config_button_selected, width=140)
        self.audio_button = ctk.CTkButton(self, text="Audio", command=config_button_selected, width=140)
        self.analog_input_button = ctk.CTkButton(self, text="Single Ended Analog", command=config_button_selected, width=140)
        self.hdmi_button.grid(row=3, column=0, padx=10, pady=5)
        self.audio_button.grid(row=3, column=1, padx=10, pady=5)
        self.analog_input_button.grid(row=3, column=2, padx=10, pady=5)
        # hdmi_button.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")
        # audio_button.grid(row=3, column=1, padx=10, pady=5, sticky="nsew")
        # analog_input_button.grid(row=3, column=2, padx=10, pady=5, sticky="nsew")

        # Disable all buttons that aren't available for now
        # led_button.configure(state="disabled")        # LED mode works.
        self.sw_btn_button.configure(state="disabled")
        self.clk_crypto_button.configure(state="disabled")
        self.arduino_button.configure(state="disabled")
        self.raspberry_pi_button.configure(state="disabled")
        self.pmod_button.configure(state="disabled")
        self.hdmi_button.configure(state="disabled")
        self.audio_button.configure(state="disabled")
        self.analog_input_button.configure(state="disabled")

    def resize(self, event):
        # Resize event handler.
        self.configure(width=event.width-330, height=event.height/2-80)
        # self.configure(width=event.width-20, height=(event.height/2)-20)
        print("I was called")
        button_width = 140
        if event.width < 1000:
            button_width = 150
        elif event.width < 1200:
            button_width = 200
        elif event.width < 1400:
            button_width = 250
        else:
            button_width = 300


        button_height = 28
        if event.height < 600:
            button_height = 36
        elif event.height < 700:
            button_height = 48
        else:
            button_height = 56


        print(f"Height: {button_height}, Width: {button_width}")
        self.led_button.configure(width=button_width, height=button_height)
        self.sw_btn_button.configure(width=button_width, height=button_height)
        self.clk_crypto_button.configure(width=button_width, height=button_height)
        self.arduino_button.configure(width=button_width, height=button_height)
        self.raspberry_pi_button.configure(width=button_width, height=button_height)
        self.pmod_button.configure(width=button_width, height=button_height)
        self.hdmi_button.configure(width=button_width, height=button_height)
        self.audio_button.configure(width=button_width, height=button_height)
        self.analog_input_button.configure(width=button_width, height=button_height)


class ConfigMenu(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        window_height = parent.app.get_window_height()
        window_width = parent.app.get_window_width()

        self.configure(width=window_width-10, height=window_height/2)