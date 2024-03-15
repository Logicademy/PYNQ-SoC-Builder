import customtkinter as ctk
from tktooltip import ToolTip
import os
import application.xml_manager as xmlman

class Main_Menu(ctk.CTkFrame):
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

            proj_config = None
            # If the file exists, read the config from it.
            if os.path.exists(file_path.replace("\\", "/")):
                xmlmanager = xmlman.Xml_Manager(file_path)
                proj_config = xmlmanager.read_proj_config()

            print("Have I gotted called")
            if proj_config:
                print("Have I gotted set")

                # Set the variables
                try:
                    print("on" if proj_config['open_viv_gui'] else "off")
                    self.open_gui_var.set("on" if proj_config['open_viv_gui'] else "off")
                    if proj_config['open_viv_gui']:
                        print("Yes")
                        open_gui_check_box.select()
                    else:
                        print("No")
                        open_gui_check_box.deselect()
                except:
                    print("No Open GUI param in XML")
                
                try:
                    self.keep_gui_open_var.set("on" if proj_config['keep_viv_opn'] else "off")
                    if proj_config['keep_viv_opn']:
                        keep_gui_open_check_box.select()
                    else:
                        keep_gui_open_check_box.deselect()
                except:
                    print("No Keep Viv Open param in XML")
                
                try:
                    self.gen_jnb_var.set("on" if proj_config['gen_jnb'] else "off")
                    if proj_config['gen_jnb']:
                        gen_jnb_check_box.select()
                    else:
                        gen_jnb_check_box.deselect()
                except:
                    print("No Gen JNB param in XML")
                
                try:
                    self.use_testplan_var.set("on" if proj_config['use_tstpln'] else "off")
                    if proj_config['use_tstpln']:
                        use_testplan_check_box.select()
                    else:
                        use_testplan_check_box.deselect()
                except:
                    print("No Use Testplan param in XML")
                
                try:
                    self.use_io_var.set("on" if proj_config['use_board_io'] else "off")
                    if proj_config['use_board_io']:
                        use_io_check_box.select()
                    else:
                        use_io_check_box.deselect()
                except:
                    print("No Use Board IO param in XML")
                
                checkbox_event()

        entry_path = ctk.CTkEntry(row_1_frame, width=360, placeholder_text="To get started, browse for a .hdlgen project file")
        browse_button = ctk.CTkButton(row_1_frame, text="Browse", command=browse_files, width=100)
        entry_path.grid(row=1, column=0, padx=5, pady=5)
        browse_button.grid(row=1, column=1, padx=5, pady=5)

        ## Row 2
        # Select Mode
        mode_font = ("Segoe UI", 16)
        mode_label = ctk.CTkLabel(self.row_2_frame, text="Mode", font=mode_font, pady=5, width=20)

        self.mode_menu_options = ["Run All", "Generate Tcl", "Run Vivado", "Copy Bitstream", "Gen Jupyter Notebook"]
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
            # print("Checkbox toggled\topen GUI: ", self.open_gui_var.get())
            # print("\t\t\topen GUI: ", self.keep_gui_open_var.get())
            if self.open_gui_var.get() == "on":
                keep_gui_open_check_box.configure(state="normal")
            else:
                keep_gui_open_check_box.configure(state="disabled")

            if self.gen_jnb_var.get() == "on":
                use_testplan_check_box.configure(state="normal")
            else:
                use_testplan_check_box.configure(state="disabled")
            # self.app.checkbox_values = [self.open_gui_var.get(), self.keep_gui_open_var.get()]
            
            if self.use_io_var.get() == "on":
                configure_io_button.configure(state="normal")
            else:
                configure_io_button.configure(state="disabled")

            # Convert to true/false
            self.app.checkbox_values = [self.open_gui_var.get() == "on", self.keep_gui_open_var.get() == "on", self.gen_jnb_var.get() == "on", self.use_testplan_var.get() == "on", self.use_io_var.get() == "on"]


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
        self.open_gui_var = ctk.StringVar(value="on")
        open_gui_check_box = ctk.CTkCheckBox(viv_subframe, text="Open Vivado GUI", command=checkbox_event,
                                    variable=self.open_gui_var, onvalue="on", offvalue="off", width=140)
        open_gui_check_box.grid(row=0, column=0, pady=5, padx=5, sticky = 'nswe')

        self.keep_gui_open_var = ctk.StringVar(value="off")
        keep_gui_open_check_box = ctk.CTkCheckBox(viv_subframe, text="Keep Vivado Open", command=checkbox_event,
                                    variable=self.keep_gui_open_var, onvalue="on", offvalue="off", width=140)
        keep_gui_open_check_box.grid(row=1, column=0, pady=5, padx=5, sticky = 'nswe')


        # jnb subframe
        self.gen_jnb_var = ctk.StringVar(value="on")
        gen_jnb_check_box = ctk.CTkCheckBox(jnb_subframe, text="Generate JNB", command=checkbox_event,
                                    variable=self.gen_jnb_var, onvalue="on", offvalue="off", width=140, )
        gen_jnb_check_box.grid(row=0, column=0, pady=5, padx=5, sticky = 'nswe')

        self.use_testplan_var = ctk.StringVar(value="on")
        use_testplan_check_box = ctk.CTkCheckBox(jnb_subframe, text="Use Testplan", command=checkbox_event,
                                    variable=self.use_testplan_var, onvalue="on", offvalue="off", width=140)
        use_testplan_check_box.grid(row=1, column=0, pady=5, padx=5, sticky = 'nswe')

        # io subframe
        self.use_io_var = ctk.StringVar(value="on")
        use_io_check_box = ctk.CTkCheckBox(io_subframe, text="Use Board I/O", command=checkbox_event,
                                    variable=self.use_io_var, onvalue="on", offvalue="off", width=140)
        use_io_check_box.grid(row=0, column=0, pady=5, padx=5, sticky = 'nswe')

        def on_io_config_button():
            self.app.hdlgen_path = entry_path.get()
            if not os.path.isfile(entry_path.get()):
                self.app.top_level_message = "Error: Could not find HDLGen file at path specified"
                self.app.open_alert()
                return
            else:
                self.app.show_page(self.app.page3)


        # config = ctk.StringVar(value="on")
        configure_io_button = ctk.CTkButton(io_subframe, text="Configure I/O", command=on_io_config_button, width=140)
        configure_io_button.grid(row=1, column=0, pady=5, padx=5, sticky = 'nswe')

        ToolTip(open_gui_check_box, msg="Open Vivado GUI when executing automation steps", delay=0.5)
        ToolTip(keep_gui_open_check_box, msg="Keep Vivado GUI open once automation steps have completed", delay=0.5)
        ToolTip(gen_jnb_check_box, msg="Generate Jupyter Notebook file for project", delay=0.5)
        ToolTip(use_testplan_check_box, msg="Generate JNB to execute each individual test case", delay=0.5)
        ToolTip(use_io_check_box, msg="Enable to allow connection to PYNQ-Z2 I/O such as LEDs", delay=0.5)

        checkbox_event() # Calling to set default values

        ## Last Row
        def _on_run_button():
            self.app.mode = mode_dropdown.get()
            self.app.hdlgen_path = entry_path.get()
            
            # Check if HDLGen file exists - if not send message box and return from this func.
            if not os.path.isfile(entry_path.get()):
                self.app.top_level_message = "Error: Could not find HDLGen file at path specified"
                self.app.open_alert()
                return
            
            # Save the config
            proj_config = {
                "open_viv_gui": True if self.open_gui_var.get() == "on" else False,
                "keep_viv_opn": True if self.keep_gui_open_var.get() == "on" else False,
                "gen_jnb": True if self.gen_jnb_var.get() == "on" else False,
                "use_tstpln": True if self.use_testplan_var.get() == "on" else False,
                "use_board_io": True if self.use_io_var.get() == "on" else False
            }

            # Available Path entry_path.get().replace("\\", "/")
            try:
                xmlmanager = xmlman.Xml_Manager(self.app.hdlgen_path)
                xmlmanager.write_proj_config(proj_config)
            except Exception as e:
                print(f"Couldn't save config: {e}")
            
            
            # Run threaded program:
            # self.run_pynq_manager()
            proceed = self.app.page2.run_pynq_manager() # If false, abort.
            # HDLGen file exists:
            # Move to page two:
            if proceed:
                self.app.show_page(self.app.page2)
                self.app.root.geometry("500x580")
            else:
                # Do nothing
                pass

        # Go Button
        run_button = ctk.CTkButton(row_last_frame, text="Run", command=_on_run_button)
        run_button.grid(row=0, column=0, pady=5, padx=5)
        remote_button = ctk.CTkButton(row_last_frame, text="Remote Lab", command=self.app.open_remote_menu)
        remote_button.grid(row=0, column=1, pady=5, padx=5)

    

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
