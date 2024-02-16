import customtkinter as ctk
import os 
import threading
import time
import pynq_manager as pm
import pyperclip

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class Application:

    def __init__(self, root):

        # Set root and title
        self.root = root
        self.root.title("PYNQ SoC Builder")
        self.root.geometry("500x240")
        self.root.resizable(False, False) # Dont let the window be resizable
        self.root.protocol("WM_DELETE_WINDOW", self.on_close) # Set function to handle close

        ## Shared variables (shared between pages)
        self.mode = None
        self.hdlgen_path = None
        self.checkbox_values = None

        # Shared Variables for Messages
        self.top_level_message = None
        self.dialog_response = None

        # Shared flags
        self.build_running = False              # If build process is running, this flag will be True
        self.subprocess_exit_signal = threading.Event()    # If force closed, threading.Event() used to signal close to running threads.

        # Shared Tcl Generator Flags
        self.skip_board_config = False

        # Initalise app pages
        self.page1 = Page1(self)        # Main Menu
        self.page2 = Page2(self)        # Page Showing progress
        # self.page3 = Page3(self)        # Possible we create a summary page later 

        # Show Inital Page
        self.show_page(self.page1)

        # Initalise attribute toplevel_window
        self.toplevel_window = None

    def show_page(self, page):
        # Hide all existing pages
        # Possible we should make this iterate thru all pages to hide (more dynamic)
        # Should be ok for this small application
        self.page1.hide()
        self.page2.hide()
        # self.page3.hide()
        page.show() # Show requested page.

    def open_alert(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = Alert_Window(self) # Create window if None or destroyed
        else:
            self.toplevel_window.focus() # if window exists focus it.
    
    def open_dialog(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = Dialog_Window(self) # Create window if None or destroyed
        else:
            self.toplevel_window.focus() # if window exists focus it.
        

    
    def on_close(self):
        # find a way to check if there are any threads running...should we set a flag??
        # build_running
        if self.build_running:
            # Prompt user if they are sure:
            self.top_level_message = "A build is currently running, quitting now might cause unexpected results or behaviour. Are you sure?"
            self.open_dialog()

            # Wait for the user to click their response
            self.toplevel_window.wait_window()

            print(self.dialog_response)
            response = self.dialog_response
            if response == "yes":
                # terminate process, by continuing past this if block
                pass
            elif response == "no":
                # leave and take no action
                return
            else:
                print("Invalid response from Dialog, not quitting (default)")
                return
        # Quit behaviour:
        print("Quitting application")
        self.root.destroy() # kill tkinter window
        exit()              # quit app

        

class Page1(ctk.CTkFrame):
    def __init__(self, app):
        ctk.CTkFrame.__init__(self, app.root)
        self.app = app       

        row_0_frame = ctk.CTkFrame(self, width=500, height=30, corner_radius=0)
        row_1_frame = ctk.CTkFrame(self, width=500, height=30)
        self.row_2_frame = ctk.CTkFrame(self, width=500, height=30)
        row_3_frame = ctk.CTkFrame(self, width=500)
        row_3_frame.grid_rowconfigure(0, weight=1)
        # row_3_frame.grid_rowconfigure(1, weight=1)
        row_3_frame.grid_columnconfigure(0, weight=1)
        row_3_frame.grid_columnconfigure(1, weight=1)
        row_3_frame.grid_columnconfigure(2, weight=1)
        row_3_frame.columnconfigure(0, weight=1)
        row_3_frame.columnconfigure(1, weight=1)
        row_3_frame.columnconfigure(2, weight=1)
        # self.rowconfigure(3, weight=1)
        self.columnconfigure(0,weight=1)
        # row_3_frame.rowconfigure(0, weight=1)
        # row_3_frame.rowconfigure(1, weight=1)
        # row_3_frame.rowconfigure(2, weight=1)
        row_4_frame = ctk.CTkFrame(self, width=500, height=30)
        row_last_frame = ctk.CTkFrame(self, width=500, height=30)

        row_0_frame.grid(row=0, sticky="nsew")
        row_0_frame.columnconfigure(0, weight=1) # Centre the row
        row_1_frame.grid(row=1, pady=15, padx=10)
        # self.row_2_frame.grid(row=2,pady=10)
        row_3_frame.grid(row=3, padx=5, ipady=5, sticky="nsew")
        # row_4_frame.grid(row=4, padx=5, pady=5)


        row_last_frame.grid(row=10, pady=15)

        ## Row 0
        # Title Label
        title_font = ("Segoe UI", 20, "bold") # Title font
        title_label = ctk.CTkLabel(row_0_frame, text="PYNQ SoC Builder", font=title_font, padx=10)
        title_label.grid(row=0, column=0, sticky="nsew")

        title_label.bind("<Button-3>", self.on_right_button_title_label)


        ## Row 1
        # File path entry and browse button
        def browse_files():
            file_path = ctk.filedialog.askopenfilename(filetypes=[("HDLGen Files", "*.hdlgen")])
            entry_path.delete(0, ctk.END)
            entry_path.insert(0, file_path)
        entry_path = ctk.CTkEntry(row_1_frame, width=360, placeholder_text="To get started, browse for a .hdlgen project file")
        browse_button = ctk.CTkButton(row_1_frame, text="Browse", command=browse_files, width=100)
        entry_path.grid(row=1, column=0, padx=5, pady=5)
        browse_button.grid(row=1, column=1, padx=5, pady=5)

        ## Row 2
        # Select Mode
        mode_font = ("Segoe UI", 16)
        mode_label = ctk.CTkLabel(self.row_2_frame, text="Mode", font=mode_font, pady=5, width=20)

        self.mode_menu_options = ["Run All", "Generate Tcl", "Run Vivado", "Copy Bitstream", "Gen JNB /w Testplan", "Gen JNB w/o Testplan"]
        mode_menu_var = ctk.StringVar(self)
        mode_menu_var.set(self.mode_menu_options[0])

        def on_mode_dropdown(choice):
            # callback - not currently used
            # self.app.top_level_message = "We wanna ask a question"
            # self.app.open_dialog()
            pass

        mode_dropdown = ctk.CTkOptionMenu(self.row_2_frame, variable=mode_menu_var, values=self.mode_menu_options, command=on_mode_dropdown, width=150)
        mode_label.grid(row=2, column=0, pady=5, padx=10)
        mode_dropdown.grid(row=2, column=1, pady=5, padx=10)

        # Row 3
        ## Checkbox buttons and labels
        def checkbox_event():
            # print("Checkbox toggled\topen GUI: ", open_gui_var.get())
            # print("\t\t\topen GUI: ", keep_gui_open_var.get())
            if open_gui_var.get() == "on":
                keep_gui_open_check_box.configure(state="normal")
            else:
                keep_gui_open_check_box.configure(state="disabled")

            if gen_jnb_var.get() == "on":
                use_testbench_check_box.configure(state="normal")
            else:
                use_testbench_check_box.configure(state="disabled")
            # self.app.checkbox_values = [open_gui_var.get(), keep_gui_open_var.get()]
            
            if scan_io_var.get() == "off":
                configure_io_button.configure(state="normal")
            else:
                configure_io_button.configure(state="disabled")

            # Convert to true/false
            self.app.checkbox_values = [open_gui_var.get() == "on", keep_gui_open_var.get() == "on", gen_jnb_var.get() == "on", use_testbench_var.get() == "on", scan_io_var.get() == "on"]

        # vivado config subframe
        viv_subframe = ctk.CTkFrame(row_3_frame, width=166)
        # jnb_subframe
        jnb_subframe = ctk.CTkFrame(row_3_frame, width=166)
        # io_subframe
        io_subframe = ctk.CTkFrame(row_3_frame, width=166)
        
        viv_subframe.grid(row=0, column=0)
        jnb_subframe.grid(row=0, column=1)
        io_subframe.grid(row=0, column=2)

        # Vivado config subframe
        open_gui_var = ctk.StringVar(value="on")
        open_gui_check_box = ctk.CTkCheckBox(viv_subframe, text="Open Vivado GUI", command=checkbox_event,
                                    variable=open_gui_var, onvalue="on", offvalue="off", width=140)
        open_gui_check_box.grid(row=0, column=0, pady=5, padx=5, sticky = 'nswe')

        keep_gui_open_var = ctk.StringVar(value="off")
        keep_gui_open_check_box = ctk.CTkCheckBox(viv_subframe, text="Keep Vivado Open", command=checkbox_event,
                                    variable=keep_gui_open_var, onvalue="on", offvalue="off", width=140)
        keep_gui_open_check_box.grid(row=1, column=0, pady=5, padx=5, sticky = 'nswe')


        # jnb subframe
        gen_jnb_var = ctk.StringVar(value="on")
        gen_jnb_check_box = ctk.CTkCheckBox(jnb_subframe, text="Generate JNB", command=checkbox_event,
                                    variable=gen_jnb_var, onvalue="on", offvalue="off", width=140, )
        gen_jnb_check_box.grid(row=0, column=0, pady=5, padx=5, sticky = 'nswe')

        use_testbench_var = ctk.StringVar(value="off")
        use_testbench_check_box = ctk.CTkCheckBox(jnb_subframe, text="Use Testbench", command=checkbox_event,
                                    variable=use_testbench_var, onvalue="on", offvalue="off", width=140)
        use_testbench_check_box.grid(row=1, column=0, pady=5, padx=5, sticky = 'nswe')

        # io subframe
        scan_io_var = ctk.StringVar(value="on")
        scan_io_check_box = ctk.CTkCheckBox(io_subframe, text="Scan I/O", command=checkbox_event,
                                    variable=scan_io_var, onvalue="on", offvalue="off", width=140)
        scan_io_check_box.grid(row=0, column=0, pady=5, padx=5, sticky = 'nswe')

        # config = ctk.StringVar(value="on")
        configure_io_button = ctk.CTkButton(io_subframe, text="Configure I/O", command=self.on_io_config_button, width=140)
        configure_io_button.grid(row=1, column=0, pady=5, padx=5, sticky = 'nswe')

        # run_button = ctk.CTkButton(row_last_frame, text="Run", command=_on_run_button)
        # run_button.grid(row=0, column=0, pady=5, padx=5)
        # ctk.CTkCheckBox(io_subframe, text="Use Testbench", command=checkbox_event,
        #                             variable=use_testbench_var, onvalue="on", offvalue="off")
        # use_testbench_check_box.grid(row=0, column=1, pady=5, padx=5)

        checkbox_event() # Calling to set default values

        # check_var3 = ctk.StringVar(value="on")
        # check_box3 = ctk.CTkCheckBox(row_3_frame, text="Show Vivado GUI", command=checkbox_event,
        #                             variable=check_var3, onvalue="on", offvalue="off")
        # check_box3.grid(row=0, column=2, pady=5, padx=5)


        ## Last Row
        def _on_run_button():
            self.app.mode = mode_dropdown.get()
            self.app.hdlgen_path = entry_path.get()
            
            # Check if HDLGen file exists - if not send message box and return from this func.
            if not os.path.isfile(entry_path.get()):
                self.app.top_level_message = "Error: Could not find HDLGen file at path specified"
                self.app.open_alert()
                return
            
            
            # Run threaded program:
            # self.run_pynq_manager()
            proceed = self.app.page2.run_pynq_manager() # If false, abort.
            # HDLGen file exists:
            # Move to page two:
            if proceed:
                self.app.show_page(self.app.page2)
                self.app.root.geometry("500x240")
            else:
                # Do nothing
                pass

        # Go Button
        run_button = ctk.CTkButton(row_last_frame, text="Run", command=_on_run_button)
        run_button.grid(row=0, column=0, pady=5, padx=5)

    def on_io_config_button(self):
        pass

    def on_right_button_title_label(self, arg):
        # Second argument provided is the button press event, eg: <ButtonPress event state=Mod1 num=3 x=141 y=12>
        # print(arg)
        if self.row_2_frame.winfo_ismapped():
            self.row_2_frame.grid_forget()
            self.app.root.geometry("500x240")
        else:
            self.row_2_frame.grid(row=2)
            self.app.root.geometry("500x280")


    def show(self):
        self.pack()
    
    def hide(self):
        self.pack_forget()

class Page2(ctk.CTkFrame):
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
        self.generate_tcl(False)
        self.run_vivado(False)
        self.copy_to_dir(False)
        self.generate_jnb(False)
        self.operation_completed()

    def generate_tcl(self, assert_complete=True):
        regenerate_bd = False # Default
        # start_gui = True 
        # keep_vivado_open = False

        # Checkbox_values shared variable is mapped as open_gui_var/keep_gui_open_var
        # self.app.checkbox_values = [open_gui_var.get(), keep_gui_open_var.get()]
        start_gui = self.app.checkbox_values[0]
        keep_vivado_open = self.app.checkbox_values[1]

        # Run check here, and run dialog:
        pm_obj = pm.Pynq_Manager(self.app.hdlgen_path)
        response = None
        if pm_obj.get_bd_exists:
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
        
        pm_obj.generate_tcl(regenerate_bd=regenerate_bd, start_gui=start_gui, keep_vivado_open=keep_vivado_open, skip_board_config=self.app.skip_board_config)
        if assert_complete:
            self.operation_completed()

    def run_vivado(self, assert_complete=True):
        pm_obj = pm.Pynq_Manager(self.app.hdlgen_path)
        pm_obj.run_vivado()
        self.operation_completed()

    def copy_to_dir(self, assert_complete=True):
        pm_obj = pm.Pynq_Manager(self.app.hdlgen_path)
        pm_obj.copy_to_dir()
        if assert_complete:
            self.operation_completed()

    def generate_jnb(self, assert_complete=True):
        generate_jnb = self.app.checkbox_values[2]
        use_testbench = self.app.checkbox_values[3]
        generic = not use_testbench

        if not generate_jnb:
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

    

class Alert_Window(ctk.CTkToplevel):
    def __init__(self, app):
        ctk.CTkToplevel.__init__(self, app.root)
        self.app = app
        # self.attributes('-topmost', 'true')
        self.title("Alert")
        self.grab_set() # This makes the pop-up the primary window and doesn't allow interaction with main menu
        self.geometry("300x100")
        icon_font = ("Segoe Fluent Icons Regular", 80)
        self.resizable(False, False) # Dont let the window be resizable
        
        self.left_frame = ctk.CTkFrame(self, width=100, height=100)
        self.right_frame = ctk.CTkFrame(self, width=200, height=100)

        self.label = ctk.CTkLabel(self.left_frame, text="\uedae", font=icon_font, width=100, height=100)
        self.label.pack()

        self.error_text = "\n"+self.app.top_level_message
        self.msglabel = ctk.CTkLabel(self.right_frame, text=self.error_text, width=200, height=100, wraplength=180, anchor="n")
        self.msglabel.pack()
        
        self.left_frame.grid(column=0, row=0)
        self.right_frame.grid(column=1, row=0)


class Dialog_Window(ctk.CTkToplevel):
    def __init__(self, app):
        ctk.CTkToplevel.__init__(self, app.root)
        self.app = app
        self.title("Dialog")
        self.grab_set() # This makes the pop-up the primary window and doesn't allow interaction with main menu
        self.geometry("300x140")
        icon_font = ("Segoe Fluent Icons Regular", 80)
        self.resizable(False, False) # Dont let the window be resizable
        
        self.left_frame = ctk.CTkFrame(self, width=100, height=100)
        self.right_frame = ctk.CTkFrame(self, width=200, height=100)
        self.button_frame = ctk.CTkFrame(self, width=300, height=50)

        self.label = ctk.CTkLabel(self.left_frame, text="\uf142", font=icon_font, width=100, height=100)
        self.label.pack()

        self.question = "\n"+self.app.top_level_message
        self.msglabel = ctk.CTkLabel(self.right_frame, text=self.question, width=200, height=100, wraplength=180, anchor="n")
        self.msglabel.pack()
        

        def _on_yes_button():
            # set var
            # close window
            self.app.dialog_response = "yes"
            self.destroy()

        def _on_no_button():
            # set var
            # close window
            self.app.dialog_response = "no"
            self.destroy()  

        self.button_frame = ctk.CTkFrame(self, width=300, height=50)
        self.yes_button = ctk.CTkButton(self.button_frame, text="Yes", command=_on_yes_button)
        self.yes_button.grid(row=0, column=0, pady=5, padx=5)
        self.no_button = ctk.CTkButton(self.button_frame, text="No", command=_on_no_button)
        self.no_button.grid(row=0, column=1, pady=5, padx=5)

        self.left_frame.grid(column=0, row=0)
        self.right_frame.grid(column=1, row=0)
        self.button_frame.grid(column=0, row=1, columnspan=2)



if __name__ == "__main__":
    root = ctk.CTk()
    app = Application(root)
    root.mainloop()