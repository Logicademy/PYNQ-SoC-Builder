import customtkinter as ctk

class IO_Config_Page(ctk.CTkFrame):
    def __init__(self, app):
        ctk.CTkFrame.__init__(self, app.root)
        self.app = app       

        row_0_frame = ctk.CTkFrame(self, width=500, height=30, corner_radius=0)
        row_1_frame = ctk.CTkFrame(self, width=500, height=30)
        row_2_frame = ctk.CTkFrame(self, width=500, height=30)
        row_3_frame = ctk.CTkFrame(self, width=500, height=30)
        row_last_frame = ctk.CTkFrame(self, width=500, height=30)

        row_0_frame.grid(row=0, sticky="nsew")
        
        row_0_frame.columnconfigure(0, weight=1) # Centre title

        row_1_frame.columnconfigure(0, weight=1) # Centre all the buttons
        row_2_frame.columnconfigure(0, weight=1) 
        row_3_frame.columnconfigure(0, weight=1) 
        row_1_frame.columnconfigure(1, weight=1) 
        row_2_frame.columnconfigure(1, weight=1) 
        row_3_frame.columnconfigure(1, weight=1) 
        row_1_frame.columnconfigure(2, weight=1) 
        row_2_frame.columnconfigure(2, weight=1) 
        row_3_frame.columnconfigure(2, weight=1) 

        # This here is a just a 10 px vertical spacer. Can't use pady as that pads both N and S sides
        background_color = row_1_frame.cget("bg_color")
        spacer_frame = ctk.CTkFrame(self, height=10, fg_color=background_color,)
        spacer_frame.grid(row=1, column=0, sticky="ew")
        self.rowconfigure(1, weight=1)

        row_1_frame.grid(row=2, pady=5, ipadx=10)
        row_2_frame.grid(row=3, pady=5, ipadx=10)
        row_3_frame.grid(row=4, pady=5, ipadx=10)

        row_last_frame.grid(row=10, pady=10)

        ## Row 0
        # Title Label
        title_font = ("Segoe UI", 20, "bold") # Title font
        title_label = ctk.CTkLabel(row_0_frame, text="Configure Board I/O Connections", font=title_font, padx=10)
        title_label.grid(row=0, column=0, sticky="nsew")

        # title_label.bind("<Button-3>", self.on_right_button_title_label)

        def config_button_selected():
            pass

        # Row 1
        led_button = ctk.CTkButton(row_1_frame, text="LEDs", command=self.app.open_io_led_window, width=140)
        sw_btn_button = ctk.CTkButton(row_1_frame, text="Switches+Buttons", command=config_button_selected, width=140)
        clk_crypto_button = ctk.CTkButton(row_1_frame, text="Clock+Crypto", command=config_button_selected, width=140)
        led_button.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        sw_btn_button.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        clk_crypto_button.grid(row=0, column=2, padx=10, pady=5, sticky="nsew")

        ## Row 2
        arduino_button = ctk.CTkButton(row_2_frame, text="Arduino", command=config_button_selected, width=140)
        raspberry_pi_button = ctk.CTkButton(row_2_frame, text="Raspberry Pi", command=config_button_selected, width=140)
        pmod_button = ctk.CTkButton(row_2_frame, text="Pmod", command=config_button_selected, width=140)
        arduino_button.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        raspberry_pi_button.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        pmod_button.grid(row=0, column=2, padx=10, pady=5, sticky="nsew")

        # Row 3
        hdmi_button = ctk.CTkButton(row_3_frame, text="HDMI", command=config_button_selected, width=140)
        audio_button = ctk.CTkButton(row_3_frame, text="Audio", command=config_button_selected, width=140)
        analog_input_button = ctk.CTkButton(row_3_frame, text="Single Ended Analog", command=config_button_selected, width=140)
        hdmi_button.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        audio_button.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        analog_input_button.grid(row=0, column=2, padx=10, pady=5, sticky="nsew")

        # Disable all buttons that aren't available for now
        # led_button.configure(state="disabled")        # LED mode works.
        sw_btn_button.configure(state="disabled")
        clk_crypto_button.configure(state="disabled")
        arduino_button.configure(state="disabled")
        raspberry_pi_button.configure(state="disabled")
        pmod_button.configure(state="disabled")
        hdmi_button.configure(state="disabled")
        audio_button.configure(state="disabled")
        analog_input_button.configure(state="disabled")
        
        ## Last Row
        def on_return_button():
            # Saves should be taking place on each individual IO pop-up window.
            # Therefore no action required here, just to return.
            self.app.show_page(self.app.page1)
            self.app.root.geometry("500x240")

        return_button = ctk.CTkButton(row_last_frame, text="Return", command=on_return_button)
        return_button.grid(row=0, column=0, pady=5, padx=5)

    def show(self):
        self.pack()
    
    def hide(self):
        self.pack_forget()  