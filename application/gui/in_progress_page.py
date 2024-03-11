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

        # Shared Variable:
        self.current_running_mode = None    # Used by logger thread to know what process is running

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
        self.synthesis_log_data = ""
        # scrolling_label = ctk.CTkLabel(row_1_scrollable_frame, text=log_data, wraplength=480, anchor="e")
        self.scrolling_entry_variable = ctk.StringVar()
        self.scrolling_entry_variable.set(self.log_data)
        
        row_1_frame = ctk.CTkFrame(self,width=500, height=30)
        row_1_frame.grid(row=1, column=0, sticky="nsew")

        self.log_text_box = ctk.CTkTextbox(row_1_frame, width=500, height=170, corner_radius=0)
        self.log_text_box.insert("0.0", self.log_data)
        self.log_text_box.configure(state="disabled")
        self.log_text_box.grid(row=0, column=0)

        self.synthesis_log_text_box = ctk.CTkTextbox(row_1_frame, width=500, height=170, corner_radius=0)
        self.synthesis_log_text_box.insert("0.0", self.log_data)
        self.synthesis_log_text_box.configure(state="disabled")
        self.synthesis_log_text_box.grid(row=1, column=0)

        row_2_frame = ctk.CTkFrame(self,width=500, height=30)
        row_2_frame.grid(row=2, column=0, sticky="nsew")

        self.progress_bar = ctk.CTkProgressBar(row_2_frame, progress_color="green", orientation="horizontal", width=500, height=10, corner_radius=0)
        self.progress_bar.pack()
        self.progress_bar.stop()

        bottom_row_frame = ctk.CTkFrame(self, width=500, height=20)
        bottom_row_frame.grid(row=3, column=0, sticky="nsew")

        copy_to_clip_button = ctk.CTkButton(bottom_row_frame, width=150, text="Copy Log to Clipboard", command=self.copy_logs_to_clip)
        self.force_quit_button = ctk.CTkButton(bottom_row_frame, width=150, text="Force Quit", fg_color="red3", hover_color="red4", command=self.app.on_close)
        self.go_back_complete_button = ctk.CTkButton(bottom_row_frame, width=150, text="OK", fg_color="green3", hover_color="green4", command=self.on_return_button)
        
        bottom_row_frame.columnconfigure(1,weight=1)
        copy_to_clip_button.grid(row=0, column=0)
        self.force_quit_button.grid(row=0, column=1,sticky="e")

    def copy_logs_to_clip(self):
        pyperclip.copy(self.log_data)

    def add_to_log_box(self, text):
        self.log_text_box.configure(state="normal")
        self.log_data += text
        self.log_text_box.delete("0.0", "end")  # delete all text
        self.log_text_box.insert("0.0", self.log_data) # repost all text
        self.log_text_box.configure(state="disabled")
            # Get the last line index
        last_line_index = self.log_text_box.index('end-1c linestart')
        # Scroll to the last line
        self.log_text_box.see(last_line_index)

    def add_to_synthesis_log_box(self, text):
        self.synthesis_log_text_box.configure(state="normal")
        self.synthesis_log_data += text
        self.synthesis_log_text_box.delete("0.0", "end")  # delete all text
        self.synthesis_log_text_box.insert("0.0", self.synthesis_log_data) # repost all text
        self.synthesis_log_text_box.configure(state="disabled")
        # Get the last line index
        last_line_index = self.synthesis_log_text_box.index('end-1c linestart')
        # Scroll to the last line
        self.synthesis_log_text_box.see(last_line_index)

    def run_pynq_manager(self):

        # Find Vivado log file and delete it.
        try:
            os.remove(os.path.join(os.getcwd(), "vivado.log"))
            print("Successfully deleted Vivado.log file")
        except FileNotFoundError:
            print("No vivado.log file to delete")
        except Exception as e:
            print(f"An error occured: {e}")
        # Find Vivado jou file and delete it.
        try:
            os.remove(os.path.join(os.getcwd(), "vivado.jou"))
            print("Successfully deleted Vivado.jou file")
        except FileNotFoundError:
            print("No vivado.jou file to delete")
        except Exception as e:
            print(f"An error occured: {e}")

        self.add_to_log_box(f"\n\nRunning in mode {self.app.mode} commencing at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}")
        self.add_to_log_box(f"\nHDLGen Project: {self.app.hdlgen_path}")
        self.progress_bar.configure(mode="indeterminate", indeterminate_speed=0.4)
        self.progress_bar.start()

        pm_obj = pm.Pynq_Manager(self.app.hdlgen_path)
        pm_obj.get_board_config_exists()
        
        # Set up the logging thread
        # The logger will need to know: 
        #   - the current stage
        #   - if in vivado mode, the log file
        self.syn_log_path = "C:/repo/HDLGen-ChatGPT-Latest/User_Projects/ToLuke/FIFOs/FIFO4x64Top/VHDL/AMDprj/FIFO4x64Top.runs/synth_1/runme.log"
        syn_thread = threading.Thread(target=self.run_synthesis_logger)
        # syn_thread.start()
        logger_thread = threading.Thread(target=self.run_logger)
        logger_thread.start()   # Start the logger thread

        # Execute Program
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
        
        self.app.build_running = True
        return True

    def run_logger(self):
        # This is the logger function, it will be run on it's own thread and be responsible for updating the log window.
        #   Variables:
        #       - self.add_to_log_box(string) -> Updates the log box
        
        # Function Steps:
        #   1) Whilst the build_running flag is false, we wait. (Run logger called before program commences)
        #   2) When program starts, we move to main loop of the logger.
        #   3) 

        i = 0
        j = 0
        while not self.app.build_running:
            i += 1
            # run_logger thread is called before the application starts, therefore we wait.
            # We check if build has started every tenth of a second, only posting a message every 1 second.
            # All modules (except the run vivado) will simply access the "add to log box" api themselves.
            # Only Vivado run will use this thread to print relevant messages.

            if i > 10:
                i -= 10
                self.add_to_log_box("\nWaiting for build to start...")
            time.sleep(0.1)

        while self.app.build_running:
            
            # Main logger loop
            if self.current_running_mode == "gen_tcl":
                # self.add_to_log_box("\nGenerating Tcl Script for Vivado")
                # Generate Tcl File Mode
                pass
            elif self.current_running_mode == "run_viv":
                # self.add_to_log_box("\nExecuting Tcl Script in Vivado")
                # Here we need to search for the various triggers
                # Run Vivado Mode
                vivado_log_path = os.path.join(os.getcwd(), "vivado.log")

                while not os.path.exists(vivado_log_path):
                    self.add_to_log_box("\nWaiting for Vivado to launch...")
                    time.sleep(1)



                with open(vivado_log_path, 'r') as file:
                    while True:
                        line = file.readline()
                        if not line:
                            # End of file reached, wait for the next line to become available
                            time.sleep(1)  # Adjust the sleep duration as needed
                        else:
                            # Process the line as needed
                            # Look for specific indicators of whats happening.
                            # line
                            if line == "":
                                pass
                                # Protection for the next check, if empty string, skip.
                                # continue  - we dont need this to continue cos it'll infinite loop
                            elif line[0] == "#":
                                pass
                                # If line starts with #, its from sourced file and we dont care.
                                # continue
                            elif "open_project" in line:
                                self.add_to_log_box("\nOpening Vivado Project")
                                self.add_to_log_box("\n"+line)
                            elif "create_bd_design" in line:
                                self.add_to_log_box("\nCreate BD Design")
                                self.add_to_log_box("\n"+line)
                            elif "_0_0_synth_1" in line:
                                self.add_to_log_box("\nStarting synthesis")
                                self.add_to_log_box("\n"+line)
                            elif "Launched impl_1..." in line:
                                self.add_to_log_box("\nLaunching Implementation")
                                self.add_to_log_box("\n"+line)
                                self.add_to_log_box("\nSee nextline for log path:")
                                self.add_to_log_box(file.readline())
                            elif "Waiting for impl_1 to finish..." in line:
                                self.add_to_log_box("\nWaiting for impl_1 to finish...see impl log tab for more details.")
                                time.sleep(1)
                            elif "write_bitstream completed successfully" in line:
                                self.add_to_log_box("\nBitstream written successfully.")
                            elif "exit" in line:
                                self.add_to_log_box("\nExit command issued to Vivado. Waiting for Vivado to close.")
                                # Stall the process until the flag is updated by other thread.
                                while self.app.build_running:
                                    time.sleep(1)
                                    pass
                                break
                            if self.current_running_mode != "run_viv":
                                    break
                            if self.app.vivado_force_quit_event and self.app.vivado_force_quit_event.is_set():
                                print("Quitting logger due to quit event.")
                                break
            elif self.current_running_mode == "cpy_dir":
                # To be handled by copy_dir API
                # self.add_to_log_box("\nCopying Bitstream to <project>/PYNQBuild/output folder")
                # Copy to Directory Mode
                pass
            elif self.current_running_mode == "gen_jnb":
                # To be handled by copy_dir API
                # self.add_to_log_box("\nGenerating Jupyter Notebook")
                # Generate Jupyter Notebook Mode
                pass
            elif self.current_running_mode == None:
                # This mode should never be possible reach.
                self.add_to_log_box("\nBuild Idle.")
                pass
            else:
                self.add_to_log_box("\nError: Unaccessible code section reached")
                pass
            time.sleep(1)    

        # Finally section
        # Run any closing code: Perhaps print a summary to the log.
        self.add_to_log_box("\n\n===== Summary =====\nTime to build: MM:SS\netc.etc.etc.")
        return

    def run_synthesis_logger(self):
        path_to_log = self.syn_log_path
        self.quit_synthesis_logger = False
        waiting_counter = 0

        while not os.path.exists(path_to_log):
            if waiting_counter % 6 == 0:    # Print every three seconds
                self.add_to_synthesis_log_box("\nWaiting for synthesis job to start")
            time.sleep(0.5)
            waiting_counter += 1
            if self.quit_synthesis_logger:
                self.add_to_synthesis_log_box("\nQuit Synthesis Logger Asserted...stopping.")
                return

        with open(path_to_log, 'r') as file:
            while True:
                line = file.readline()
                if not line:
                    time.sleep(1)   # No line in buffer, wait 1 sec and read again
                else:
                    # Handle line
                    if line == "":
                        time.sleep(0.5)  # Wait 0.5 seconds just to stop infinite loop
                        continue        # If blank line, just skip to next line
                    else:
                        self.add_to_synthesis_log_box("\n" + line)
                
                if self.app.vivado_force_quit_event and self.app.vivado_force_quit_event.is_set():
                    print("Quitting synthesis due to quit event.")
                    break
                elif not self.app.build_running:
                    print("Quitting synthesis due to quit event.")
                    break


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

        # Setting mode for the logger thread
        self.current_running_mode = "gen_tcl"

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

            # print(self.app.dialog_response)
            response = self.app.dialog_response
            if response == "yes":
                regenerate_bd = True
            elif response == "no":
                regenerate_bd = False
            else:
                print("Invalid response from Dialog, regenerate_bd = False (default)")
        
        pm_obj.generate_tcl(regenerate_bd=regenerate_bd, start_gui=start_gui, keep_vivado_open=keep_vivado_open, skip_board_config=self.app.skip_board_config, io_map=io_map, gui_app=self)
        
        if assert_complete:
            self.operation_completed()

    def run_vivado(self, assert_complete=True):
        # Setting mode for the logger thread
        self.current_running_mode = "run_viv"

        print("Inprogress: Starting Vivado")
        pm_obj = pm.Pynq_Manager(self.app.hdlgen_path)
        pm_obj.run_vivado(self.app.vivado_force_quit_event)
        print("In progress vivado ended")
        # time.sleep(0.1)

        time.sleep(0.1)


        # new_thread = multiprocessing.Process(target=pm_obj.run_vivado)
        # new_thread.start()

        # while pm_obj.get_vivado_running:
        #     time.sleep(0.5)
        #     print("Vivado is running...")

        if assert_complete:
            self.operation_completed()

    def copy_to_dir(self, assert_complete=True):
        # Setting mode for the logger thread
        self.current_running_mode = "cpy_dir"

        pm_obj = pm.Pynq_Manager(self.app.hdlgen_path)
        res = pm_obj.copy_to_dir()
        if not res:
            self.app.top_level_message = "Could not find .bit file - Please see Vivado logs for information"
            self.app.open_alert()
        if assert_complete:
            self.operation_completed()

    def generate_jnb(self, assert_complete=True):
        # Setting mode for the logger thread
        self.current_running_mode = "gen_jnb"

        generate_jnb = self.app.checkbox_values[2]
        use_testplan = self.app.checkbox_values[3]
        generic = not use_testplan

        if generate_jnb:
            pm_obj = pm.Pynq_Manager(self.app.hdlgen_path)
            pm_obj.generate_jnb(generic=generic)
        
        if assert_complete:
            self.operation_completed()

    def operation_completed(self):
        # Setting mode for the logger thread back to default
        self.current_running_mode = None

        self.force_quit_button.grid_forget()
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
        self.go_back_complete_button.grid_forget()  # Hide the button
        self.force_quit_button.grid(row=0, column=1,sticky="e")
    
    def hide(self):
        self.pack_forget()