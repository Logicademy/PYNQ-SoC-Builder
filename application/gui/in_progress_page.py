import customtkinter as ctk
from tktooltip import ToolTip
import os
import application.pynq_manager as pm
import pyperclip
import threading
import time

class In_Progress_Page(ctk.CTkFrame):
    def __init__(self, app):
        ctk.CTkFrame.__init__(self, app.root)
        self.app = app
        # self.configure(["-width", "500"])
        # self.configure(["-height", "240"])


        # Title Row
        row_0_frame = ctk.CTkFrame(self, width=500, height=30, corner_radius=0)
        row_0_frame.grid(row=0, column=0, sticky="nsew")
        title_font = ("Segoe UI", 20, "bold") # Title font
        title_label = ctk.CTkLabel(row_0_frame, text="PYNQ SoC Builder", font=title_font, width=500)
        title_label.grid(row=0, column=0, sticky="nsew")

        # row_1_scrollable_frame = ctk.CTkScrollableFrame(self, height=100, width=480)
        # # NB Do Not Delete: Scrollable frame has bug that without this line, frame cannot be less than 200 pixel
        # row_1_scrollable_frame._scrollbar.configure(height=0)   
        # row_1_scrollable_frame.grid(row=1, column=0, sticky="e") #sticky="ew"

        self.log_data = ""
        # scrolling_label = ctk.CTkLabel(row_1_scrollable_frame, text=log_data, wraplength=480, anchor="e")
        self.scrolling_entry_variable = ctk.StringVar()
        self.scrolling_entry_variable.set(self.log_data)
        
        self.log_text_box = ctk.CTkTextbox(self, width=500, height=170, corner_radius=0)
        self.log_text_box.insert("0.0", self.log_data)
        self.log_text_box.configure(state="disabled")
        self.log_text_box.grid(row=1, column=0)

        row_2_frame = ctk.CTkFrame(self,width=500, height=30)
        row_2_frame.grid(row=2, column=0, sticky="nsew")

        self.progress_bar = ctk.CTkProgressBar(row_2_frame, progress_color="green", orientation="horizontal", width=500, height=10, corner_radius=0)
        self.progress_bar.pack()
        self.progress_bar.stop()


        bottom_row_frame = ctk.CTkFrame(self, width=500, height=20)
        bottom_row_frame.grid(row=3, column=0, sticky="nsew")

        copy_to_clip_button = ctk.CTkButton(bottom_row_frame, width=150, text="Copy Log to Clipboard", command=self.copy_logs_to_clip)
        self.force_quit_button = ctk.CTkButton(bottom_row_frame, width=150, text="Force Quit", fg_color="red3", hover_color="red4", command=self.app.on_close)
        self.go_back_complete_button = ctk.CTkButton(bottom_row_frame, width=150, text="Return", fg_color="green3", hover_color="green4", command=self.on_return_button)
        
        bottom_row_frame.columnconfigure(1,weight=1)
        copy_to_clip_button.grid(row=0, column=0)
        self.force_quit_button.grid(row=0, column=1,sticky="e")

        # go_back_complete_button.grid(row=0, column=1,sticky="e")

    def copy_logs_to_clip(self):
        pyperclip.copy(self.log_data)

    def add_to_log_box(self, text):
        self.log_text_box.configure(state="normal")
        self.log_data += text
        self.log_text_box.delete("0.0", "end")  # delete all text
        self.log_text_box.insert("0.0", self.log_data) # repost all text
        self.log_text_box.configure(state="disabled")

    def run_pynq_manager(self):
        self.add_to_log_box(f"\n\nRunning in mode {self.app.mode} commencing at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}")
        self.add_to_log_box(f"\nHDLGen Project: {self.app.hdlgen_path}")
        self.progress_bar.configure(mode="indeterminate", indeterminate_speed=0.4)
        self.progress_bar.start()

        pm_obj = pm.Pynq_Manager(self.app.hdlgen_path)
        if not pm_obj.get_board_config_exists():
            self.app.top_level_message = "Could not find PYNQ-Z2 board files in Vivado directory. Do you wish to continue? - Bitstream output may crash FPGA if not configured"
            self.app.open_dialog()

            # Wait for the user to click their response
            self.app.toplevel_window.wait_window()

            print(self.app.dialog_response)
            response = self.app.dialog_response
            if response == "yes":
                self.add_to_log_box("\nCRITICAL: Project Not Configured for PYNQ-Z2 board, bitstream compilation may fail or generated bitstream may have crash or behave unexpectedly on FPGA.")
                self.app.skip_board_config = True
            elif response == "no":
                # self.app.show_page(self.app.page1)
                self.app.skip_board_config = False
                self.add_to_log_box("\nClosing Project: PYNQ-Z2 Board Config Not Found - Quitting.")
                return False
            else:
                print("Invalid response from Dialog, regenerate_bd = False (default)")

        if self.app.mode == self.app.page1.mode_menu_options[0]:    # Run All
            thread = threading.Thread(target=self.run_all)
            thread.start()
        elif self.app.mode == self.app.page1.mode_menu_options[1]:  # Generate Tcl
            thread = threading.Thread(target=self.generate_tcl)
            thread.start()
        elif self.app.mode == self.app.page1.mode_menu_options[2]:  # Run Vivado
            thread = threading.Thread(target=self.run_vivado)
            thread.start()
        elif self.app.mode == self.app.page1.mode_menu_options[3]:  # Copy Bitstream
            thread = threading.Thread(target=self.copy_to_dir)
            thread.start()
        elif self.app.mode == self.app.page1.mode_menu_options[4]:  # Generate JNB
            thread = threading.Thread(target=self.generate_jnb)
            thread.start()
        elif self.app.mode == self.app.page1.mode_menu_options[5]:  # Generate Generic JNB
            # thread = threading.Thread(target=self.run_all)
            # thread.start()
            self.add_to_log_box("Not yet implemented in Pynq_Manager.py")
        self.app.build_running = True
        return True


    def run_all(self):
        self.progress_bar.start()
        self.generate_tcl(False)    # False flag used to ask func not to assert complete after running
        self.run_vivado(False)      # this is because we are running many functions and wish only to assert at very end
        self.copy_to_dir(False)
        self.generate_jnb(False)
        self.operation_completed()

    def generate_tcl(self, assert_complete=True):
        regenerate_bd = True # Default
        # start_gui = True 
        # keep_vivado_open = False

        # Checkbox_values shared variable is mapped as open_gui_var/keep_gui_open_var
        # self.app.checkbox_values = [open_gui_var.get(), keep_gui_open_var.get()]
        start_gui = self.app.checkbox_values[0]
        keep_vivado_open = self.app.checkbox_values[1]

        # I/O Mapping
        # If "Use Board I/O" checkbox is enabled, pass io_configuration.
        # If not, pass None.
        use_board_io = self.app.checkbox_values[4]
        if use_board_io:
            io_map = self.app.io_configuration
        else:
            io_map = None

        # Run check here, and run dialog:
        pm_obj = pm.Pynq_Manager(self.app.hdlgen_path)
        response = None
        if pm_obj.get_bd_exists():
            self.app.top_level_message = "A block diagram already exists, would you like to regenerate a fresh BD?"
            self.app.open_dialog()
            
            # Wait for the user to click their response
            self.app.toplevel_window.wait_window()

            print(self.app.dialog_response)
            response = self.app.dialog_response
            if response == "yes":
                regenerate_bd = True
            elif response == "no":
                regenerate_bd = False
            else:
                print("Invalid response from Dialog, regenerate_bd = False (default)")
        
        pm_obj.generate_tcl(regenerate_bd=regenerate_bd, start_gui=start_gui, keep_vivado_open=keep_vivado_open, skip_board_config=self.app.skip_board_config, io_map=io_map)
        
        if assert_complete:
            self.operation_completed()

    def run_vivado(self, assert_complete=True):
        pm_obj = pm.Pynq_Manager(self.app.hdlgen_path)
        pm_obj.run_vivado()
        self.operation_completed()

    def copy_to_dir(self, assert_complete=True):
        pm_obj = pm.Pynq_Manager(self.app.hdlgen_path)
        res = pm_obj.copy_to_dir()
        if not res:
            self.app.top_level_message = "Could not find .bit file - Please see Vivado logs for information"
            self.app.open_alert()
        if assert_complete:
            self.operation_completed()

    def generate_jnb(self, assert_complete=True):
        generate_jnb = self.app.checkbox_values[2]
        use_testplan = self.app.checkbox_values[3]
        generic = not use_testplan

        if generate_jnb:
            pm_obj = pm.Pynq_Manager(self.app.hdlgen_path)
            pm_obj.generate_jnb(generic=generic)
        
        if assert_complete:
            self.operation_completed()

    def operation_completed(self):
        self.force_quit_button.destroy()
        self.app.build_running = False
        self.go_back_complete_button.grid(row=0, column=1,sticky="e")
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.stop()    # Stop the progress bar from moving more
        self.progress_bar.set(1)    # Set progress bar to full
    
    def on_return_button(self):
        # HDLGen file exists:
        # Move to page two:
        self.app.show_page(self.app.page1)

    def show(self):
        self.pack()
    
    def hide(self):
        self.pack_forget()