import customtkinter as ctk
import xml.dom.minidom
import application.hdlgenproject as hdlproj
#######################################
#####      Log Frame Tab View     #####
##### (Frame with Tabbed Top Bar) #####
#######################################
class LogTabView(ctk.CTkTabview):
    def __init__(self, parent):
        super().__init__(parent)

        # Set font of tabs
        dummy_label = ctk.CTkLabel(self, text="dummy") # First get default font
        default_font = dummy_label.cget("font")

        custom_font = (default_font, 20)               # Change size of default font
        self._segmented_button.configure(font=custom_font)

        # Create tabs
        self.add("Project Summary")
        self.add("Testplan")
        self.add("Builder Log")
        self.add("Synthesis Log")
        self.add("Implementation Log")

        # Justify to the LEFT
        self.configure(anchor='nw')

        self.summarytab = SummaryTab(self.tab("Project Summary"))
        self.summarytab.pack()

        # Testplan Box (Its a simply log box with the data set.)
        self.testplan = LogBoxTab(self.tab("Testplan"))
        self.testplan.pack()

        # Load testplan
        proj = hdlproj.HdlgenProject()
        if proj.TBNoteData:
            self.testplan.add_to_log_box(proj.TBNoteData, True)
        else:
            self.testplan.add_to_log_box("No test plan provided.", True)

        # Builder Log Box
        self.builderLog = LogBoxTab(self.tab("Builder Log"))
        self.builderLog.pack()

        # Synthesis Log
        self.synthesisLog = LogBoxTab(self.tab("Synthesis Log"))
        self.synthesisLog.pack()

        # Impl Log
        self.implLog = LogBoxTab(self.tab("Implementation Log"))
        self.implLog.pack()

    def resize(self, event):
        # Call the resize event handler of all tabs
        self.summarytab.resize(event)
        self.testplan.resize(event)
        self.builderLog.resize(event)
        self.synthesisLog.resize(event)
        self.implLog.resize(event)

        # As sample data, add event data to the log boxes.
        self.builderLog.add_to_log_box(str(event)+"\n")
        self.synthesisLog.add_to_log_box(str(event)+"\n")
        self.implLog.add_to_log_box(str(event)+"\n")

##########################################
##### Summary Tab (Scrollable Frame) #####
##########################################
class SummaryTab(ctk.CTkScrollableFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        # Get fonts
        dummy_label = ctk.CTkLabel(self, text="dummy")
        default_font = dummy_label.cget("font")

        text_font = (default_font, 18)
        bold_text_font = (default_font, 18, 'bold')
        sig_dictionary_font = (default_font, 16)

        # This class is a scrollable frame, we just need to now add a grid of all the information I suppose.
        # Scrollables will be needed for items which are very big.
        self.name_lbl = ctk.CTkLabel(self, text="Name", font=bold_text_font, justify='left', anchor='w', width=150)
        self.name_lbl.grid(row=0, column=0, padx=5, pady=5)
        self.name_val_lbl = ctk.CTkLabel(self, text="", font=text_font, justify='left', anchor='w', width=400, wraplength=400)
        self.name_val_lbl.grid(row=0, column=1, padx=5, pady=5)

        self.location_lbl = ctk.CTkLabel(self, text="Location", font=bold_text_font, justify='left', anchor='w', width=150)
        self.location_lbl.grid(row=1, column=0, padx=5, pady=5)
        self.location_var_lbl = ctk.CTkLabel(self, text="", font=text_font, justify='left', anchor='w', width=400, wraplength=400)
        self.location_var_lbl.grid(row=1, column=1, padx=5, pady=5)

        self.environment_lbl = ctk.CTkLabel(self, text="Environment", font=bold_text_font, justify='left', anchor='w', width=150)
        self.environment_lbl.grid(row=2, column=0, padx=5, pady=5)
        self.environment_var_lbl = ctk.CTkLabel(self, text="", font=text_font, justify='left', anchor='w', width=400, wraplength=400)
        self.environment_var_lbl.grid(row=2, column=1, padx=5, pady=5)

        self.vivado_lbl = ctk.CTkLabel(self, text="Vivado Path", font=bold_text_font, justify='left', anchor='w', width=150)
        self.vivado_lbl.grid(row=3, column=0, padx=5, pady=5)
        self.vivado_var_lbl = ctk.CTkLabel(self, text="", font=text_font, justify='left', anchor='w', width=400, wraplength=400)
        self.vivado_var_lbl.grid(row=3, column=1, padx=5, pady=5)

        self.lang_lbl = ctk.CTkLabel(self, text="Language", font=bold_text_font, justify='left', anchor='w', width=150)
        self.lang_lbl.grid(row=4, column=0, padx=5, pady=5)
        self.lang_var_lbl = ctk.CTkLabel(self, text="", font=text_font, justify='left', anchor='w', width=400, wraplength=400)
        self.lang_var_lbl.grid(row=4, column=1, padx=5, pady=5)

        self.auth_lbl = ctk.CTkLabel(self, text="Author", font=bold_text_font, justify='left', anchor='w', width=150)
        self.auth_lbl.grid(row=5, column=0, padx=5, pady=5)
        self.auth_var_lbl = ctk.CTkLabel(self, text="", font=text_font, justify='left', anchor='w', width=400, wraplength=400)
        self.auth_var_lbl.grid(row=5, column=1, padx=5, pady=5)

        self.comp_lbl = ctk.CTkLabel(self, text="Company", font=bold_text_font, justify='left', anchor='w', width=150)
        self.comp_lbl.grid(row=6, column=0, padx=5, pady=5)
        self.comp_var_lbl = ctk.CTkLabel(self, text="", font=text_font, justify='left', anchor='w', width=400, wraplength=400)
        self.comp_var_lbl.grid(row=6, column=1, padx=5, pady=5)

        self.email_lbl = ctk.CTkLabel(self, text="Email", font=bold_text_font, justify='left', anchor='w', width=150)
        self.email_lbl.grid(row=7, column=0, padx=5, pady=5)
        self.email_var_lbl = ctk.CTkLabel(self, text="", font=text_font, justify='left', anchor='w', width=400, wraplength=400)
        self.email_var_lbl.grid(row=7, column=1, padx=5, pady=5)

        self.rhs_signal_frame = ctk.CTkFrame(self, width=550, height=1150)

        self.signal_dict_lbl = ctk.CTkLabel(self.rhs_signal_frame, text="Signal Dictionary", font=bold_text_font, justify='left', anchor='w', width=550)
        self.signal_dict_lbl.grid(row=0, column=0, padx=5, pady=5)
        self.signal_dict_tbox = ctk.CTkTextbox(self.rhs_signal_frame, width=550, font=sig_dictionary_font)
        self.signal_dict_tbox.insert("0.0", "datIn - in - single bit - description\ndatIn - in - single bit - description\ndatIn - in - single bit - description\n")
        self.signal_dict_tbox.grid(row=1, column=0, padx=5, pady=5)

        self.int_sig_dict_lbl = ctk.CTkLabel(self.rhs_signal_frame, text="Internal Signals", font=bold_text_font, justify='left', anchor='w', width=550)
        self.int_sig_dict_lbl.grid(row=2, column=0, padx=5, pady=5)
        self.int_sig_dict_tbox = ctk.CTkTextbox(self.rhs_signal_frame, width=550, font=sig_dictionary_font)
        self.int_sig_dict_tbox.insert("0.0", "datIn - in - single bit - description\ndatIn - in - single bit - description\ndatIn - in - single bit - description\n")
        self.int_sig_dict_tbox.grid(row=3, column=0, padx=5, pady=5)

        self.rhs_signal_frame.grid(row=0, column=2, padx=5, pady=5, rowspan=100)

        self.load_summary()

    #############################################################
    ##### Load the Summary Variables from the HDLGen Object #####
    #############################################################
    def load_summary(self):
        # Load the HDLGen file
        proj = hdlproj.HdlgenProject()

        # Assign the variables
        self.name_val_lbl.configure(text=proj.name)
        self.location_var_lbl.configure(text=proj.location)
        self.environment_var_lbl.configure(text=proj.environment)
        self.vivado_var_lbl.configure(text=proj.vivado_dir)
        self.lang_var_lbl.configure(text=proj.project_language)
        self.auth_var_lbl.configure(text=proj.author)
        self.comp_var_lbl.configure(text=proj.company)
        self.email_var_lbl.configure(text=proj.email)

        # Parsed ports and internal signal strings need to be formatted here.

        # Assign to textboxes
        self.signal_dict_tbox.insert("0.0", proj.parsed_ports)
        self.signal_dict_tbox.configure(state="disabled")
        self.int_sig_dict_tbox.insert("0.0", proj.parsed_internal_sigs)
        self.int_sig_dict_tbox.configure(state="disabled")

    def resize(self, event):
        # print("is 'this' getting called")
        # its possible we need to resize this.
        self.configure(width=event.width-60, height=(event.height/2)-80)

        # Place in grid
        self.name_lbl.grid(row=0, column=0, padx=5, pady=5)
        self.location_lbl .grid(row=1, column=0, padx=5, pady=5)
        self.environment_lbl.grid(row=2, column=0, padx=5, pady=5)
        self.vivado_lbl.grid(row=3, column=0, padx=5, pady=5)
        self.lang_lbl.grid(row=4, column=0, padx=5, pady=5)
        self.auth_lbl.grid(row=5, column=0, padx=5, pady=5)
        self.comp_lbl.grid(row=6, column=0, padx=5, pady=5)
        self.email_lbl.grid(row=7, column=0, padx=5, pady=5)

        self.name_val_lbl.grid(row=0, column=1, padx=5, pady=5)
        self.location_var_lbl.grid(row=1, column=1, padx=5, pady=5)
        self.environment_var_lbl.grid(row=2, column=1, padx=5, pady=5)
        self.vivado_var_lbl.grid(row=3, column=1, padx=5, pady=5)
        self.lang_var_lbl.grid(row=4, column=1, padx=5, pady=5)
        self.auth_var_lbl.grid(row=5, column=1, padx=5, pady=5)
        self.comp_var_lbl.grid(row=6, column=1, padx=5, pady=5)
        self.email_var_lbl.grid(row=7, column=1, padx=5, pady=5)

        if event.width < 1000:
            # Only this one might change.
            self.rhs_signal_frame.grid(row=8, column=0, columnspan=2, rowspan=1, padx=5, pady=5)

            # Notes: All of the labels will stay at 150. Only the vars should expand.
            # # Min width = 800 
            lbl_width = 150
            self.name_lbl.configure(width=lbl_width)
            self.location_lbl .configure(width=lbl_width)
            self.environment_lbl.configure(width=lbl_width)
            self.vivado_lbl.configure(width=lbl_width)
            self.lang_lbl.configure(width=lbl_width)
            self.auth_lbl.configure(width=lbl_width)
            self.comp_lbl.configure(width=lbl_width)
            self.email_lbl.configure(width=lbl_width)

            # label_var_width = 450 when frame = 1200 wide.
            widget_width = (event.width-230) # I think this is right

            self.name_val_lbl.configure(width=widget_width)
            self.location_var_lbl.configure(width=widget_width)
            self.environment_var_lbl.configure(width=widget_width)
            self.vivado_var_lbl.configure(width=widget_width)
            self.lang_var_lbl.configure(width=widget_width)
            self.auth_var_lbl.configure(width=widget_width)
            self.comp_var_lbl.configure(width=widget_width)
            self.email_var_lbl.configure(width=widget_width)
        

            widget_width = (event.width-80)
            self.rhs_signal_frame.configure(width=widget_width)
            self.signal_dict_lbl.configure(width=widget_width)
            self.signal_dict_tbox.configure(width=widget_width)
            self.int_sig_dict_lbl.configure(width=widget_width)
            self.int_sig_dict_tbox.configure(width=widget_width)
            # single column, widen everything.
        else:
            # Only this one might change.
            self.rhs_signal_frame.grid(row=0, column=2, padx=5, pady=5, rowspan=100, columnspan=1)

            # Notes: All of the labels will stay at 150. Only the vars should expand.
            # # Min width = 800 
            lbl_width = 150
            self.name_lbl.configure(width=lbl_width)
            self.location_lbl .configure(width=lbl_width)
            self.environment_lbl.configure(width=lbl_width)
            self.vivado_lbl.configure(width=lbl_width)
            self.lang_lbl.configure(width=lbl_width)
            self.auth_lbl.configure(width=lbl_width)
            self.comp_lbl.configure(width=lbl_width)
            self.email_lbl.configure(width=lbl_width)

            # label_var_width = 450 when frame = 1200 wide.
            label_var_width = 420 + (event.width-1200)/2 # I think this is right

            self.name_val_lbl.configure(width=label_var_width, wraplength=label_var_width)
            self.location_var_lbl.configure(width=label_var_width, wraplength=label_var_width)
            self.environment_var_lbl.configure(width=label_var_width, wraplength=label_var_width)
            self.vivado_var_lbl.configure(width=label_var_width, wraplength=label_var_width)
            self.lang_var_lbl.configure(width=label_var_width, wraplength=label_var_width)
            self.auth_var_lbl.configure(width=label_var_width, wraplength=label_var_width)
            self.comp_var_lbl.configure(width=label_var_width, wraplength=label_var_width)
            self.email_var_lbl.configure(width=label_var_width, wraplength=label_var_width)
        
            rhs_width = 520 + (event.width-1200)/2    # I think this is right
            self.rhs_signal_frame.configure(width=rhs_width)
            self.signal_dict_lbl.configure(width=rhs_width)
            self.signal_dict_tbox.configure(width=rhs_width)
            self.int_sig_dict_lbl.configure(width=rhs_width)
            self.int_sig_dict_tbox.configure(width=rhs_width)


            #   Back up
            # self.name_lbl
            # self.name_val_lbl
            # self.location_lbl 
            # self.location_var_lbl
            # self.environment_lbl
            # self.environment_var_lbl
            # self.vivado_lbl
            # self.vivado_var_lbl
            # self.lang_lbl
            # self.lang_var_lbl
            # self.auth_lbl
            # self.auth_var_lbl
            # self.comp_lbl
            # self.comp_var_lbl
            # self.email_lbl
            # self.email_var_lbl
            # self.rhs_signal_frame 
            # self.signal_dict_lbl
            # self.signal_dict_tbox 
            # self.int_sig_dict_lbl
            # self.int_sig_dict_tbox
            # two column
        


class LogBoxTab(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.log_text_box = ctk.CTkTextbox(self, state='disabled')
        self.log_text_box.pack()

        self.log_data = ""


    def add_to_log_box(self, text, set_text=False):
        if set_text:
            self.log_data = text
        else:
            self.log_data += text
        self.log_text_box.configure(state="normal")
        self.log_text_box.delete("0.0", "end")          # delete all text
        self.log_text_box.insert("0.0", self.log_data)  # repost all text
        self.log_text_box.configure(state="disabled")
        # Get the last line index
        last_line_index = self.log_text_box.index('end-1c linestart')
        # Scroll to the last line
        self.log_text_box.see(last_line_index)

    def resize(self, event):
        self.configure(width=event.width-20, height=(event.height/2)-50)
        self.log_text_box.configure(width=event.width-40, height=(event.height/2)-80)
        # when we resize, maybe we can set the dimensions of the textbox.
        # its possible we need to resize this

# class ConfigTabView(ctk.CTkTabview):
#     def __init__(self, parent):
#         super().__init__(parent)

#         self.parent = parent

#         window_height = parent.parent.app.get_window_height()
#         window_width = parent.parent.app.get_window_width()

#         self.configure(width=window_width-290, height=(window_height/2))
        
#         # Set size of tabs
#         dummy_label = ctk.CTkLabel(self, text="dummy")
#         default_font = dummy_label.cget("font")

#         tab_font = (default_font, 20)
#         text_font = (default_font, 20)
#         bold_text_font = (default_font, 24, 'bold')


#         self._segmented_button.configure(font=tab_font)

#         # Create tabs
#         self.add("Build Status")
#         self.add("Project Config")
#         self.add("I/O Config")
#         self.add("App Preferences")

#         # Justify to the LEFT
#         self.configure(anchor='nw')

#         # Add widgets to each tab?
#         # self.label = ctk.CTkLabel(master=self.tab("Project Config"), text="Project Config Area")
#         # self.label.pack()

#         self.label = ctk.CTkLabel(master=self.tab("I/O Config"), text="I/O Config Area")
#         self.label.pack()

#         self.label = ctk.CTkLabel(master=self.tab("App Preferences"), text="App Preferences Area")
#         self.label.pack()

#         ######## RESIZING NOTES
#         # 960 is minimum for 2 column (text and Vivado Settings)
#         # 1280 is minimum for 3 columns
#         # 1560 is minimum for 4 columns

#         # self.label = ctk.CTkLabel(master=self.tab("Project Config"), text="Vivado Settings")
#         # self.label.pack()
#         self.configure(width=window_width-290, height=(window_height/2))

#         self.project_config_scrollable = ctk.CTkScrollableFrame(self.tab("Project Config"), width=window_width-310, height=(window_height/2)-80)
        
#         self.project_config_scrollable._scrollbar.configure(height=0)
        
#         # self.project_config_scrollable.pack_propagate(0)
#         self.project_config_scrollable.pack()

#         self.RHS_switch_frame = ctk.CTkFrame(self.project_config_scrollable)
#         self.LHS_explaination_frame = ctk.CTkFrame(self.RHS_switch_frame, width=500)
#         self.LHS_explaination_frame.grid(row=0, column=0, rowspan=100, padx=5, sticky="news")

#         self.switch_var0 = ctk.StringVar(value="on")
    
#         # Vivado Settings
#         self.vivado_settings_lbl = ctk.CTkLabel(self.RHS_switch_frame, text="Vivado Settings", font=bold_text_font)
#         # self.vivado_settings_lbl.grid(row=0, column=1, padx=5, pady=5)    # No need to pack these because the resize() call handles it.

#         self.open_viv_sw = ctk.CTkSwitch(self.RHS_switch_frame, text="Open Vivado GUI", 
#                                         variable=self.switch_var0, onvalue="on", offvalue="off", font=text_font)
#         # self.open_viv_sw.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
#         self.keep_viv_open_sw = ctk.CTkSwitch(self.RHS_switch_frame, text="Keep Vivado Open", 
#                                         variable=self.switch_var0, onvalue="on", offvalue="off", font=text_font)
#         # self.keep_viv_open_sw.grid(row=2, column=1, padx=5, pady=5, sticky="w")
    
#         self.always_regen_bd_sw = ctk.CTkSwitch(self.RHS_switch_frame, text="Always Regenerate Block Design", 
#                                         variable=self.switch_var0, onvalue="on", offvalue="off", font=text_font)
#         # self.always_regen_bd_sw.grid(row=3, column=1, padx=5, pady=5, sticky="w")

    


#         # Jupyter Notebook Settings
#         self.jupyter_settings_lbl = ctk.CTkLabel(self.RHS_switch_frame, text="Jupyter Notebook Settings", font=bold_text_font)
#         # self.jupyter_settings_lbl.grid(row=0, column=2, padx=5, pady=5)

#         self.gen_when_build_sw = ctk.CTkSwitch(self.RHS_switch_frame, text="Generate when Building", 
#                                         variable=self.switch_var0, onvalue="on", offvalue="off", font=text_font)
#         # self.gen_when_build_sw.grid(row=1, column=2, padx=5, pady=5, sticky="w")
        
#         self.gen_tst_sw = ctk.CTkSwitch(self.RHS_switch_frame, text="Generate using Testplan", 
#                                         variable=self.switch_var0, onvalue="on", offvalue="off", font=text_font)
#         # self.gen_tst_sw.grid(row=2, column=2, padx=5, pady=5, sticky="w")

#         # PYNQ Board Settings
#         self.pynq_board_settings_lbl = ctk.CTkLabel(self.RHS_switch_frame, text="PYNQ Board Settings", font=bold_text_font)
#         # self.pynq_board_settings_lbl.grid(row=0, column=3, padx=5, pady=5)

#         self.gen_io_sw = ctk.CTkSwitch(self.RHS_switch_frame, text="Make Connections to Board I/O", 
#                                         variable=self.switch_var0, onvalue="on", offvalue="off", font=text_font)
#         # self.gen_io_sw.grid(row=1, column=3, padx=5, pady=5, sticky="w")


#         self.RHS_switch_frame.grid()

#         # Set tab
#         self.set("Project Config")

#     def resize(self, event):
#         # Default#
#         LHS_width_old = (event.width-310)/2
#         LHS_width = (event.width/2)-330
#         self.LHS_explaination_frame.configure(width=LHS_width)
#         self.LHS_explaination_frame.grid(row=0, column=0, rowspan=100, padx=5, sticky="news")

#         if (event.width-310)/2 > 685:
#             # Vivado Settings
#             self.vivado_settings_lbl.grid(row=0, column=1, padx=5, pady=5, sticky="news")
#             self.open_viv_sw.grid(row=1, column=1, padx=5, pady=5, sticky="w")
#             self.keep_viv_open_sw.grid(row=2, column=1, padx=5, pady=5, sticky="w")
#             self.always_regen_bd_sw.grid(row=3, column=1, padx=5, pady=5, sticky="w")
#             # Jupyter Notebook Settings
#             self.jupyter_settings_lbl.grid(row=0, column=2, padx=5, pady=5, sticky="news")
#             self.gen_when_build_sw.grid(row=1, column=2, padx=5, pady=5, sticky="w")
#             self.gen_tst_sw.grid(row=2, column=2, padx=5, pady=5, sticky="w")
#             # PYNQ Board Settings
#             self.pynq_board_settings_lbl.grid(row=4, column=1, padx=5, pady=5, sticky="news")
#             self.gen_io_sw.grid(row=5, column=1, padx=5, pady=5, sticky="w")     
#         elif (event.width-310)/2 > 425:
#             # Vivado Settings
#             self.vivado_settings_lbl.grid(row=0, column=1, padx=5, pady=5, sticky="news")
#             self.open_viv_sw.grid(row=1, column=1, padx=5, pady=5, sticky="w")
#             self.keep_viv_open_sw.grid(row=2, column=1, padx=5, pady=5, sticky="w")
#             self.always_regen_bd_sw.grid(row=3, column=1, padx=5, pady=5, sticky="w")
#             # Jupyter Notebook Settings
#             self.jupyter_settings_lbl.grid(row=4, column=1, padx=5, pady=5, sticky="news")
#             self.gen_when_build_sw.grid(row=5, column=1, padx=5, pady=5, sticky="w")
#             self.gen_tst_sw.grid(row=6, column=1, padx=5, pady=5, sticky="w")
#             # PYNQ Board Settings
#             self.pynq_board_settings_lbl.grid(row=7, column=1, padx=5, pady=5, sticky="news")
#             self.gen_io_sw.grid(row=8, column=1, padx=5, pady=5, sticky="w")
#         else:
#             # In this event, we just wanna have everything on top and make it get as wide as it needs.
#             self.LHS_explaination_frame.configure(width=(event.width-330))
#             self.LHS_explaination_frame.grid(row=110, column=0, padx=5, pady=5, sticky="news")

#             # Vivado Settings
#             self.vivado_settings_lbl.grid(row=101, column=0, padx=5, pady=5, sticky="news")
#             self.open_viv_sw.grid(row=102, column=0, padx=5, pady=5, sticky="w")
#             self.keep_viv_open_sw.grid(row=103, column=0, padx=5, pady=5, sticky="w")
#             self.always_regen_bd_sw.grid(row=104, column=0, padx=5, pady=5, sticky="w")
#             # Jupyter Notebook Settings
#             self.jupyter_settings_lbl.grid(row=105, column=0, padx=5, pady=5, sticky="news")
#             self.gen_when_build_sw.grid(row=106, column=0, padx=5, pady=5, sticky="w")
#             self.gen_tst_sw.grid(row=107, column=0, padx=5, pady=5, sticky="w")
#             # PYNQ Board Settings
#             self.pynq_board_settings_lbl.grid(row=108, column=0, padx=5, pady=5, sticky="news")
#             self.gen_io_sw.grid(row=109, column=0, padx=5, pady=5, sticky="w")

# class ConfigMenu(ctk.CTkFrame):
#     def __init__(self, parent):
#         super().__init__(parent)

#         window_height = parent.app.get_window_height()
#         window_width = parent.app.get_window_width()

#         self.configure(width=window_width-10, height=window_height/2)

