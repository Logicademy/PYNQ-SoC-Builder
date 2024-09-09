import xml.dom.minidom
import os
import re
import application.xml_manager as xmlman
from application.config import *
# tcl_generator.py
# This Python 3 script is responsible for generating a Tcl script file dynamically depending on the project.

# Author: Luke Canny
# Date: 12/10/23


# Run this in the Vivado Tcl Command Line
# source C:/masters/masters_automation/generate_script.tcl

# In Windows CMD:
# D:\Xilinx\Vivado\2019.1\bin\vivado.bat -mode tcl -source C:/masters/masters_automation/generate_script.tcl
# /path/to/vivado/bat -mode tcl -source /path/to/generate_script.tcl


# New Notes for New Feature:
# Tcl commands to create external connection and to rename the connection
# startgroup
# make_bd_pins_external  [get_bd_pins CB4CLED_0/count]
# endgroup
# connect_bd_net [get_bd_pins count/gpio_io_i] [get_bd_pins CB4CLED_0/count]
# set_property name NEWNAME [get_bd_ports count_0]
# dunno what makegroup does but no need worry about it


# set_property {STEPS.SYNTH_DESIGN.ARGS.MORE OPTIONS} {} [get_runs synth_1]
# reset_run synth_1


# ---- I/O Mapping Info ---- 
# Current mapping scheme looks for _led suffix on (non-internal) signals.
# _led0 - Map to LED 0 on board
# _led1 - Map to LED 1 on board
# _led2 - Map to LED 2 on board
# _led3 - Map to LED 3 on board
#
# _led - Automatic mapping.
# _led13 - Maps signal to LEDs 1, 2, 3
io_suffix = ["_led", "_led0", "_led1", "_led2", "_led3", "_led01", "_led02", "_led03", "_led12", "_led13", "_led23", "_led3"]

pynq_constraints = {
    # clock
    "clock": "set_property -dict { PACKAGE_PIN H16   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];\ncreate_clock -add -name signal_name_pin -period 8.00 -waveform {0 4} [get_ports { signal_name }];",
    # switches
    "sw0": "set_property -dict { PACKAGE_PIN M20   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "sw1": "set_property -dict { PACKAGE_PIN M19   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",

    # RGB LEDs
    "led4_b": "set_property -dict { PACKAGE_PIN L15   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "led4_g": "set_property -dict { PACKAGE_PIN G17   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "led4_r": "set_property -dict { PACKAGE_PIN N15   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "led5_b": "set_property -dict { PACKAGE_PIN G14   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "led5_g": "set_property -dict { PACKAGE_PIN L14   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "led5_r": "set_property -dict { PACKAGE_PIN M15   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",

    # LEDs
    "led0": "set_property -dict { PACKAGE_PIN R14   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "led1": "set_property -dict { PACKAGE_PIN P14   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "led2": "set_property -dict { PACKAGE_PIN N16   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "led3": "set_property -dict { PACKAGE_PIN M14   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",

    # Buttons
    "btn0": "set_property -dict { PACKAGE_PIN D19   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "btn1": "set_property -dict { PACKAGE_PIN D20   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "btn2": "set_property -dict { PACKAGE_PIN L20   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "btn3": "set_property -dict { PACKAGE_PIN L19   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",

    # PmodA
    "ja0": "set_property -dict { PACKAGE_PIN Y18   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "ja1": "set_property -dict { PACKAGE_PIN Y19   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "ja2": "set_property -dict { PACKAGE_PIN Y16   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "ja3": "set_property -dict { PACKAGE_PIN Y17   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "ja4": "set_property -dict { PACKAGE_PIN U18   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "ja5": "set_property -dict { PACKAGE_PIN U19   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "ja6": "set_property -dict { PACKAGE_PIN W18   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "ja7": "set_property -dict { PACKAGE_PIN W19   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",


    #PmodB
    "jb0": "set_property -dict { PACKAGE_PIN W14   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "jb1": "set_property -dict { PACKAGE_PIN Y14   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "jb2": "set_property -dict { PACKAGE_PIN T11   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "jb3": "set_property -dict { PACKAGE_PIN T10   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "jb4": "set_property -dict { PACKAGE_PIN V16   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "jb5": "set_property -dict { PACKAGE_PIN W16   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "jb6": "set_property -dict { PACKAGE_PIN V12   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "jb7": "set_property -dict { PACKAGE_PIN W13   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",

    #Audio 
    "adr0": "set_property -dict { PACKAGE_PIN M17   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "adr1": "set_property -dict { PACKAGE_PIN M18   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",

    "au_mclk_r": "set_property -dict { PACKAGE_PIN U5    IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "au_sda_r": "set_property -dict { PACKAGE_PIN T9    IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "au_scl_r": "set_property -dict { PACKAGE_PIN U9    IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "au_dout_r": "set_property -dict { PACKAGE_PIN F17   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "au_din_r": "set_property -dict { PACKAGE_PIN G18   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "au_wclk_r": "set_property -dict { PACKAGE_PIN T17   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "au_bclk_r": "set_property -dict { PACKAGE_PIN R18   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",


    # Single Ended Analog Inputs
    #NOTE: The ar_an_p pins can be used as single ended analog inputs with voltages from 0-3.3V (Arduino Analog pins a[0]-a[5]). 
    #      These signals should only be connected to the XADC core. When using these pins as digital I/O, use pins a[0]-a[5].
    "ar_an0_p": "set_property -dict { PACKAGE_PIN E17   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "ar_an0_n": "set_property -dict { PACKAGE_PIN D18   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "ar_an1_p": "set_property -dict { PACKAGE_PIN E18   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "ar_an1_n": "set_property -dict { PACKAGE_PIN E19   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "ar_an2_p": "set_property -dict { PACKAGE_PIN K14   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "ar_an2_n": "set_property -dict { PACKAGE_PIN J14   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "ar_an3_p": "set_property -dict { PACKAGE_PIN K16   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "ar_an3_n": "set_property -dict { PACKAGE_PIN J16   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "ar_an4_p": "set_property -dict { PACKAGE_PIN J20   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "ar_an4_n": "set_property -dict { PACKAGE_PIN H20   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "ar_an5_p": "set_property -dict { PACKAGE_PIN G19   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "ar_an5_n": "set_property -dict { PACKAGE_PIN G20   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",

    #Arduino Digital I/O 
    "ar0": "set_property -dict { PACKAGE_PIN T14   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "ar1": "set_property -dict { PACKAGE_PIN U12   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "ar2": "set_property -dict { PACKAGE_PIN U13   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "ar3": "set_property -dict { PACKAGE_PIN V13   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "ar4": "set_property -dict { PACKAGE_PIN V15   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "ar5": "set_property -dict { PACKAGE_PIN T15   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "ar6": "set_property -dict { PACKAGE_PIN R16   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "ar7": "set_property -dict { PACKAGE_PIN U17   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "ar8": "set_property -dict { PACKAGE_PIN V17   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "ar9": "set_property -dict { PACKAGE_PIN V18   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "ar10": "set_property -dict { PACKAGE_PIN T16   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "ar11": "set_property -dict { PACKAGE_PIN R17   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "ar12": "set_property -dict { PACKAGE_PIN P18   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "ar13": "set_property -dict { PACKAGE_PIN N17   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "a": "set_property -dict { PACKAGE_PIN Y13   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",

    #Arduino Digital I/O On Outer Analog Header
    #NOTE: These pins should be used when using the analog header signals A0-A5 as digital I/O 
    "a0": "set_property -dict { PACKAGE_PIN Y11   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "a1": "set_property -dict { PACKAGE_PIN Y12   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "a2": "set_property -dict { PACKAGE_PIN W11   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "a3": "set_property -dict { PACKAGE_PIN V11   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "a4": "set_property -dict { PACKAGE_PIN T5    IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "a5": "set_property -dict { PACKAGE_PIN U10   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",

    # Arduino SPI
    "ck_miso": "set_property -dict { PACKAGE_PIN W15   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "ck_mosi": "set_property -dict { PACKAGE_PIN T12   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "ck_sck": "set_property -dict { PACKAGE_PIN H15   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "ck_ss": "set_property -dict { PACKAGE_PIN F16   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",

    # Arduino I2C
    "ar_scl": "set_property -dict { PACKAGE_PIN P16   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "ar_sda": "set_property -dict { PACKAGE_PIN P15   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",

    #Raspberry Digital I/O 
    "rpio_02_r": "set_property -dict { PACKAGE_PIN W18   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "rpio_03_r": "set_property -dict { PACKAGE_PIN W19   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "rpio_04_r": "set_property -dict { PACKAGE_PIN Y18   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "rpio_05_r": "set_property -dict { PACKAGE_PIN Y19   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "rpio_06_r": "set_property -dict { PACKAGE_PIN U18   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "rpio_07_r": "set_property -dict { PACKAGE_PIN U19   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "rpio_08_r": "set_property -dict { PACKAGE_PIN F19   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "rpio_09_r": "set_property -dict { PACKAGE_PIN V10   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "rpio_10_r": "set_property -dict { PACKAGE_PIN V8    IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "rpio_11_r": "set_property -dict { PACKAGE_PIN W10   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "rpio_12_r": "set_property -dict { PACKAGE_PIN B20   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "rpio_13_r": "set_property -dict { PACKAGE_PIN W8    IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "rpio_14_r": "set_property -dict { PACKAGE_PIN V6    IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "rpio_15_r": "set_property -dict { PACKAGE_PIN Y6    IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "rpio_16_r": "set_property -dict { PACKAGE_PIN B19   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "rpio_17_r": "set_property -dict { PACKAGE_PIN U7    IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "rpio_18_r": "set_property -dict { PACKAGE_PIN C20   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "rpio_19_r": "set_property -dict { PACKAGE_PIN Y8    IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "rpio_20_r": "set_property -dict { PACKAGE_PIN A20   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "rpio_21_r": "set_property -dict { PACKAGE_PIN Y9    IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "rpio_22_r": "set_property -dict { PACKAGE_PIN U8    IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "rpio_23_r": "set_property -dict { PACKAGE_PIN W6    IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "rpio_24_r": "set_property -dict { PACKAGE_PIN Y7    IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "rpio_25_r": "set_property -dict { PACKAGE_PIN F20   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "rpio_26_r": "set_property -dict { PACKAGE_PIN W9    IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "rpio_sd_r": "set_property -dict { PACKAGE_PIN Y16   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "rpio_sc_r": "set_property -dict { PACKAGE_PIN Y17   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",

    #HDMI Rx
    "hdmi_rx_cec": "set_property -dict { PACKAGE_PIN H17   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "hdmi_rx_clk_n": "set_property -dict { PACKAGE_PIN P19   IOSTANDARD TMDS_33  } [get_ports { signal_name }];",
    "hdmi_rx_clk_p": "set_property -dict { PACKAGE_PIN N18   IOSTANDARD TMDS_33  } [get_ports { signal_name }];",
    "hdmi_rx_d_n0": "set_property -dict { PACKAGE_PIN W20   IOSTANDARD TMDS_33  } [get_ports { signal_name }];",
    "hdmi_rx_d_p0": "set_property -dict { PACKAGE_PIN V20   IOSTANDARD TMDS_33  } [get_ports { signal_name }];",
    "hdmi_rx_d_n1": "set_property -dict { PACKAGE_PIN U20   IOSTANDARD TMDS_33  } [get_ports { signal_name }];",
    "hdmi_rx_d_p1": "set_property -dict { PACKAGE_PIN T20   IOSTANDARD TMDS_33  } [get_ports { signal_name }];",
    "hdmi_rx_d_n2": "set_property -dict { PACKAGE_PIN P20   IOSTANDARD TMDS_33  } [get_ports { signal_name }];",
    "hdmi_rx_d_p2": "set_property -dict { PACKAGE_PIN N20   IOSTANDARD TMDS_33  } [get_ports { signal_name }];",
    "hdmi_rx_hpd": "set_property -dict { PACKAGE_PIN T19   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "hdmi_rx_scl": "set_property -dict { PACKAGE_PIN U14   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "hdmi_rx_sda": "set_property -dict { PACKAGE_PIN U15   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",

    #HDMI Tx
    "hdmi_tx_cec": "set_property -dict { PACKAGE_PIN G15   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "hdmi_tx_clk_n": "set_property -dict { PACKAGE_PIN L17   IOSTANDARD TMDS_33  } [get_ports { signal_name }];",
    "hdmi_tx_clk_p": "set_property -dict { PACKAGE_PIN L16   IOSTANDARD TMDS_33  } [get_ports { signal_name }];",
    "hdmi_tx_d_n0": "set_property -dict { PACKAGE_PIN K18   IOSTANDARD TMDS_33  } [get_ports { signal_name }];",
    "hdmi_tx_d_p0": "set_property -dict { PACKAGE_PIN K17   IOSTANDARD TMDS_33  } [get_ports { signal_name }];",
    "hdmi_tx_d_n1": "set_property -dict { PACKAGE_PIN J19   IOSTANDARD TMDS_33  } [get_ports { signal_name }];",
    "hdmi_tx_d_p1": "set_property -dict { PACKAGE_PIN K19   IOSTANDARD TMDS_33  } [get_ports { signal_name }];",
    "hdmi_tx_d_n2": "set_property -dict { PACKAGE_PIN H18   IOSTANDARD TMDS_33  } [get_ports { signal_name }];",
    "hdmi_tx_d_p2": "set_property -dict { PACKAGE_PIN J18   IOSTANDARD TMDS_33  } [get_ports { signal_name }];",
    "hdmi_tx_hpdn": "set_property -dict { PACKAGE_PIN R19   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",

    #Crypto SDA 
    "crypto_sda": "set_property -dict { PACKAGE_PIN J15   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];"
}

pynq_constraints_mode = {
    # switches
    "sw0": "in",
    "sw1": "in",
    # RGB LEDs
    "led4_b": "out",
    "led4_g": "out",
    "led4_r": "out",
    "led5_b": "out",
    "led5_g": "out",
    "led5_r": "out",
    # LEDs
    "led0": "out",
    "led1": "out",
    "led2": "out",
    "led3": "out",
    # Buttons
    "btn0": "in",
    "btn1": "in",
    "btn2": "in",
    "btn3": "in"
}

io_full_dictionary = {key: None for key in pynq_constraints.keys()}


# Contraints file contents:
# TODO: Add tag that this has been auto generated by PYNQ SoC Builder


# Configurable Variables
verbose_prints = False # Not implemented yet.

########## Start of Tcl Script Generation ##########

## Order of Procedure ##

# 1. Source the Tcl API file
# 2. Open Project
# 3. Create new Block Design file
# 4. Add Processor IP to BD
# 5. Add User Created Model to BD
# 6. Add AXI GPIO for EACH input/output
#   a. Configure each GPIO accordingly
#   b. Connect each GPIO to the imported model (user model)
# 7. Add AXI Interconnect IP
#   a. Configure the Interconnect
#   b. Connect Mxx_AXI ports to each AXI GPIO's S_AXI port
#   c. Connect M_AXI_GP0 of the Processing System to S00_AXI connection of the AXI Interconnect.
# 8. Add "Processor System Reset" IP
#   a. Run Connection Automation
#   b. then Run Block Automation
# 9. Populate Memory Information
# 10.Validate the Block Diagram
# 11.Create HDL Wrapper
#   a. Set created wrapper as top
# 12. Run Synthesis, Implementation and Generate Bitstream


def generate_tcl(hdlgen_prj, add_to_log_box):
    # io_map = True   # Force true for testing purposes
    # This is the instruction to load from file.
    xmlmanager = xmlman.Xml_Manager(hdlgen_prj, hdlgen_prj.hdlgen_path)
    io_map = xmlmanager.read_io_config()
    proj_config = xmlmanager.read_proj_config()

    try: 
        if proj_config['use_board_io'] == False:
            io_map = None
    except Exception as e:
        print(f"Found exception {e} in Tcl_Gen @ line 287")


    add_to_log_box(f"\nRunning Generate Tcl Program")

    file_contents = ""

    ###################################################################
    ########## Parsing .hdlgen file for required information ##########
    ###################################################################

    # As of 23/3/24 all the .hdlgen information is parsed in hdlgenproject.py 
    # - All variables are found here.

    ###########################################
    ########## Source Generate Procs ##########
    ###########################################
    file_contents += source_generate_procs()

    ##############################################
    ########## Open Project / Start GUI ##########
    ##############################################

    # Try to load from XML and sanitize the response
    start_gui = True
    try:
        start_gui = proj_config['open_viv_gui']
    except Exception as e:
        add_to_log_box("\nCouldn't load open_viv_gui setting from XML - using default: True")
    finally:
        if not isinstance(start_gui, bool): # Check if the value is a boolean when finishing 
            start_gui = True
            add_to_log_box("\nopen_viv_gui not loaded as boolean, ignoring and using default: True")

    # Add Tcl Command 
    if start_gui:
        file_contents += "\nstart_gui" 
    

    # Open Project
    file_contents += f"\nopen_project {hdlgen_prj.path_to_xpr}" # Path store in hdlgenproject.py

    # Print info to log_box
    add_to_log_box(f"\nXPR Location: {hdlgen_prj.path_to_xpr}")


    ###############################################
    ########## Set Project Configuration ##########
    ###############################################


    if SET_BOARD_PART_PROPERTY:
        try: 
            if proj_config['board'] == "PYNQ Z2":
                print("Setting board to Z2")
                file_contents += f"\nset_property board_part tul.com.tw:pynq-z2:part0:1.0 [current_project]"
            elif proj_config['board'] == "PYNQ Z1":
                print("Setting board to Z1")
                file_contents += f"\nset_property board_part www.digilentinc.com:pynq-z1:part0:1.0 [current_project]"
            else:
                print(f"Tcl Gen: Could not recognise board: {proj_config['board']}, using PYNQZ2 as default")
                file_contents += f"\nset_property board_part tul.com.tw:pynq-z2:part0:1.0 [current_project]"

        except Exception as e:
            print(f"Tcl Gen: Could not determine target board, using PYNQ Z-2 {e} if true: {SET_BOARD_PART_PROPERTY}")
            if SET_BOARD_PART_PROPERTY:
                file_contents += f"\nset_property board_part tul.com.tw:pynq-z2:part0:1.0 [current_project]"


    #################################################
    ########## Import XDC Constraints File ##########
    #################################################
    file_contents += import_xdc_constraints_file(hdlgen_prj.full_path_to_xdc, hdlgen_prj.location)

    ###########################################
    ########## Generate Block Design ##########
    ###########################################

    # Try to load from XML and sanitize the response
    regenerate_bd = True
    try:
        regenerate_bd = proj_config['regen_bd']
    except Exception as e:
        add_to_log_box("\nCouldn't load alwys_gen_bd setting from XML - using default: True")
    finally:
        if not isinstance(regenerate_bd, bool): # Check if value is a boolean before continuing
            regenerate_bd = True
            add_to_log_box("\nalwys_gen_bd not loaded as boolean, ignoring and using default: True")

    # Decision Variables
    generate_new_bd_design = regenerate_bd   # Default Consignment
    delete_old_bd_design = False             # Default Consignment

    # Example Wrapper Path:
    # D:/HDLGen-ChatGPT/User_Projects/Fearghal_November/RISCV_RB/VHDL/AMDprj/RISCV_RB.srcs/sources_1/bd/RISCV_RB_bd/hdl/RISCV_RB_bd_wrapper.vhd

    # Example BD Path:
    # D:/HDLGen-ChatGPT/User_Projects/Fearghal_November/RISCV_RB/VHDL/AMDprj/RISCV_RB.srcs/sources_1/bd/RISCV_RB_bd/RISCV_RB_bd.bd
    
    path_to_bd_folder_check = hdlgen_prj.path_to_bd + "/" +  hdlgen_prj.bd_filename
    path_to_bd_file_check = path_to_bd_folder_check + "/" + hdlgen_prj.bd_filename + ".bd"
    
    # Wrapper can be Verilog or VHDL
    path_to_wrapper = path_to_bd_folder_check + "/hdl/" + hdlgen_prj.bd_filename + "_wrapper"

    # Use this variables for checking if a wrapper exists
    path_to_vhdl_wrapper_file_check = path_to_wrapper + "vhd"
    path_to_verilog_wrapper_file_check = path_to_wrapper + "v"


    bd_exists = os.path.exists(path_to_bd_file_check)
    wrapper_exists = os.path.exists(path_to_vhdl_wrapper_file_check) or os.path.exists(path_to_verilog_wrapper_file_check)

    add_to_log_box(f"\nExisting Block Design Found?: {bd_exists}")
    add_to_log_box(f"\nExisting HDL Wrapper Found?: {wrapper_exists}")
    add_to_log_box(f"\nRegenerate new BD?: {regenerate_bd}")

    print(f"\nExisting Block Design Found?: {bd_exists}")
    print(f"\nExisting HDL Wrapper Found?: {wrapper_exists}")
    print(f"\nRegenerate new BD?: {regenerate_bd}")

    ## This area is a mess.
    if (wrapper_exists and bd_exists):
        if regenerate_bd:
            delete_old_bd_design = True
        else:
            generate_new_bd_design = False

    elif (not wrapper_exists and bd_exists):
        print("Wrapper does not exist, BD does exist")
        if regenerate_bd:   
            file_contents += f"\ndelete_file {path_to_bd_file_check}"  # then the BD design
            delete_old_bd_design = False
            # This section of code could be re-done much better, new workflow later generates wrapper always, therefore
            # we can now handle this situation with no problem.
    elif (wrapper_exists and not bd_exists):
        print("Wrapper exists but BD doesn't, application cannot handle this situation.")
        file_contents += ""
    elif (not wrapper_exists and not bd_exists):
        print("Wrapper and BD not found, generating these components...")

    if delete_old_bd_design:
        add_to_log_box("\nRemoving Old Block Design")
        # TODO: This could have safety checks to in event that one or other doesn't exist.
        file_contents += f"\ndelete_hdl_wrapper {path_to_wrapper}"  # Wrapper deletes first - Note Tcl API doesn't want extension
        file_contents += f"\ndelete_file {path_to_bd_file_check}"       # then the BD design

    ## Mess is fine here.

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++#
        #++++++++# Start of Generate New BD File Block #++++++++#
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++#


    # We need to    1) Create the BD File
    #               2) Go do some other things
    #               3) Come back and export SVG / Delete the block diagram
    # Why? - BD is exported as blank, can't use same BD as whats actually used for 
    # bitstream gen cos it generates full picture too fast
    
    generate_svg = True
    if generate_svg:
        img_bd_name = "image_bd"
        path_to_img_bd = hdlgen_prj.path_to_bd + "/" + img_bd_name + "/" + img_bd_name + ".bd"

        file_contents += f"\ndelete_file_safely {hdlgen_prj.path_to_bd + '/' + img_bd_name} /{img_bd_name}.bd"    # + '/' + img_bd_name removed to fix bug

        # Create block design, import the 
        file_contents += f"\ncreate_bd_file {img_bd_name}"
        # file_contents += "\nupdate_compile_order -fileset sources_1"
        # file_contents += f"\ncreate_bd_cell -type module -reference {module_source} {module_source}_0"
        file_contents += "\nset_property source_mgmt_mode All [current_project]"    # Setting automatic mode for source management
        file_contents += f"\nadd_module {hdlgen_prj.name} {hdlgen_prj.name}_0"  # Import the user-created module

    if generate_new_bd_design:
        add_to_log_box("\nGenerating New Block Design")
        created_signals = [] # This is an array of all signals that are created (this is cos >32 bit signals are divided)

        # (3) Create a new BD File
        file_contents += f"\ncreate_bd_file {hdlgen_prj.bd_filename}"              # Create a new BD
        
        add_to_log_box(f"\nCreating Block Design: {hdlgen_prj.bd_filename}")
        
        # (4) Add User Created Model to BD
        file_contents += "\nset_property source_mgmt_mode All [current_project]"    # Setting automatic mode for source management
        file_contents += f"\nadd_module {hdlgen_prj.name} {hdlgen_prj.name}_0"  # Import the user-created module
        add_to_log_box(f"\nImporting Module: {hdlgen_prj.name}")

        if generate_svg:
            file_contents += "\nupdate_module_reference { " + hdlgen_prj.bd_filename + "_" + hdlgen_prj.name + " _0_0 " + img_bd_name + "_" + hdlgen_prj.name + "_0_0  }" # Refresh model (important if injecting to port map)
        else:
            file_contents += "\nupdate_module_reference { " + hdlgen_prj.bd_filename + "_" + hdlgen_prj.name + " _0_0 }" # Refresh model (important if injecting to port map)



        # (5) Add Processor to BD
        file_contents += "\nadd_processing_unit"                        # Import Processing Unit to the BD
        add_to_log_box(f"\nAdding Processing Unit")
        
        # Running this as safety
        file_contents += "\nupdate_compile_order -fileset sources_1"
        file_contents += "\nupdate_compile_order -fileset sim_1"

        # Just before (6) we need to make any port that will use I/O an external port.
        # Before connecting to GPIO, make pin external if needed.
        # It should also only be completed if the io_map is supplied


        if io_map:
            add_to_log_box(f"\nIO Map Present: {io_map}")

        returned_contents, created_signals = generate_connections(hdlgen_prj.name, hdlgen_prj.get_generate_conn_signals(), io_map, hdlgen_prj.location, add_to_log_box)
        file_contents += returned_contents

        file_contents += connect_interconnect_reset_and_run_block_automation(created_signals, add_to_log_box)
    
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++#
        #++++++++# End of Generate New BD File Block #++++++++#
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++#


    # Need to check what mode we are in:
    # if project_language == "VHDL":
    file_contents += create_vhdl_wrapper(hdlgen_prj.bd_filename, hdlgen_prj.path_to_bd) 
    # elif project_language == "Verilog":
    #     file_contents += create_verilog_wrapper(bd_filename, path_to_bd)
    # else:
    #     print("Couldn't detect language - Deaulting to VHDL")
    #     file_contents += create_vhdl_wrapper(bd_filename, path_to_bd)


    path_to_bd_export = hdlgen_prj.environment + "/" + hdlgen_prj.AMDproj_folder_rel_path + "/" + hdlgen_prj.bd_filename + ".tcl"   # hotfix changed to environment
    path_to_bd_file = f"{hdlgen_prj.path_to_bd}/{hdlgen_prj.bd_filename}/{hdlgen_prj.bd_filename}.bd"

    # Just before we generate bitstream, reopen first design and export it as SVG before deleting it again.
    if generate_svg:

        # Check if the directory exists and if not make it.

        # Open the design again
        file_contents += f"\nopen_bd_design {path_to_img_bd}"
        
        # Export SVG image of the created model
        print(f"Attempting to export SVG at {hdlgen_prj.location}/PYNQBuild/generated/{hdlgen_prj.name}.svg")
        friendly_cwd = os.getcwd().replace('\\', '/')
        file_contents += f"\nwrite_bd_layout -force -format svg {hdlgen_prj.location}/PYNQBuild/generated/{hdlgen_prj.name}.svg"

        # Delete it all again
        file_contents += f"\nexport_ip_user_files -of_objects  [get_files {path_to_img_bd}] -no_script -reset -force -quiet"
        file_contents += f"\nremove_files  {path_to_img_bd}"
        file_contents += f"\nfile delete -force {hdlgen_prj.path_to_bd + '/' + img_bd_name}"

    file_contents += generate_bitstream(path_to_bd_export,path_to_bd_file)


    # Try to load from XML and sanitize the response
    keep_vivado_open = False
    try:
        keep_vivado_open = proj_config['keep_viv_opn']
    except Exception as e:
        add_to_log_box("\nCouldn't load keep_viv_opn setting from XML - using default: False")
    finally:
        if not isinstance(start_gui, bool): # Check if the value is a boolean when finishing 
            keep_vivado_open = False
            add_to_log_box("\nkeep_viv_opn not loaded as boolean, ignoring and using default: False")


    file_contents += save_and_quit(start_gui, keep_vivado_open)
    write_tcl_file(file_contents, add_to_log_box, hdlgen_prj.location)


            #++++++++++++++++++++++++++++++++++++++++#
            #++++++++# END OF MAIN FUNCTION #++++++++#
            #++++++++++++++++++++++++++++++++++++++++#



################################################################################################
########## Import and Connect Interconnect Reset, Run Block and Connection Automation ##########
################################################################################################

def connect_interconnect_reset_and_run_block_automation(created_signals, add_to_log_box=None):
    # (7) Add the AXI Interconnect to the IP Block Design
    file_contents = f"\nadd_axi_interconnect 1 {len(created_signals)}"

    # Connect each GPIO to the Interconnect
    for x in range(len(created_signals)):
        file_contents += f"\nconnect_bd_intf_net -boundary_type upper [get_bd_intf_pins axi_interconnect_0/M{x:02d}_AXI] [get_bd_intf_pins {created_signals[x]}/S_AXI]"
        

    # (8) Add "Processor System Reset" IP
    file_contents += "\nadd_system_reset_ip"
    # Connect M_AXI_GP0 of the Processing System to S00_AXI connection of the AXI Interconnect.
    # TODO: Add this line to the proc file instead maybe
    file_contents += "\nconnect_bd_intf_net [get_bd_intf_pins processing_system7_0/M_AXI_GP0] -boundary_type upper [get_bd_intf_pins axi_interconnect_0/S00_AXI]"

    # Run auto-connection tool
    # file_contents += "\nrun_bd_auto_connect"
    file_contents += "\nrun_bd_automation_rule_processor"
    file_contents += "\nrun_bd_automation_rule_interconnect"
    for io in created_signals:
        file_contents += f"\nrun_bd_automation_rule_io {io}/s_axi_aclk" 
    

    # Run block automation tool
    file_contents += "\nrun_bd_block_automation"

    # (9) Populate Memory Information
    file_contents += "\nrun_addr_editor_auto_assign"
    
    # (10) Validate the Block Diagram
    file_contents += "\nvalidate_bd"

    return file_contents

##################################################################################
########## Generate Tcl Code to Slice GPIO PIN in GPIO_MODE = IN or OUT ##########
##################################################################################

def connect_slice_to_gpio(bit, gpio_mode, gpio_name, gpio_width, slice_number, module_source):
    file_contents = "\nstartgroup"
    file_contents += f"\ncreate_bd_cell -type ip -vlnv xilinx.com:ip:xlslice:1.0 {gpio_name}_{slice_number}_slice"
    file_contents += "\nendgroup"

    if gpio_mode == "in":
        file_contents += f"\nconnect_bd_net [get_bd_pins {gpio_name}/gpio_io_o] [get_bd_pins {gpio_name}_{slice_number}_slice/Din]"

        file_contents += "\nstartgroup"
        file_contents += f"\nset_property -dict [list CONFIG.DIN_TO {bit} CONFIG.DIN_FROM {bit} CONFIG.DIN_WIDTH {gpio_width} CONFIG.DIN_FROM {bit} CONFIG.DOUT_WIDTH 1] [get_bd_cells {gpio_name}_{slice_number}_slice]"
        file_contents += "\nendgroup"

        file_contents += "\nstartgroup"
        file_contents += f"\nmake_bd_pins_external  [get_bd_pins {gpio_name}_{slice_number}_slice/Dout]"
        file_contents += "\nendgroup"
        file_contents += f"\nset_property name {gpio_name}_{slice_number}_ext [get_bd_ports Dout_0]"

    elif gpio_mode == "out":
        file_contents += f"\nconnect_bd_net [get_bd_pins {module_source}_0/{gpio_name}] [get_bd_pins {gpio_name}_{slice_number}_slice/Din]"

        file_contents += "\nstartgroup"
        file_contents += f"\nset_property -dict [list CONFIG.DIN_TO {bit} CONFIG.DIN_FROM {bit} CONFIG.DIN_WIDTH {gpio_width} CONFIG.DIN_FROM {bit} CONFIG.DOUT_WIDTH 1] [get_bd_cells {gpio_name}_{slice_number}_slice]"
        file_contents += "\nendgroup"

        file_contents += "\nstartgroup"
        file_contents += f"\nmake_bd_pins_external  [get_bd_pins {gpio_name}_{slice_number}_slice/Dout]"
        file_contents += "\nendgroup"
        file_contents += f"\nset_property name {gpio_name}_{slice_number}_ext [get_bd_ports Dout_0]"


    return file_contents

###########################################################################################
########## Generate Tcl Code to Add and Connect All Input GPIO with External Pin ##########
###########################################################################################
def generate_all_input_external_gpio(gpio_name, gpio_width, module_source, occurences, add_to_log_box=None):
    file_contents = ""
    
    add_to_log_box(f"\nConnecting {gpio_name} to {occurences[0][0]} in 'all_input_external' mode")
    # In this configuration, we need to:
    #   1) Add an ALL INPUT GPIO, 
    #   2) make the pin of the COMPONENT external
    #   3) and connect to component.
    file_contents += f"\nadd_axi_gpio_all_input {gpio_name} {gpio_width}"
    # Need to make the GPIO external then move 
    # startgroup \n make_bd_pins_external  [get_bd_pins A/gpio_io_o] \n endgroup

    file_contents += f"\nstartgroup\nmake_bd_pins_external [get_bd_pins {module_source}_0/{gpio_name}]\nendgroup"
    file_contents += f"\nset_property name {gpio_name}_ext [get_bd_ports {gpio_name}_0]"
    
    # If the GPIO is added correctly, connect it to the User I/O
    file_contents += f"\nconnect_gpio_all_input_to_module_port {gpio_name} {module_source}_0"
    return file_contents

############################################################################################
########## Generate Tcl Code to Add and Connect All Output GPIO with External Pin ##########
############################################################################################
def generate_all_output_external_gpio(gpio_name, gpio_width, module_source, occurences, add_to_log_box=None):
    file_contents = ""
    
    add_to_log_box(f"\nConnecting {gpio_name} to {occurences[0][0]} in 'all_output_external' mode")
    # In this configuration, we need to:
    #   1) Add an ALL OUTPUT GPIO, 
    #   2) make the pin of the GPIO external, 
    #   3) and connect to component.
    file_contents += f"\nadd_axi_gpio_all_output {gpio_name} {gpio_width}"
    # Need to make the GPIO external then move 
    # startgroup \n make_bd_pins_external  [get_bd_pins A/gpio_io_o] \n endgroup

    file_contents += f"\nstartgroup\nmake_bd_pins_external [get_bd_pins {gpio_name}/gpio_io_o]\nendgroup"
    file_contents += f"\nset_property name {gpio_name}_ext [get_bd_ports gpio_io_o_0]"
    
    # If the GPIO is added correctly, connect it to the User I/O
    file_contents += f"\nconnect_gpio_all_output_to_module_port {gpio_name} {module_source}_0"
    return file_contents

##############################################################################################
########## Generate Tcl Code to Add and Connect All Input GPIO with No External Pin ##########
##############################################################################################
def generate_all_input_no_ext_gpio(gpio_name, gpio_width, module_source, add_to_log_box=None):
    file_contents = f"\nadd_axi_gpio_all_input {gpio_name} {gpio_width}"
    file_contents += f"\nconnect_gpio_all_input_to_module_port {gpio_name} {module_source}_0"
    return file_contents 

###############################################################################################
########## Generate Tcl Code to Add and Connect All Output GPIO with No External Pin ##########
###############################################################################################
def generate_all_output_no_ext_gpio(gpio_name, gpio_width, module_source, add_to_log_box=None):
    file_contents = f"\nadd_axi_gpio_all_output {gpio_name} {gpio_width}"
    file_contents += f"\nconnect_gpio_all_output_to_module_port {gpio_name} {module_source}_0"
    return file_contents 

##########################################
########## Generate Connections ##########
##########################################
def generate_connections(module_source, all_ports_parsed, io_map, location, add_to_log_box=None):
    xdc_contents = ""
    file_contents = ""
    interconnect_signals = []
    slice_number = 0 # Used to ensure all connections are unique

    # Assuming our component exists, and the processing unit and then nothing else.

    # Generate each signal as per IO map - not following the all_ports

    # pynq_constraints_mode tells us mode of the IO port.
    # pynq_contraints tells us the XDC line
    # for port in all_ports_parsed = [gpio_name, gpio_mode, gpio_width]
    # component_name is passed in.
    # io_map in form: "led0": "signal" or
    # io_map in form: "led0": "signal[bit]"

    # For now lets assume we are working with a single port from all_ports_pased
    for signal in all_ports_parsed: 
        gpio_name = signal[0]
        gpio_mode = signal[1]
        gpio_width = signal[2]

        # Add GPIO block for the component - This is a given and will always be done first.
        #file_contents += add gpio
        
        # Next - Take the array of keys and cycle thru the dictionary - if there is a match,
        occurences = []
        if io_map:
            for key, value in io_map.items():
                if gpio_name == io_map[key][0]:
                    occurences.append([key, io_map[key]])
                # elif gpio_name == io_map[key].split('[')[0]:
                #     occurences.append([key, io_map[key]])
                # elif  gpio_name == io_map[key]: # Might be redundant 
                #     occurences.append([key, io_map[key]])
            
        # Now we need to know: Target IO port (i.e. LED0) and the bit that is to be connected.
        # Lets assume ONLY 1 can be configured right now.
        if len(occurences) == 0:
            
            # If this signal does not appear in io_map (i.e. no signals in occurences array) set signal up with no I/O.
            # No XDC constraints required.
            # No external pins to be generated.

            if gpio_mode == "out" and int(gpio_width) <= 32:
                file_contents += generate_all_input_no_ext_gpio(gpio_name, gpio_width, module_source, add_to_log_box)
                # Add signal to the list of GPIO to be connected to interconnect (needed for block automation)
                interconnect_signals.append(gpio_name)
            elif gpio_mode == "in" and int(gpio_width) <= 32:
                file_contents += generate_all_output_no_ext_gpio(gpio_name, gpio_width, module_source, add_to_log_box)
                interconnect_signals.append(gpio_name)
            elif gpio_mode == "out" and int(gpio_width) > 32:
                returned_file_contents, returned_interconnect_signals = create_split_all_inputs(gpio_mode, gpio_name, gpio_width, module_source, add_to_log_box)

                file_contents += returned_file_contents
                for conn in returned_interconnect_signals:
                    interconnect_signals.append(conn)

            elif gpio_mode == "in" and int(gpio_width) > 32:
                print(gpio_name + " is greater than 32 bits. I/O will be split.")

                returned_file_contents, returned_interconnect_signals = create_split_all_outputs(gpio_mode, gpio_name, gpio_width, module_source, add_to_log_box)

                file_contents += returned_file_contents
                for conn in returned_interconnect_signals:
                    interconnect_signals.append(conn)

            pass # No I/O in this port;

        elif gpio_width == 1 and len(occurences) == 1:  # This will need to be changed to > 0 if support for 1 to many is developed.

            # If gpio_width = 1 and len(occurences) > 0
            # XDC constraints = {gpio_name}_ext
            # External Pin is generated.

            # Currently just assuming that only 1 I/O per pin.
            # If its more that should only be a change in the XDC file anyways. :) (if same mode)
            
            if gpio_mode == "in" and pynq_constraints_mode[occurences[0][0]]=="in":
                # Do not know yet what happens if you have two drivers. Probably not good.
                
                add_to_log_box("\nDon't know how to configure inputs yet for gpio_mode = in and pynq_constraints_mode = in. Skipping IO config. (GPIO_width = 1)")
                file_contents += generate_all_output_no_ext_gpio(gpio_name, gpio_width, module_source, add_to_log_box)
                
                # Add signal to the list of GPIO to be connected to interconnect (needed for block automation)
                # Possible Solution:
                # - Make the GPIO an ALL OUTPUT (i.e. You cannot write to the signal using Jupyter Notebook anymore.)

                interconnect_signals.append(gpio_name)
            elif gpio_mode == "in" and pynq_constraints_mode[occurences[0][0]]=="out":
                file_contents += generate_all_output_external_gpio(gpio_name, gpio_width, module_source, occurences, add_to_log_box)
                interconnect_signals.append(gpio_name)
                # XDC Constraints
                xdc_contents += add_line_to_xdc(occurences[0][0], gpio_name+"_ext")

            elif gpio_mode == "out" and pynq_constraints_mode[occurences[0][0]]=="in":
                # This mode is not possible, and should be ignored.
                
                add_to_log_box(f"\n{gpio_name} as an output and ({occurences[0][0]}) board I/O as input is not possible. Configuring without I/O")

                file_contents += generate_all_input_no_ext_gpio(gpio_name, gpio_width, module_source, add_to_log_box)
                # Add signal to the list of GPIO to be connected to interconnect (needed for block automation)
                interconnect_signals.append(gpio_name)
                pass
            elif gpio_mode == "out" and pynq_constraints_mode[occurences[0][0]]=="out":
                file_contents += generate_all_input_external_gpio(gpio_name, gpio_width, module_source, occurences, add_to_log_box)
                interconnect_signals.append(gpio_name)
                # run XDC constraints 
                xdc_contents += add_line_to_xdc(occurences[0][0], gpio_name+"_ext")

            pass # if the GPIO_width is 1. Make that port external
        elif gpio_width == len(occurences) and gpio_width <= 32:    # It wouldn't be possible but ok to add check anyways for readability.
            # if gpio width == len(occurences) then we have fully routed a signal and don't need to slice.
            # 1) Add GPIO,
            # 2) Connect
            interconnect_signals.append(gpio_name)
            # for occur in occurences:
            # board_io = occur[0]
            # signal_pin = occur[1]
            force_continue = False
            last_occur_io_mode = pynq_constraints_mode[occurences[0][0]]
            for occur in occurences:
                if pynq_constraints_mode[occur[0]] != last_occur_io_mode:
                    print("=========Does not support mixed INPUT and OUTPUT for GPIO same GPIO at this time=======")
                    add_to_log_box("\n=========Does not support mixed INPUT and OUTPUT for GPIO same GPIO at this time=======")
                    file_contents += generate_all_output_no_ext_gpio(gpio_name, gpio_width, module_source, add_to_log_box)
                    force_continue = True
                else:
                    last_occur_io_mode = pynq_constraints_mode[occur[0]]

            # last_occur_io_mode - Right now only out or in exclusively is allowed. Therefore last checked is also valid.
            if force_continue:
                continue # Continue to next signal

            if gpio_mode == "in" and last_occur_io_mode=="in":
                # Do not know yet what happens if you have two drivers. Probably not good.
                
                add_to_log_box("\nDon't know how to configure inputs yet for gpio_mode = in and pynq_constraints_mode = in. Skipping IO config. (gpio_width > 1)")
                file_contents += generate_all_output_no_ext_gpio(gpio_name, gpio_width, module_source, add_to_log_box)
                # Interconnect is completed already
                # - Handle (in, in) situations

            elif gpio_mode == "in" and last_occur_io_mode=="out":
                file_contents += generate_all_output_external_gpio(gpio_name, gpio_width, module_source, occurences, add_to_log_box)
                # Interconnect is completed already
                # Generate XDC
                for occur in occurences:
                    xdc_contents += add_line_to_xdc(occur[0], occur[1][0]+"_ext["+str(occur[1][1])+"]")

            elif gpio_mode == "out" and last_occur_io_mode=="in":
                # This mode is not possible, and should be ignored.
                
                add_to_log_box(f"\n{gpio_name} as an output and IO as input is not possible. Configuring without I/O")
                file_contents += generate_all_input_no_ext_gpio(gpio_name, gpio_width, module_source, add_to_log_box)
                # Interconnect is completed already
                
            elif gpio_mode == "out" and last_occur_io_mode=="out":
                file_contents += generate_all_input_external_gpio(gpio_name, gpio_width, module_source, occurences, add_to_log_box)
                # Interconnect is completed already
                # Generate XDC
                for occur in occurences:
                    xdc_contents += add_line_to_xdc(occur[0], occur[1][0]+"_ext["+str(occur[1][1])+"]")
            

        # Split Signal Instances
        
            ###########################################################################
            ###########################################################################
            ###########################################################################
            ###########################################################################
            ###########################################################################
            ###########################################################################
                    
        # NEEDS URGENT REVIEW
        elif gpio_width > 0 and len(occurences) > 0 and gpio_width > len(occurences) and gpio_width <= 32:
            # Need to slice signals -> equal case caught above.

            # IMPROVEMENT: We could reduce number of IP used by combining neighbouring bits into a single slice IP. I won't for sake of development time right now.
            # occurences in the form of [signal[x], bit] -> (We know that there cannot be just a single signal as gpio_width > 1 )
            if gpio_mode == "in":
                file_contents += generate_all_output_no_ext_gpio(gpio_name, gpio_width, module_source, add_to_log_box)
            elif gpio_mode == "out":
                file_contents += generate_all_input_no_ext_gpio(gpio_name, gpio_width, module_source, add_to_log_box)
            interconnect_signals.append(gpio_name)  # Add to interconnect as normal.
            
            for occur in occurences:
                board_io = occur[0]
                signal_name = occur[1][0]
                signal_pin = occur[1][1]
                if gpio_mode == "in" and pynq_constraints_mode[board_io]=="in":
                    # Do not know yet what happens if you have two drivers.
                    
                    add_to_log_box("\nDon't know how to configure inputs yet. Skipping IO")

                   
                elif gpio_mode == "in" and pynq_constraints_mode[board_io]=="out":
                    # think LED on selOPALU
                    
                    # # Define the regular expression pattern
                    # pattern = r'\[(\d+)\]'
                    # # Use re.search to find the pattern in the string
                    # match = re.search(pattern, signal_pin)

                    # Check if the pattern is found
                    # if match:
                        # Extract the number from the matched group
                        # extracted_number = match.group(1)
                        # print("Extracted number:", extracted_number)
                    # else:
                        # print("No match found - Assuming bit 0.")
                        
                    
                    # bit = 0
                    # try:
                        # bit = int(extracted_number)
                    # except Exception:
                        # add_to_log_box("\nCould not find specifed bit, assuming bit 0.")
                    
                    # Procedure
                    # 1) Do GPIO connection as normal.
                    # 2) Add and configure slice component, 
                    # 3) make it external.

                    # Just like normal, make the inital connection.
                    file_contents += connect_slice_to_gpio(signal_pin, gpio_mode, gpio_name, gpio_width, slice_number, module_source)
                    # Add External Port to XDC.
                    xdc_contents += add_line_to_xdc(board_io, signal_name+"_"+str(slice_number)+"_ext")

                    slice_number += 1   # must be called every time above API is used to ensure there is never any name collisions
                    pass
                elif gpio_mode == "out" and pynq_constraints_mode[board_io]=="in":
                    # This mode is not possible, and should be ignored.
                    add_to_log_box(f"\n{gpio_name} as an output and IO as input is not possible. Configuring without I/O")
                    
                    # Add signal to the list of GPIO to be connected to interconnect (needed for block automation)
                    pass # not possible
                elif gpio_mode == "out" and pynq_constraints_mode[board_io]=="out":
                    # think LED on count
                    
                    # # Define the regular expression pattern
                    # pattern = r'\[(\d+)\]'
                    # # Use re.search to find the pattern in the string
                    # match = re.search(pattern, signal_pin)

                    # Check if the pattern is found
                    # if match:
                    #     # Extract the number from the matched group
                    #     extracted_number = match.group(1)
                    #     print("Extracted number:", extracted_number)
                    # else:
                    #     print("No match found - Assuming bit 0.")
                        
                    
                    # bit = 0
                    # try:
                    #     bit = int(extracted_number)
                    # except Exception:
                        
                    #     add_to_log_box("\nCould not find specifed bit, assuming bit 0.")
                    
                    # Procedure
                    # 1) Do GPIO connection as normal.
                    # 2) Add and configure slice component, 
                    # 3) make it external.

                    # Just like normal, make the inital connection.
                    file_contents += connect_slice_to_gpio(signal_pin, gpio_mode, gpio_name, gpio_width, slice_number, module_source)
                    # Add External Port to XDC.
                    xdc_contents += add_line_to_xdc(board_io, signal_name+"_"+str(slice_number)+"_ext")

                    slice_number += 1   # must be called every time above API is used to ensure there is never any name collisions
                    pass
                pass

        elif gpio_width > 1 and len(occurences) > 1 and gpio_width < len(occurences):
            
            add_to_log_box("\nMore occurences than GPIO, not applicable for now. Ignoring - No External Connection Made")
            if gpio_mode == "out":
                file_contents += generate_all_input_no_ext_gpio(gpio_name, gpio_width, module_source, add_to_log_box)
            elif gpio_mode == "in":
                file_contents += generate_all_output_no_ext_gpio(gpio_name, gpio_width, module_source, add_to_log_box)
            interconnect_signals.append(gpio_name)

        elif gpio_width > 32 and len(occurences) > 0 and gpio_width > len(occurences):
    
            add_to_log_box(f"\nOutput on Signal >32-bit. {gpio_name} {gpio_width} {occurences}")
            print(f"\nOutput on Signal >32-bit. {gpio_name} {gpio_width} {occurences}")

            # How to approach this:
            # 1) Split our signal as notebook_gen does, into 32 bit chunks with naming standard.
            # 2) Run loop for each occurence, create a new slice IP for each individual signal.
            # 3) Can mix in and out - Don't bother supporting inputs at this time.

            # [gpio_name, gpio_mode, gpio_width]
            # gpio_width > 32 - that is known

            # TODO: This should be looped for each occurence.



            if gpio_mode == "in":
                returned_contents, returned_interconnect_signals = create_split_all_outputs(gpio_mode, gpio_name, gpio_width, module_source, add_to_log_box)
                file_contents += returned_contents
                for conn in returned_interconnect_signals:
                    interconnect_signals.append(conn)
            elif gpio_mode == "out":
                returned_contents, returned_interconnect_signals = create_split_all_inputs(gpio_mode, gpio_name, gpio_width, module_source, add_to_log_box)
                file_contents += returned_contents
                for conn in returned_interconnect_signals:
                    interconnect_signals.append(conn)

            for occur in occurences:
                # Extract info from occurence.
                board_io = occur[0]
                signal_signal_name = occur[1][0]
                signal_pin = occur[1][1]

                # # Locate the target bit from occurence map.
                # pattern = r'\[(\d+)\]'
                # match = re.search(pattern, signal_pin)
                # if match:
                #     # Extract the number from the matched group
                #     extracted_number = match.group(1)
                #     print("Extracted number:", extracted_number)
                # else:
                #     print("No match found - Assuming bit 0.")
                # bit = 0
                # try:
                #     bit = int(extracted_number)
                # except Exception:
                    
                #     add_to_log_box("\nCould not find specifed bit, assuming bit 0.") 


                # Now that we have extracted the necessary info, we target our specific application
                if gpio_mode == "in" and pynq_constraints_mode[board_io]=="in":
                    
                    add_to_log_box("\nInput IO Mapping on Split Input not supported yet. Adding without IO")

                        # GPIO are already added. No need to do anything with XDC.
                    pass
                elif gpio_mode == "in" and pynq_constraints_mode[board_io]=="out":
                    
                    add_to_log_box(f"\n{signal_pin} mapping to ({board_io}) ")
                    # Slicing signal

                    # Just like normal, make the inital connection.
                    # Bit and GPIO need to be changed to sub_bit and sub_signal (33 becomes 1 and gpio_name becomes gpio_name_63_32)
                    pin_counter = 0
                    gpio_split = []
                    while gpio_width - pin_counter > 0:
                        if gpio_width - pin_counter > 32:
                            signal_name = f"{gpio_name}_{pin_counter+31}_{pin_counter}"
                            pin_counter += 32
                            signal_width = 32
                        elif gpio_width - pin_counter <= 32:
                            signal_name = f"{gpio_name}_{gpio_width-1}_{pin_counter}"
                            signal_width = gpio_width - pin_counter
                            pin_counter += gpio_width - pin_counter
                        gpio_split.append([signal_name, signal_width])

                    # Here, we now have an array of ["signal_0_31", "signal_32_63", "signal_64_95"] # We can assume that desired bit is NOT out of range.
                    # Now we need to align the bit with the subsignal and offset the bit.
                    sub_signal_index = signal_pin // 32    #   0-31 = 0, 32-63 = 1, 64-95 = 2 and so on.

                    sub_signal = gpio_split[sub_signal_index][0]   # sub_signal
                    sub_width = gpio_split[sub_signal_index][1]
                    sub_bit_offset = 32*sub_signal_index        #  0-31 = -0, 32-63 = -32, 64-95 = -64 offset and so on
                    sub_bit = signal_pin - sub_bit_offset
                    # We now operate as if we are in <32 bit mode as we know the GPIO to target.



                    file_contents += connect_slice_to_gpio(sub_bit, gpio_mode, sub_signal, sub_width, slice_number, module_source)
                    # Add External Port to XDC.
                    xdc_contents += add_line_to_xdc(board_io, sub_signal+"_"+str(slice_number)+"_ext")

                    slice_number += 1   # must be called every time above API is used to ensure there is never any name collisions


                elif gpio_mode == "out" and pynq_constraints_mode[board_io]=="in":
                    # This case is impossible
                    
                    add_to_log_box(f"\n{signal_pin} as an output and ({board_io}) board I/O as input is not possible. Configuring without I/O")
                    # The GPIO is already added, no XDC changes needed.
                    # XDC
                    
                elif gpio_mode == "out" and pynq_constraints_mode[board_io]=="out":
                    
                    add_to_log_box(f"\n{signal_pin} mapping to ({board_io}) ")
                    
                    # Output is routed, just add the slice pin.
                    file_contents += connect_slice_to_gpio(signal_pin, gpio_mode, gpio_name, gpio_width, slice_number, module_source)
                    # Add External Port to XDC.
                    xdc_contents += add_line_to_xdc(board_io, gpio_name+"_"+str(slice_number)+"_ext")

                    slice_number += 1   # must be called every time above API is used to ensure there is never any name collisions

        else:
            
            add_to_log_box(f"\nEdge Case Detected. {gpio_name} {gpio_width} {occurences}")
            print(f"\nEdge Case Detected. {gpio_name} {gpio_width} {occurences}")

        # imagine we somehow swap the key and value of the dictionary:
        # Now check: Is our signal in the swapped dictionary?
    write_xdc_file(xdc_contents, add_to_log_box, location)
    return file_contents, interconnect_signals

#######################################################
########## Split and Route ALL INPUT signal ##########
#######################################################
def create_split_all_inputs(gpio_mode, gpio_name, gpio_width, module_source, add_to_log_box=None):
    add_to_log_box(f"\nCreating split ALL OUTPUTS for {gpio_name} of size {gpio_width}")
    file_contents = ""
    interconnect_signals = []
    
    print(gpio_name + " is greater than 32 bits. I/O will be split")
    gpio_width_int = int(gpio_width)

    # Splitting up the GPIO is similar as for the gpio_mode == "in" below.
    # Except we store X downto Y values as well.
    split_signal_dict = []
    pin_counter = 0
    while gpio_width_int - pin_counter > 0:
        if gpio_width_int - pin_counter  > 32:
            split_signal_dict.append([f"{gpio_name}_{pin_counter+31}_{pin_counter}", 32, pin_counter, pin_counter+31])
            pin_counter += 32
        elif gpio_width_int - pin_counter <= 32:
            split_signal_dict.append([f"{gpio_name}_{gpio_width_int-1}_{pin_counter}", gpio_width_int-pin_counter, pin_counter, gpio_width_int-1])
            pin_counter += gpio_width_int - pin_counter
    # From here is different.
    # 1) Make n separate ALL INPUT GPIO.
    # 2) Add a Slice IP for each of the GPIO signals created.
        # Configure as: add_slice_ip {name dIn_width dIn_from dIn_downto dout_width}
    # 3) Connect Component to Slices
    # 4) Connect Slices to GPIOs.
    # 5) Add new slice signals to created_signals map.
    
    # 1) Add GPIO
    for sub_sig in split_signal_dict:
        file_contents += f"\nadd_axi_gpio_all_input {sub_sig[0]} {sub_sig[1]}"
    # 2) Add Slices
    for sub_sig in split_signal_dict:
        file_contents += f"\nadd_slice_ip {sub_sig[0]}_slice {gpio_width} {sub_sig[3]} {sub_sig[2]} {sub_sig[1]}"
    # 3) Connect Component to Slices
    for sub_sig in split_signal_dict:
        file_contents += f"\nconnect_bd_net [get_bd_pins {module_source}_0/{gpio_name}] [get_bd_pins {sub_sig[0]}_slice/Din]"
    # 4) Connect the Slices to GPIO
    for sub_sig in split_signal_dict:
        file_contents += f"\nconnect_bd_net [get_bd_pins {sub_sig[0]}/gpio_io_i] [get_bd_pins {sub_sig[0]}_slice/Dout]"
    # 5) Add signals to created_signals dictionary - Required by interconnect steps later.
    for sub_sig in split_signal_dict:
        interconnect_signals.append(sub_sig[0])
    return file_contents, interconnect_signals

#######################################################
########## Split and Route ALL OUTPUT signal ##########
#######################################################
def create_split_all_outputs(gpio_mode, gpio_name, gpio_width, module_source, add_to_log_box=None):
    
    add_to_log_box(f"\nCreating split ALL INPUTS for {gpio_name} of size {gpio_width}")
    ###### IMPORTANT: As we are in a loop here creating signals - Need to check what still exists.
    print(gpio_name + " is greater than 32 bits. I/O will be split.")
    gpio_width_int = int(gpio_width)
    
    file_contents = ""
    interconnect_signals = []
    # First: Make n (two or more) GPIO for each 32 bit block + remainder.
    # Second: Add a concat block with n ports 
    # Third: Connect output of concat (merged signal) to the component
    # Fourth: Connect n GPIO to n inputs to concat IP.
    # Fifth: Add our new signals to an updated all_ports map for later.
    # Precurser: Make an array similar to all_ports that will store config.
    split_signal_dict = []
    pin_counter = 0
    while gpio_width_int - pin_counter > 0:
        if gpio_width_int - pin_counter  > 32:
            split_signal_dict.append([f"{gpio_name}_{pin_counter+31}_{pin_counter}", 32])
            pin_counter += 32
        elif gpio_width_int - pin_counter <= 32:
            split_signal_dict.append([f"{gpio_name}_{gpio_width_int-1}_{pin_counter}", gpio_width_int-pin_counter])
            pin_counter += gpio_width_int - pin_counter

    # Now we have formed a split signal map, we can follow the steps.

    # 1 Make N GPIO blocks
    for sub_sig in split_signal_dict:
        file_contents += f"\nadd_axi_gpio_all_output {sub_sig[0]} {sub_sig[1]}"
    
    # 2 Import Concat IP
    # name_concat for IP name, length of our split signal dict is the number of items we need to support.
    file_contents += f"\nadd_concat_ip {gpio_name}_concat {len(split_signal_dict)}"

    # 3 Connecting the CONCAT block to Comp
    file_contents += f"\nconnect_bd_net [get_bd_pins {gpio_name}_concat/dout] [get_bd_pins {module_source}_0/{gpio_name}]"

    # 4 Connect GPIO to CONCAT
    port_count = 0
    for sub_sig in split_signal_dict:
        file_contents += f"\nconnect_bd_net [get_bd_pins {sub_sig[0]}/gpio_io_o] [get_bd_pins {gpio_name}_concat/In{port_count}]"
        port_count += 1

    # final signals 
    for sub_sig in split_signal_dict:
        interconnect_signals.append(sub_sig[0]) 

    return file_contents, interconnect_signals


########################################################################
########## Parse all ports format from XML into useful format ##########
########################################################################
def parse_all_ports(all_ports):
    # All ports recieved as in HDLGen XML.
    #    signame = sig.getElementsByTagName("name")[0]
    #    mode = sig.getElementsByTagName("mode")[0]
    #    type = sig.getElementsByTagName("type")[0]
    #    desc = sig.getElementsByTagName("description")[0]
    # Job here is to convert into:
    # [signal_name, gpio_mode, gpio_width]
    new_array = []
    for io in all_ports:
        gpio_name = io[0]   # GPIO Name
        gpio_mode = io[1]   # GPIO Mode (in/out)
        gpio_type = io[2]   # GPIO Type (single bit/bus/array)

        if (gpio_type == "single bit"):
            gpio_width = 1
        elif (gpio_type[:3] == "bus"):
            # <type>bus(31 downto 0)</type> - Example Type Value
            substring = gpio_type[4:]           # substring = '31 downto 0)'
            words = substring.split()           # words = ['31', 'downto', '0)']
            gpio_width = int(words[0]) + 1      # eg. words[0] = 31
        elif (gpio_type[:5] == "array"):
            print("ERROR: Array mode type is not yet supported :(")
        else:
            print("ERROR: Unknown GPIO Type")
            print(gpio_type)
        new_array.append([gpio_name, gpio_mode, gpio_width])
    return new_array

#################################################
########## Import XDC Constraints File ##########
#################################################
def import_xdc_constraints_file(full_path_to_xdc, location):
    # Specify the name of the constraints
    file_contents = "\nset constraint_name \"constrs_1\""

    # Check if the constraint exists

    ############# Steps to delete existing XDC file #############
    # export_ip_user_files -of_objects  [get_files {{C:/repo/HDLGen-ChatGPT/User_Projects/Backup_led_Working_io_mapping/CB4CLED/VHDL/AMDprj/CB4CLED.srcs/constrs_1/imports/pynq-z2_v1.0.xdc/PYNQ-Z2 v1.0.xdc}}] -no_script -reset -force -quiet
    # remove_files  -fileset constrs_1 {{C:/repo/HDLGen-ChatGPT/User_Projects/Backup_led_Working_io_mapping/CB4CLED/VHDL/AMDprj/CB4CLED.srcs/constrs_1/imports/pynq-z2_v1.0.xdc/PYNQ-Z2 v1.0.xdc}}
    # file delete -force {C:/repo/HDLGen-ChatGPT/User_Projects/Backup_led_Working_io_mapping/CB4CLED/VHDL/AMDprj/CB4CLED.srcs/constrs_1/imports/pynq-z2_v1.0.xdc/PYNQ-Z2 v1.0.xdc} 

    ############# Steps to add new XDC file (note: Copy XDC to project is enabled by import_files command) #############
    # add_files -fileset constrs_1 -norecurse {{C:/repo/PYNQ-SoC-Builder/pynq-z2_v1.0.xdc/PYNQ-Z2 v1.0.xdc}}
    # import_files -fileset constrs_1 {{C:/repo/PYNQ-SoC-Builder/pynq-z2_v1.0.xdc/PYNQ-Z2 v1.0.xdc}}

    ############# Steps to check if constraints exist ############# 
    # file exists C:/repo/HDLGen-ChatGPT/User_Projects/Backup_led_Working_io_mapping/CB4CLED/VHDL/AMDprj/CB4CLED.srcs/constrs_1/imports/pynq-z2_v1.0.xdc
    # file exists - path to xdc.

    # Step 1: Check if file exists:
    file_contents += f"\nset xdc_exists [file exists {full_path_to_xdc}]"
    
    # Step 2: If file exists - Delete it.
    file_contents += "\nif {$xdc_exists} {"
    
    file_contents += "\n    export_ip_user_files -of_objects  [get_files {{"
    file_contents += full_path_to_xdc
    file_contents += "}}] -no_script -reset -force -quiet"

    file_contents += "\n    remove_files  -fileset constrs_1 {{"
    file_contents += full_path_to_xdc
    file_contents += "}}"

    file_contents += "\n    file delete -force {"
    file_contents += full_path_to_xdc
    file_contents += "}"
    
    file_contents += "\n}"

    # Step 3: Add XDC file
    current_dir = os.getcwd()
    friendly_current_dir = current_dir.replace("\\", "/")
    path_to_constraints = location + "/PYNQBuild/generated/physical_constr.xdc"       # This needs to be updated with generated constraints

    file_contents += "\nadd_files -fileset constrs_1 -norecurse {"
    file_contents += path_to_constraints
    file_contents += "}"

    file_contents += "\nimport_files -force -fileset constrs_1 {"   # -force flag will overwrite physical_constr.xdc if it exists and somehow wasn't deleted.
    file_contents += path_to_constraints
    file_contents += "}"

    return file_contents

##########################################
#   Create VHDL Wrapper and set as top   #
##########################################
def create_vhdl_wrapper(bd_filename, path_to_bd):
    file_contents = f"\nset wrapper_exists [file exists {path_to_bd}/{bd_filename}_wrapper.vhd]"
    file_contents += "\nif {$wrapper_exists} {"
    file_contents += f"\n    export_ip_user_files -of_objects  [get_files {path_to_bd}/{bd_filename}_wrapper.vhd] -no_script -reset -force -quiet"
    file_contents += f"\n    remove_files  {path_to_bd}/{bd_filename}_wrapper.vhd"
    file_contents += f"\n    file delete -force {path_to_bd}/{bd_filename}_wrapper.vhd"
    file_contents += f"\n    update_compile_order -fileset sources_1"
    file_contents += "\n} else {"
    file_contents += f"\n    create_hdl_wrapper {path_to_bd} {bd_filename}"
    file_contents += f"\n    set_wrapper_top {bd_filename}_wrapper"
    file_contents += "\n}"
    return file_contents

#############################################
#   Create Verilog Wrapper and set as top   #
#############################################

def create_verilog_wrapper(bd_filename, path_to_bd):
    file_contents = f"\nset wrapper_exists [file exists {path_to_bd}/{bd_filename}_wrapper.v]"
    file_contents += "\nif {$wrapper_exists} {"
    file_contents += f"\n    export_ip_user_files -of_objects  [get_files {path_to_bd}/{bd_filename}_wrapper.v] -no_script -reset -force -quiet"
    file_contents += f"\n    remove_files  {path_to_bd}/{bd_filename}_wrapper.v"
    file_contents += f"\n    file delete -force {path_to_bd}/{bd_filename}_wrapper.v"
    file_contents += f"\n    update_compile_order -fileset sources_1"
    file_contents += "\n} else {"
    file_contents += f"\n    create_hdl_wrapper {path_to_bd} {bd_filename}"
    file_contents += f"\n    set_wrapper_top {bd_filename}_wrapper"
    file_contents += "\n}"
    return file_contents

################################
#   Import generate_procs.tcl  #
################################
def source_generate_procs():
    current_dir = os.getcwd()
    friendly_current_dir = current_dir.replace("\\", "/")
    file_contents = "source " + friendly_current_dir + "/application/generate_procs.tcl"  # Source the procedures
    return file_contents

##########################################
#   Return Generate Bitstream Tcl Code   #
##########################################
def generate_bitstream(path_to_bd_export, path_to_bd_design):
    # (12) Run Synthesis, Implementation and Generate Bitstream
    file_contents = "\ngenerate_bitstream"
    # If BD isn't open, export will fail.
    file_contents += f"\nopen_bd_design {path_to_bd_design}"
    file_contents += f"\nexport_bd {path_to_bd_export}"
    return file_contents

####################################
#   Return Save and Quit Tcl Code  #
####################################
def save_and_quit(start_gui, keep_vivado_open):
    file_contents = "\nwait_on_run impl_1"
    if start_gui:
        if not keep_vivado_open:
            file_contents += "\nstop_gui"
            # file_contents += "\nclose_design"
            file_contents += "\nexit"
        else:
            # GUI started, and user wishes to close Vivado themselves.
            # Do nothing.
            pass
    else: # GUI not started, close project, don't run stop_gui command.
        # file_contents += "\nstop_gui"
        # file_contents += "\nclose_design"
        file_contents += "\nexit"
    return file_contents

########################
#   Write to Tcl File  #
########################
def write_tcl_file(file_contents, add_to_log_box, location):
    with open(f'{location}/PYNQBuild/generated/generate_script.tcl', 'w') as file:
        # Export Tcl Script
        file.write(file_contents)
        # print("generate_script.tcl generated!")
        add_to_log_box(f"\nSuccessfully wrote Tcl Script to {location}/PYNQBuild/generated/generate_script.tcl")

########################
#   Write to XDC File  #
########################
def write_xdc_file(xdc_contents, add_to_log_box, location):
    with open(f'{location}/PYNQBuild/generated/physical_constr.xdc', 'w') as file:
        # Export contraints file
        file.write(xdc_contents)
        add_to_log_box(f"\nSuccessfully wrote constraints file to {location}/PYNQBuild/generated/physical_constr.xdc")

########################
#   Make XDC Cfg Line  #
########################
def add_line_to_xdc(board_gpio, external_pin):
    line_to_add = pynq_constraints[board_gpio]
    line_to_add = line_to_add.replace("signal_name", external_pin)
    line_to_add = "\n" + line_to_add
    line_to_add += f" # {external_pin} connection to {board_gpio}"
    return line_to_add