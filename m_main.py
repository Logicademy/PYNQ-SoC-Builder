import customtkinter as ctk
import application.new_gui.main_menu as main_menu

class Application:

    def __init__(self, root):

        # Set root and title
        self.root = root
        self.root.title("PYNQ SoC Builder")
        self.root.geometry("1200x800")

        self.root.minsize(800, 500)
        # self.root.resizable(False, False) # Dont let the window be resizable
        # self.root.protocol("WM_DELETE_WINDOW", self.on_close) # Set function to handle close

        self.page1 = main_menu.MainPage(self)
        # self.page2 = etc(self)

        self.show_page(self.page1)

    def get_window_height(self):
        # Wait for the window to be displayed and its size to be finalized
        self.root.update_idletasks()
        self.root.update()
        return self.root.winfo_height()
    
    def get_window_width(self):
        # Wait for the window to be displayed and its size to be finalized
        self.root.update_idletasks()
        self.root.update()
        return self.root.winfo_width()

    def show_page(self, page):
        # Hide all existing pages
        self.page1.hide()
        # self.page2.hide()
        # self.page3.hide()
        page.show() # Show requested page.

# Launch Application
if __name__ == "__main__":
    root = ctk.CTk()
    app = Application(root)
    root.mainloop()