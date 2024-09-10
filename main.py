import customtkinter as ctk
import application.gui.main_menu as main_menu
import application.gui.popups as popups
import application.gui.open_project as openproj
import threading
import git
import os
import subprocess
import sys
class Application:

    ##############################
    ##### Set Up Application #####
    ##############################
    def __init__(self, root):

        # Set root and title
        self.root = root
        self.root.title("PYNQ SoC Builder")
        self.root.geometry("1200x800")

        self.root.minsize(800, 500)
        # self.root.resizable(False, False) # Dont let the window be resizable
        # self.root.protocol("WM_DELETE_WINDOW", self.on_close) # Set function to handle close

        # Shared Variables (Shared between all pages)
        # self.build_running = False      # Flag - True build is running, False build not running
        # self.build_force_quit_event = threading.Event()     # Event to trigger Build threads to quit
        self.dialog_response = None     # Stores response from Dialog Pop-Up
        self.top_level_message = None   # Set top_level_message to be presented by dialog/alert
        self.toplevel_window = None    # Var for top level window objects
        self.hdlgen_path = None         # Current Project
        self.hdlgen_prj = None          # Current Project Object
        self.path_to_markdown = None    # Path to markdown file.

        self.page1 = main_menu.MainPage(self)
        self.page2 = openproj.OpenProjectPage(self)

        self.show_page(self.page2)

    #####################################
    ##### Return Application Height #####
    #####################################
    def get_window_height(self):
        # Wait for the window to be displayed and its size to be finalized
        self.root.update_idletasks()
        self.root.update()
        return self.root.winfo_height()

    ####################################
    ##### Return Application Width #####
    ####################################
    def get_window_width(self):
        # Wait for the window to be displayed and its size to be finalized
        self.root.update_idletasks()
        self.root.update()
        return self.root.winfo_width()

    #####################
    ##### Show Page #####
    #####################
    def show_page(self, page):
        # Hide all existing pages
        self.page1.hide()
        self.page2.hide()
        # self.page3.hide()
        page.show() # Show requested page.


    # TODO: Instead of individual functions here we can have a "Open Popup(popups.Alert_Window)" API where any popup class can be passed
    #           Not really a priority by any means. Just a clean up task.
    #############################
    ##### Open Alert Pop-Up #####
    #############################
    def open_alert(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = popups.Alert_Window(self) # Create window if None or destroyed
        else:
            self.toplevel_window.focus() # if window exists focus it.

    ###################################
    ##### Open Launch FPGA Pop-Up #####
    ###################################
    def open_fpga_popup(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = popups.FPGA_Window(self) # Create window if None or destroyed
        else:
            self.toplevel_window.focus() # if window exists focus it.

    ################################
    ##### Open Markdown Pop-Up #####
    ################################
    def open_markdown(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = popups.MarkdownWindow(self) # Create window if None or destroyed
            self.toplevel_window.focus() # Focus the window aswell.
        else:
            self.toplevel_window.focus() # if window exists focus it.
    
    ##############################
    ##### Open Dialog Pop-Up #####
    ##############################
    def open_dialog(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = popups.Dialog_Window(self) # Create window if None or destroyed
        else:
            self.toplevel_window.focus() # if window exists focus it.

    #####################################
    ##### Close Application Handler #####
    #####################################
    def close_application(self):
        # Is a build currently running?
        if self.hdlgen_prj.build_running:
            # Prompt user if they are sure:
            self.top_level_message = "A build is currently running and will force quit. Are you sure?"
            self.open_dialog()

            # Wait for the user to click their response
            self.toplevel_window.wait_window()

            # print(self.dialog_response)
            response = self.dialog_response
            if response == "yes":
                # terminate process, by continuing past this if block
                self.hdlgen_prj.build_force_quit_event.set()
                pass
            elif response == "no":
                # leave and take no action
                return
            else:
                print("Invalid response from Dialog, not quitting (default)")
                return
        # Quit behaviour:
        print("Closing Application")
        self.root.destroy()     # kill tkinter window
        exit()                  # quit app


#######################################
##### Launch Application Function #####
#######################################
if __name__ == "__main__":
    root = ctk.CTk()
    ctk.deactivate_automatic_dpi_awareness()
    app = Application(root)


    repo = git.Repo(os.getcwd())
    
    # Get the active branch
    current_branch = repo.active_branch
    print(f"Current branch: {current_branch}")

    try:
        if current_branch.name == "master":    # Temporarily changed to auto_updater for testing purposes 
            # Fetch updates from the remote
            # Configure remote URL with credentials (for HTTPS)
            repo.remotes.origin.set_url("https://github.com/Logicademy/PYNQ-SoC-Builder.git")
            origin = repo.remotes.origin
            origin.fetch()

            # Compare local and remote commits
            local_commit = repo.head.commit  # Local commit
            remote_commit = repo.refs['origin/master'].commit  # Remote branch's commit

            print(f"Local Hash: {local_commit.hexsha}")
            print(f"Local Commit: {local_commit}")
            print(f"Remote Commit: {remote_commit}")

            if local_commit.hexsha != remote_commit.hexsha:
                print("New commits are available!")
                # Launch User Prompt
                app.top_level_message = "An update is available, would you like to install it?"
                app.open_dialog()
                app.toplevel_window.wait_window() # Wait for user's response
            else:
                print("Your branch is up-to-date.")

            if app.dialog_response == "yes":
                origin.pull()
                # Step 2: Restart the application
                print("Restarting the application with updated code...")
                #time.sleep(2)  # Optional: delay to show messages or log to a file

                # Use subprocess to start a new process
                new_process = subprocess.Popen([sys.executable] + sys.argv)

                # Optional: Log the new process ID
                print(f"Started new process with PID: {new_process.pid}")
                
                # Step 3: Exit the current process
                sys.exit()

            else:
                print("Skipping update, running application...")

    except Exception as e:
        print(f"Could not auto-update project, please do manually or re-clone from Github.com/Logicademy/PYNQ-SoC-Builder - {e}")

    root.mainloop()