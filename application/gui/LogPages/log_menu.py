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
        self.parent = parent
        self.hdlgen_prj = None
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

        self.summarytab = SummaryTab(self.tab("Project Summary"), parent)
        self.summarytab.pack()

        # Testplan Box
        self.testplan = LogBoxTab(self.tab("Testplan"))
        self.testplan.pack()

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

    def load_project(self):
        self.hdlgen_prj = self.parent.hdlgen_prj
        # Who needs calling?
        # 1) Summary
        # 2) Testplan
        self.summarytab.load_project()
        
        if self.hdlgen_prj.TBNoteData:
            self.testplan.add_to_log_box(self.hdlgen_prj.TBNoteData, True)
        else:
            self.testplan.add_to_log_box("No test plan provided.", True)

        # Question? Can we now pass the log boxes as parameters to the hdlgen_proj making logging available to all?
        # No other set up should be required from down there.
        self.hdlgen_prj.set_build_logger(self.builderLog)
        self.hdlgen_prj.set_synth_logger(self.synthesisLog)
        self.hdlgen_prj.set_impl_logger(self.implLog)

##########################################
##### Summary Tab (Scrollable Frame) #####
##########################################
class SummaryTab(ctk.CTkScrollableFrame):
    def __init__(self, parent, tabview):
        super().__init__(parent)
        self.parent = parent
        self.tabview = tabview # This is the parent tabview, the parent is here the frame of the tab

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

    #############################################################
    ##### Load the Summary Variables from the HDLGen Object #####
    #############################################################
    def load_project(self):
        self.hdlgen_prj = self.tabview.hdlgen_prj

        # Assign the variables
        self.name_val_lbl.configure(text=self.hdlgen_prj.name)
        self.location_var_lbl.configure(text=self.hdlgen_prj.location)
        self.environment_var_lbl.configure(text=self.hdlgen_prj.environment)
        self.vivado_var_lbl.configure(text=self.hdlgen_prj.vivado_dir)
        self.lang_var_lbl.configure(text=self.hdlgen_prj.project_language)
        self.auth_var_lbl.configure(text=self.hdlgen_prj.author)
        self.comp_var_lbl.configure(text=self.hdlgen_prj.company)
        self.email_var_lbl.configure(text=self.hdlgen_prj.email)

        # Parsed ports and internal signal strings need to be formatted here.

        # Assign to textboxes
        self.signal_dict_tbox.insert("0.0", self.hdlgen_prj.parsed_ports)
        self.signal_dict_tbox.configure(state="disabled")
        self.int_sig_dict_tbox.insert("0.0", self.hdlgen_prj.parsed_internal_sigs)
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
