import customtkinter as ctk

class MyApp:
    def __init__(self, root):
        # Set Root
        self.root = root
        
        # Set Title
        self.root.title("PYNQ SoC Builder")

        # Shared Data...?
        self.shared_variable = ctk.StringVar()
        
        # Create and add pages to application
        self.page1 = Page1(self)
        self.page2 = Page2(self)

        # Show Inital Page
        self.show_page(self.page1)

    def show_page(self, page):
        # Hide all existing pages
        self.page1.hide()
        self.page2.hide()

        # Show request page:
        page.show()

class Page1(ctk.CTkFrame):
    def __init__(self, app):
        ctk.CTkFrame.__init__(self, app.root)
        self.app = app

        label = ctk.CTkLabel(self, text="Enter a value:")
        label.pack(pady=10)

        self.entry = ctk.CTkEntry(self, textvariable=self.app.shared_variable)
        self.entry.pack(pady=10)

        button = ctk.CTkButton(self, text="Next", command=self.go_to_page2)
        button.pack(pady=10)

    def go_to_page2(self):
        # Call the method in the app to switch to Page 2
        self.app.show_page(self.app.page2)

    def hide(self):
        self.pack_forget()

    def show(self):
        self.pack()

class Page2(ctk.CTkFrame):
    def __init__(self, app):
        ctk.CTkFrame.__init__(self, app.root)
        self.app = app

        label = ctk.CTkLabel(self, text="Value from Page 1:")
        label.pack(pady=10)

        # Display the shared variable on Page 2
        value_label = ctk.CTkLabel(self, textvariable=self.app.shared_variable)
        value_label.pack(pady=10)

        button = ctk.CTkButton(self, text="Back to Page 1", command=self.go_to_page1)
        button.pack(pady=10)

    def go_to_page1(self):
        # Call the method in the app to switch to Page 1
        self.app.show_page(self.app.page1)

    def hide(self):
        self.pack_forget()

    def show(self):
        self.pack()

if __name__ == "__main__":
    root = ctk.CTk()
    app = MyApp(root)
    root.mainloop()