import customtkinter as ctk
import os 
import threading
import time
import pynq_manager as pm

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class Application:

    def __init__(self, root):
        # Set root and title
        self.root = root
        self.root.title("PYNQ SoC Builder")
        self.root.geometry("500x240")

        # Shared Data Variable
        self.shared_var = ctk.StringVar()
        self.shared_mode_var = ctk.StringVar()
        self.shared_dir_var = ctk.StringVar()
        ## Shared variable does not need to be a ctk.Variable()
        self.mode = None
        self.hdlgen_path = None

        # Shared Variables for Messages
        self.top_level_message = None

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
            self.toplevel_window = ToplevelWindow(self) # Create window if None or destroyed
        else:
            self.toplevel_window.focus() # if window exists focus it.

class Page1(ctk.CTkFrame):
    def __init__(self, app):
        ctk.CTkFrame.__init__(self, app.root)
        self.app = app       

        row_0_frame = ctk.CTkFrame(self, width=500, height=30, corner_radius=0)
        row_1_frame = ctk.CTkFrame(self, width=500, height=30)
        row_2_frame = ctk.CTkFrame(self, width=500, height=30)
        row_3_frame = ctk.CTkFrame(self, width=500, height=30)
        row_last_frame = ctk.CTkFrame(self, width=500, height=30)

        row_0_frame.grid(row=0, sticky="nsew")
        row_0_frame.columnconfigure(0, weight=1) # Centre the row
        row_1_frame.grid(row=1, pady=5, padx=10)
        row_2_frame.grid(row=2)
        row_3_frame.grid(row=3)
        row_last_frame.grid(row=10)

        ## Row 0
        # Title Label
        title_font = ("Segoe UI", 20, "bold") # Title font
        title_label = ctk.CTkLabel(row_0_frame, text="PYNQ SoC Builder", font=title_font, padx=10)
        title_label.grid(row=0, column=0, sticky="nsew")

        ## Row 1
        # File path entry and browse button
        def browse_files():
            file_path = ctk.filedialog.askopenfilename(filetypes=[("HDLGen Files", "*.hdlgen")])
            entry_path.delete(0, ctk.END)
            entry_path.insert(0, file_path)
        entry_path = ctk.CTkEntry(row_1_frame, width=360)
        browse_button = ctk.CTkButton(row_1_frame, text="Browse", command=browse_files, width=100)
        entry_path.grid(row=1, column=0, padx=5, pady=5)
        browse_button.grid(row=1, column=1, padx=5, pady=5)

        ## Row 2
        # Select Mode
        mode_font = ("Segoe UI", 16)
        mode_label = ctk.CTkLabel(row_2_frame, text="Mode", font=mode_font, pady=5, width=20)

        self.mode_menu_options = ["Run All", "Generate Tcl", "Run Vivado", "Copy Bitstream", "Gen JNB /w Testplan", "Gen JNB w/o Testplan"]
        mode_menu_var = ctk.StringVar(self)
        mode_menu_var.set(self.mode_menu_options[0])

        def on_mode_dropdown(choice):
            # callback - not currently used
            pass

        mode_dropdown = ctk.CTkOptionMenu(row_2_frame, variable=mode_menu_var, values=self.mode_menu_options, command=on_mode_dropdown, width=150)
        mode_label.grid(row=2, column=0, pady=5, padx=10)
        mode_dropdown.grid(row=2, column=1, pady=5, padx=10)

        # Row 3
        ## Checkbox buttons and labels

        def checkbox_event():
            print("Checkbox toggled, current value: ", check_var.get())

        check_var = ctk.StringVar(value="on")
        check_box = ctk.CTkCheckBox(row_3_frame, text="Keep Vivado Open", command=checkbox_event,
                                    variable=check_var, onvalue="on", offvalue="off")
        check_box.pack()

        check_var2 = ctk.StringVar(value="on")
        check_box2 = ctk.CTkCheckBox(row_3_frame, text="Show Vivado GUI", command=checkbox_event,
                                    variable=check_var2, onvalue="on", offvalue="off")
        check_box2.pack()

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
            self.app.page2.run_pynq_manager()
            # HDLGen file exists:
            # Move to page two:
            self.app.show_page(self.app.page2)

        # Go Button
        run_button = ctk.CTkButton(row_last_frame, text="Run", command=_on_run_button)
        run_button.grid(row=0, column=0, pady=5)

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

        bottom_row_frame = ctk.CTkFrame(self, width=500, height=20)
        bottom_row_frame.grid(row=3, column=0, sticky="nsew")

        copy_to_clip_button = ctk.CTkButton(bottom_row_frame, width=150, text="Copy Log to Clipboard")
        force_quit_button = ctk.CTkButton(bottom_row_frame, width=150, text="Force Quit", fg_color="red3", hover_color="red4")
        bottom_row_frame.columnconfigure(1,weight=1)
        copy_to_clip_button.grid(row=0, column=0)
        force_quit_button.grid(row=0, column=1,sticky="e")

        

    def add_to_log_box(self, text):
        self.log_text_box.configure(state="normal")
        self.log_data += text
        self.log_text_box.delete("0.0", "end")  # delete all text
        self.log_text_box.insert("0.0", self.log_data) # repost all text
        self.log_text_box.configure(state="disabled")
        

    def run_pynq_manager(self):
        self.add_to_log_box(f"\nRunning in mode {self.app.mode} commencing at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}")    # time derivation could likely be easier.
        self.add_to_log_box(f"\nHDLGen Project: {self.app.hdlgen_path}")
        
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
            self.add_to_log_box("Not yet implemented in Pynq_Manager.py - API does not exist")
            pass

    def run_all(self):
        self.generate_tcl()
        self.run_vivado()
        self.copy_to_dir()
        self.generate_jnb()

    def generate_tcl(self):
        pm_obj = pm.Pynq_Manager(self.app.hdlgen_path)
        pm_obj.generate_tcl()

    def run_vivado(self):
        pm_obj = pm.Pynq_Manager(self.app.hdlgen_path)
        pm_obj.run_vivado()

    def copy_to_dir(self):
        pm_obj = pm.Pynq_Manager(self.app.hdlgen_path)
        pm_obj.copy_to_dir()

    def generate_jnb(self):
        pm_obj = pm.Pynq_Manager(self.app.hdlgen_path)
        pm_obj.generate_jnb()

    def show(self):
        self.pack()
    
    def hide(self):
        self.pack_forget()

class ToplevelWindow(ctk.CTkToplevel):
    def __init__(self, app):
        ctk.CTkToplevel.__init__(self, app.root)
        self.app = app
        # self.attributes('-topmost', 'true')

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

    # Show and Hide needed by all page classes
    def show(self):
        self.pack()
    
    def hide(self):
        self.pack_forget()

if __name__ == "__main__":
    root = ctk.CTk()
    app = Application(root)
    root.mainloop()