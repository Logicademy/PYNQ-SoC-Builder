import xml.dom.minidom
import os
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


def generate_tcl(path_to_hdlgen_project, regenerate_bd=True, start_gui=True, keep_vivado_open=False, skip_board_config=False, io_map=None, gui_application=None):

    # For logging to console window - Look for GUI_APP and use the add_to_log_box API - Seen throughout this project/script.
    if gui_application:
        gui_application.add_to_log_box(f"\nRunning Generate Tcl Program")

    xdc_contents = "" # Initalise the xdc_contents variable
    file_contents = ""
    ###################################################################
    ########## Parsing .hdlgen file for required information ##########
    ###################################################################

    hdlgen = xml.dom.minidom.parse(path_to_hdlgen_project)
    root = hdlgen.documentElement

    # Project Manager - Settings
    projectManager = root.getElementsByTagName("projectManager")[0]
    projectManagerSettings = projectManager.getElementsByTagName("settings")[0]
    name = projectManagerSettings.getElementsByTagName("name")[0].firstChild.data
    environment = projectManagerSettings.getElementsByTagName("environment")[0].firstChild.data
    location = projectManagerSettings.getElementsByTagName("location")[0].firstChild.data

    if gui_application:
        gui_application.add_to_log_box(f"\nLoaded HDLGen Project: {name} at {path_to_hdlgen_project}")


    # genFolder - VHDL Folders
    genFolder = root.getElementsByTagName("genFolder")[0]
    model_folder = genFolder.getElementsByTagName("vhdl_folder")[0]
    testbench_folder = genFolder.getElementsByTagName("vhdl_folder")[1]
    # ChatGPT_folder = genFolder.getElementsByTagName("vhdl_folder")[2]             # Commented as not needed
    # ChatGPT_Backups_folder = genFolder.getElementsByTagName("vhdl_folder")[3]     # Commented as not needed
    try:
        AMDproj_folder = genFolder.getElementsByTagName("vhdl_folder")[4]
    except Exception:
        AMDproj_folder = genFolder.getElementsByTagName("verilog_folder")[4]
    AMDproj_folder_rel_path = AMDproj_folder.firstChild.data

    # hdlDesign - entityIOPorts
    hdlDesign = root.getElementsByTagName("hdlDesign")[0]
    entityIOPorts = hdlDesign.getElementsByTagName("entityIOPorts")[0]
    signals = entityIOPorts.getElementsByTagName("signal")

    if gui_application:
        gui_application.add_to_log_box(f"\nHDLGen XML Loaded Successfully")

    all_ports = []
    for sig in signals:
        signame = sig.getElementsByTagName("name")[0]
        mode = sig.getElementsByTagName("mode")[0]
        type = sig.getElementsByTagName("type")[0]
        desc = sig.getElementsByTagName("description")[0]
        all_ports.append(
            [signame.firstChild.data, mode.firstChild.data, type.firstChild.data, desc.firstChild.data]
        )

    if gui_application:
        gui_application.add_to_log_box(f"\nFound Signals:")
        for sig in all_ports:
            gui_application.add_to_log_box(f"\n    {sig[0]}, {sig[1]}, {sig[2]}")

    # Derived Variables
    location = location.replace('\\', '/')
    environment = environment.replace('\\', '/')
    path_to_xpr = environment + "/" + AMDproj_folder_rel_path + "/" + name + ".xpr"    #   hotfix changed to environment
    bd_filename = name + "_bd"
    module_source = name
    path_to_bd = environment + "/" + AMDproj_folder_rel_path + "/" + name + ".srcs/sources_1/bd"    # hotfix changed to environment

    # XDC Variables
    path_to_xdc = environment + "/" + AMDproj_folder_rel_path + "/" + name + ".srcs/constrs_1/imports/generated/"    # hotfix changed to environment
    full_path_to_xdc = path_to_xdc + "physical_constr.xdc"

    #################################################
    ########## Begin Tcl Script Generation ##########
    #################################################

    ##############################################
    ########## Open Project / Start GUI ##########
    ##############################################

    file_contents += source_generate_procs()

    # Additional Step: Set if GUI should be opened
    if start_gui:
        file_contents += "\nstart_gui"                              # Open Vivado GUI (option)

    # Open Project
    file_contents += f"\nopen_project {path_to_xpr}"                # Open Project
    
    if gui_application:
        gui_application.add_to_log_box(f"\nXPR Location: {path_to_xpr}")


    ###############################################
    ########## Set Project Configuration ##########
    ###############################################

    # Set Board Part (Project Parameter)
    if not skip_board_config:
        file_contents += f"\nset_property board_part tul.com.tw:pynq-z2:part0:1.0 [current_project]"

    #################################################
    ########## Import XDC Constraints File ##########
    #################################################
    file_contents += import_xdc_constraints_file(full_path_to_xdc)

    ###########################################
    ########## Generate Block Design ##########
    ###########################################

    # Decision Variables
    generate_new_bd_design = regenerate_bd   # Default Consignment
    delete_old_bd_design = False             # Default Consignment

    # Wrapper Path:
    # D:/HDLGen-ChatGPT/User_Projects/Fearghal_November/RISCV_RB/VHDL/AMDprj/RISCV_RB.srcs/sources_1/bd/RISCV_RB_bd/hdl/RISCV_RB_bd_wrapper.vhd

    # BD Path:
    # D:/HDLGen-ChatGPT/User_Projects/Fearghal_November/RISCV_RB/VHDL/AMDprj/RISCV_RB.srcs/sources_1/bd/RISCV_RB_bd/RISCV_RB_bd.bd
    
    path_to_bd_folder_check = path_to_bd + "/" +  bd_filename
    path_to_bd_file_check = path_to_bd_folder_check + "/" + bd_filename + ".bd"
    path_to_wrapper_file_check = path_to_bd_folder_check + "/hdl/" + bd_filename + "_wrapper.vhd"

    # print(path_to_bd_file_check)
    # print(path_to_wrapper_file_check)

    bd_exists = os.path.exists(path_to_bd_file_check)
    wrapper_exists = os.path.exists(path_to_wrapper_file_check)

    if gui_application:
            gui_application.add_to_log_box(f"\nExisting Block Design Found?: {bd_exists}")
            gui_application.add_to_log_box(f"\nExisting HDL Wrapper Found?: {wrapper_exists}")
            gui_application.add_to_log_box(f"\nRegenerate new BD?: {regenerate_bd}")

    print(f"\nExisting Block Design Found?: {bd_exists}")
    print(f"\nExisting HDL Wrapper Found?: {wrapper_exists}")
    print(f"\nRegenerate new BD?: {regenerate_bd}")

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
        print("-> Wrapper exists but BD doesn't, application cannot handle this situation.")
    elif (not wrapper_exists and not bd_exists):
        print("-> Wrapper and BD not found, generating these components...")

    if delete_old_bd_design:
        file_contents += f"\ndelete_file {path_to_wrapper_file_check}"  # Wrapper deletes first
        file_contents += f"\ndelete_file {path_to_bd_file_check}"  # then the BD design
    
        # export_ip_user_files -of_objects  [get_files D:/HDLGen-ChatGPT/User_Projects/Fearghal_November/RISCV_RB/VHDL/AMDprj/RISCV_RB.srcs/sources_1/bd/RISCV_RB_bd/hdl/RISCV_RB_bd_wrapper.vhd] -no_script -reset -force -quiet
        # remove_files  D:/HDLGen-ChatGPT/User_Projects/Fearghal_November/RISCV_RB/VHDL/AMDprj/RISCV_RB.srcs/sources_1/bd/RISCV_RB_bd/hdl/RISCV_RB_bd_wrapper.vhd
        # file delete -force D:/HDLGen-ChatGPT/User_Projects/Fearghal_November/RISCV_RB/VHDL/AMDprj/RISCV_RB.srcs/sources_1/bd/RISCV_RB_bd/hdl/RISCV_RB_bd_wrapper.vhd
        # update_compile_order -fileset sources_1

        # export_ip_user_files -of_objects  [get_files D:/HDLGen-ChatGPT/User_Projects/Fearghal_November/RISCV_RB/VHDL/AMDprj/RISCV_RB.srcs/sources_1/bd/RISCV_RB_bd/RISCV_RB_bd.bd] -no_script -reset -force -quiet
        # remove_files  D:/HDLGen-ChatGPT/User_Projects/Fearghal_November/RISCV_RB/VHDL/AMDprj/RISCV_RB.srcs/sources_1/bd/RISCV_RB_bd/RISCV_RB_bd.bd
        # file delete -force D:/HDLGen-ChatGPT/User_Projects/Fearghal_November/RISCV_RB/VHDL/AMDprj/RISCV_RB.srcs/sources_1/bd/RISCV_RB_bd
        # update_compile_order -fileset sources_1 // this wont cause a fail but also isn't neccessary.

    if generate_new_bd_design:

        created_signals = [] # This is an array of all signals that are created (this is cos >32 bit signals are divided)

        # (3) Create a new BD File
        file_contents += f"\ncreate_bd_file {bd_filename}"              # Create a new BD
        if gui_application:
                gui_application.add_to_log_box(f"\nCreating Block Design: {bd_filename}")
        
        
        # (4) Add Processor to BD
        file_contents += "\nadd_processing_unit"                        # Import Processing Unit to the BD
        if gui_application:
                gui_application.add_to_log_box(f"\nAdding Processing Unit")
        

        # (5) Add User Created Model to BD
        file_contents += "\nset_property source_mgmt_mode All [current_project]"    # Setting automatic mode for source management
        file_contents += f"\nadd_module {module_source} {module_source}_0"  # Import the user-created module
        if gui_application:
                gui_application.add_to_log_box(f"\nImporting Module: {module_source}")
        
        # Running this as safety
        file_contents += "\nupdate_compile_order -fileset sources_1"
        file_contents += "\nupdate_compile_order -fileset sim_1"

        # Just before (6) we need to make any port that will use I/O an external port.
        # Before connecting to GPIO, make pin external if needed.
        # It should also only be completed if the io_map is supplied
        if io_map:

            if gui_application:
                gui_application.add_to_log_box(f"\nIO Map Present: {io_map}")
        

            # io_configuration = {
            #     "led0":"count[0]",
            #     "led1":"count[1]",
            #     "led2":"TC",
            #     "led3":"None"
            # }
            # Goal: ["count", "TC"] <= we then make these external
            
            io_config_values = io_map.values()  # Take values from dictionary
            io_config_values = [item for item in io_config_values if item != "None"] # Remove all instances of "None"

            ports_to_make_external = []
            for value in io_config_values:
                if value.endswith(']'):
                    res_set = value.split('[')  # Remove [x] from end if present. We can't make individual bits from a signal external. Only entire signal.
                    ports_to_make_external.append(res_set[0])
                else:
                    ports_to_make_external.append(value)

            # Remove duplicates ["count", "count", "TC"]
            ports_to_make_external = list(set(ports_to_make_external))

            # print(ports_to_make_external) # 

            for port in ports_to_make_external:
                # Make port external
                file_contents += f"\nmake_external_connection {module_source}_0 {port} {port + '_ext'}"

            # Each connection must then be added to the XDC file.
            # print(io_map)
            for key, value in io_map.items():
                if value == 'None':
                    # If there is no connection selected for the IO, skip to the next IO
                    continue

                if value.endswith(']'): # if it ends with ] then its > 1 bits.
                    split = value.split("[")
                    board_gpio = key
                    external_connection_pin = split[0] + "_ext[" + split[1]
                    xdc_contents += add_line_to_xdc(board_gpio, external_connection_pin)
                else:
                    xdc_contents += add_line_to_xdc(key, value+"_ext")


        # (6) Add AXI GPIO for each input/output
        for io in all_ports:
            gpio_name = io[0]   # GPIO Name
            gpio_mode = io[1]   # GPIO Mode (in/out)
            gpio_type = io[2]   # GPIO Type (single bit/bus/array)

            # New Notes for New Feature:
            # Tcl commands to create external connection and to rename the connection
            # startgroup
            # make_bd_pins_external  [get_bd_pins CB4CLED_0/count]
            # endgroup
            # connect_bd_net [get_bd_pins count/gpio_io_i] [get_bd_pins CB4CLED_0/count]
            # set_property name NEWNAME [get_bd_ports count_0]
            # dunno what makegroup does but no need worry about it
                
            # Implemented as proc make_external_connection {component bd_pin external_pin_name}

            if (gpio_type == "single bit"):
                gpio_width = 1
            elif (gpio_type[:3] == "bus"):
                # <type>bus(31 downto 0)</type>     ## Example Type Value
                substring = gpio_type[4:]           # substring = '31 downto 0)'
                words = substring.split()           # words = ['31', 'downto', '0)']
                gpio_width = int(words[0]) + 1           # words[0] = 31
            elif (gpio_type[:5] == "array"):
                print("ERROR: Array mode type is not yet supported :(")
            else:
                print("ERROR: Unknown GPIO Type")
                print(gpio_type)


            if gpio_mode == "out" and int(gpio_width) <= 32:
                print(gpio_name) 
                file_contents += f"\nadd_axi_gpio_all_input {gpio_name} {gpio_width}"
                # If the GPIO is added correctly, connect it to the User I/O
                file_contents += f"\nconnect_gpio_all_input_to_module_port {gpio_name} {module_source}_0"
                created_signals.append(gpio_name)
            elif gpio_mode == "in" and int(gpio_width) <= 32:
                file_contents += f"\nadd_axi_gpio_all_output {gpio_name} {gpio_width}"
                # If the GPIO is added correctly, connect it to the User I/O
                file_contents += f"\nconnect_gpio_all_output_to_module_port {gpio_name} {module_source}_0"
                created_signals.append(gpio_name)
            elif gpio_mode == "out" and int(gpio_width) > 32:
                print(gpio_name + " is greater than 32 bits. I/O will be split.")
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
                    created_signals.append(sub_sig[0])

            elif gpio_mode == "in" and int(gpio_width) > 32:
                print(gpio_name + " is greater than 32 bits. I/O will be split.")
                gpio_width_int = int(gpio_width)
                
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
                    created_signals.append(sub_sig[0]) 

            else:
                print("Error Adding GPIO Connection, in/out not specified correctly")
                break

        # (7) Add the AXI Interconnect to the IP Block Design
        file_contents += f"\nadd_axi_interconnect 1 {len(created_signals)}"

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
        
        ## IF BLOCK ENDS

    # (11) Create HDL Wrapper and set created wrapper as top

    file_contents += create_vhdl_wrapper(bd_filename, path_to_bd) 

    path_to_bd_export = environment + "/" + AMDproj_folder_rel_path + "/" + bd_filename + ".tcl"   # hotfix changed to environment
    path_to_bd_file = f"{path_to_bd}/{bd_filename}/{bd_filename}.bd"

    file_contents += generate_bitstream(path_to_bd_export,path_to_bd_file)
    file_contents += save_and_quit(start_gui, keep_vivado_open)
    write_tcl_file(file_contents, gui_application)
    write_xdc_file(file_contents, gui_application)

    #++++++++++++++++++++++++++++++++++++++++#
    #++++++++# END OF MAIN FUNCTION #++++++++#
    #++++++++++++++++++++++++++++++++++++++++#












#################################################
########## Import XDC Constraints File ##########
#################################################
def import_xdc_constraints_file(full_path_to_xdc):
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
    path_to_constraints = friendly_current_dir + "/generated/physical_constr.xdc"       # This needs to be updated with generated constraints

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
            file_contents += "\nclose_design"
            file_contents += "\nexit"
        else:
            # GUI started, and user wishes to close Vivado themselves.
            # Do nothing.
            pass
    else: # GUI not started, close project, don't run stop_gui command.
        # file_contents += "\nstop_gui"
        file_contents += "\nclose_design"
        file_contents += "\nexit"
    return file_contents

########################
#   Write to Tcl File  #
########################
def write_tcl_file(file_contents, gui_application):
    # Check does the /generated/ folder exist
    if not os.path.exists("./generated"):
        os.mkdir("generated")
        if gui_application:
            gui_application.add_to_log_box(f"\nDirectory '{os.getcwd()}/generated/' not found. Created successfully.")

    with open('generated/generate_script.tcl', 'w') as file:
        # Export Tcl Script
        file.write(file_contents)
        # print("generate_script.tcl generated!")
        if gui_application:
            gui_application.add_to_log_box(f"\nSuccessfully wrote Tcl Script to {os.getcwd()}/generated/generate_script.tcl")

########################
#   Write to XDC File  #
########################
def write_xdc_file(xdc_contents, gui_application):
    with open('generated/physical_constr.xdc', 'w') as file:
        # Export contraints file
        file.write(xdc_contents)
        if gui_application:
            gui_application.add_to_log_box(f"\nSuccessfully wrote constraints file to {os.getcwd()}/generated/physical_constr.xdc")

########################
#   Make XDC Cfg Line  #
########################
def add_line_to_xdc(board_gpio, external_pin):
    line_to_add = pynq_constraints[board_gpio]
    line_to_add = line_to_add.replace("signal_name", external_pin)
    line_to_add = "\n" + line_to_add
    line_to_add += f" # {external_pin} connection to {board_gpio}"
    return line_to_add