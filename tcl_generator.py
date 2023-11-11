# tcl_generator.py
# This Python 3 script is responsible for generating a Tcl script file dynamically depending on the project.

# Author: Luke Canny
# Date: 12/10/23

# Run this in the Vivado Tcl Command Line
# source C:/masters/masters_automation/generate_script.tcl

# In Windows CMD:
# D:\Xilinx\Vivado\2019.1\bin\vivado.bat -mode tcl -source C:/masters/masters_automation/generate_script.tcl
# /path/to/vivado/bat -mode tcl -source /path/to/generate_script.tcl

import xml.dom.minidom
import os

# Configurable Variables
start_gui = True
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


def generate_tcl(path_to_hdlgen_project):
    ########## Parsing .hdlgen file for required information ##########
    hdlgen = xml.dom.minidom.parse(path_to_hdlgen_project)
    root = hdlgen.documentElement

    # Project Manager - Settings
    projectManager = root.getElementsByTagName("projectManager")[0]
    projectManagerSettings = projectManager.getElementsByTagName("settings")[0]
    name = projectManagerSettings.getElementsByTagName("name")[0].firstChild.data
    environment = projectManagerSettings.getElementsByTagName("environment")[0].firstChild.data
    location = projectManagerSettings.getElementsByTagName("location")[0].firstChild.data

    # genFolder - VHDL Folders
    genFolder = root.getElementsByTagName("genFolder")[0]
    model_folder = genFolder.getElementsByTagName("vhdl_folder")[0]
    testbench_folder = genFolder.getElementsByTagName("vhdl_folder")[1]
    # ChatGPT_folder = genFolder.getElementsByTagName("vhdl_folder")[2]             # Commented as not needed
    # ChatGPT_Backups_folder = genFolder.getElementsByTagName("vhdl_folder")[3]     # Commented as not needed
    AMDproj_folder = genFolder.getElementsByTagName("vhdl_folder")[4]
    AMDproj_folder_rel_path = AMDproj_folder.firstChild.data

    # hdlDesign - entityIOPorts
    hdlDesign = root.getElementsByTagName("hdlDesign")[0]
    entityIOPorts = hdlDesign.getElementsByTagName("entityIOPorts")[0]
    signals = entityIOPorts.getElementsByTagName("signal")

    all_ports = []
    for sig in signals:
        signame = sig.getElementsByTagName("name")[0]
        mode = sig.getElementsByTagName("mode")[0]
        type = sig.getElementsByTagName("type")[0]
        desc = sig.getElementsByTagName("description")[0]
        all_ports.append(
            [signame.firstChild.data, mode.firstChild.data, type.firstChild.data, desc.firstChild.data]
        )

    # Derived Variables
    path_to_xpr = location + "/" + AMDproj_folder_rel_path + "/" + name + ".xpr"
    bd_filename = name + "_bd"
    module_source = name
    path_to_bd = location + "/" + AMDproj_folder_rel_path + "/" + name + ".srcs/sources_1/bd"

    ########## Start of Tcl Script Generation ##########

    # (1) Source Procedures File
    current_dir = os.getcwd()
    friendly_current_dir = current_dir.replace("\\", "/")
    file_contents = "source " + friendly_current_dir + "/generate_procs.tcl"  # Source the procedures
    
    # Additional Step: Set if GUI should be opened
    if start_gui:
        file_contents += "\nstart_gui"                              # Open Vivado GUI (option)


    # (2) Open Project
    file_contents += f"\nopen_project {path_to_xpr}"                # Open Project


    ################################ Experimental Block for Board Contraints ################################
    
    # Run Experimental Blocks ?
    experimental_board_config = True
    experimental_import_contraints = True
    print(f"Experimental Board Configuration: {experimental_board_config}")
    print(f"Experimental Import Constraints: {experimental_import_contraints}")

    # Set Board Part (Project Parameter)
    if experimental_board_config:
        file_contents += f"\nset_property board_part tul.com.tw:pynq-z2:part0:1.0 [current_project]"

    # Import Board Constraints
    if experimental_import_contraints:
        ## Need to find a way to check if the contraints already exist - if we learned Tcl error handling we could just always attempt to add it.

        # Specify the name of the constraint
        file_contents += "\nset constraint_name \"constr_1\""

        # Check if the constraint exists
        file_contents += "\nset constraint_exists [catch {"
        file_contents += "\n    get_property -quiet $constraint_name [get_constraints]"
        file_contents += "\n} result]"

        file_contents += "\nif {$constraint_exists} {"
        file_contents += "\n    puts \"Constraint $constraint_name exists - Skipping Step\""
        file_contents += "\n} else {"
        file_contents += "\n    puts \"Constraint $constraint_name does not exist - Importing Constraints.\""
        
        # Constaints do not exist - Import now:
        path_to_constraints = friendly_current_dir + "/pynq-z2_v1.0.xdc/PYNQ-Z2 v1.0.xdc"
        file_contents += f"\n    set path_to_constraints \"{path_to_constraints}\""
        file_contents += "\n    add_files -fileset constrs_1 -norecurse {{$path_to_constraints}}"
        file_contents += "\n    import_files -fileset constrs_1 {{$path_to_constraints}}"

        file_contents += "\n}"

        #add_files -fileset constrs_1 -norecurse {{C:/Users/canny/Documents/5th Year ECE/Project/PYNQ Board Files Complete/pynq-z2_v1.0.xdc/PYNQ-Z2 v1.0.xdc}}
        #import_files -fileset constrs_1 {{C:/Users/canny/Documents/5th Year ECE/Project/PYNQ Board Files Complete/pynq-z2_v1.0.xdc/PYNQ-Z2 v1.0.xdc}}
        

    #########################################################################################################
    
    ################### Experimental Check if Block Design Exists (and a Wrapper Exists) ####################

    # Run Experimental Code ?
    experimental_block_design_checks = False
    if experimental_block_design_checks:
        pass

    
    # (3) Create a new BD File
    file_contents += f"\ncreate_bd_file {bd_filename}"              # Create a new BD

    #########################################################################################################

    # (4) Add Processor to BD
    file_contents += "\nadd_processing_unit"                        # Import Processing Unit to the BD

    # (5) Add User Created Model to BD
    file_contents += "\nset_property source_mgmt_mode All [current_project]"    # Setting automatic mode for source management
    file_contents += f"\nadd_module {module_source} {module_source}_0"  # Import the user-created module

    # Running this as safety
    file_contents += "\nupdate_compile_order -fileset sources_1"
    file_contents += "\nupdate_compile_order -fileset sim_1"

    # (6) Add AXI GPIO for each input/output
    for io in all_ports:
        gpio_name = io[0]   # GPIO Name
        gpio_mode = io[1]   # GPIO Mode (in/out)
        gpio_type = io[2]   # GPIO Type (single bit/bus/array)

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

        if gpio_mode == "out":
            file_contents += f"\nadd_axi_gpio_all_input {gpio_name} {gpio_width}"
            # If the GPIO is added correctly, connect it to the User I/O
            file_contents += f"\nconnect_gpio_all_input_to_module_port {io[0]} {module_source}_0"
        elif gpio_mode == "in":
            file_contents += f"\nadd_axi_gpio_all_output {gpio_name} {gpio_width}"
            # If the GPIO is added correctly, connect it to the User I/O
            file_contents += f"\nconnect_gpio_all_output_to_module_port {io[0]} {module_source}_0"
        else:
            print("Error Adding GPIO Connection, in/out not specified correctly")
            break

    # (7) Add the AXI Interconnect to the IP Block Design
    file_contents += f"\nadd_axi_interconnect 1 {len(all_ports)}"

    # Connect each GPIO to the Interconnect
    for x in range(len(all_ports)):
        file_contents += f"\nconnect_bd_intf_net -boundary_type upper [get_bd_intf_pins axi_interconnect_0/M{x:02d}_AXI] [get_bd_intf_pins {all_ports[x][0]}/S_AXI]"
		

    # (8) Add "Processor System Reset" IP
    file_contents += "\nadd_system_reset_ip"
    # Connect M_AXI_GP0 of the Processing System to S00_AXI connection of the AXI Interconnect.
    # TODO: Add this line to the proc file instead maybe
    file_contents += "\nconnect_bd_intf_net [get_bd_intf_pins processing_system7_0/M_AXI_GP0] -boundary_type upper [get_bd_intf_pins axi_interconnect_0/S00_AXI]"

    # Run auto-connection tool
    # file_contents += "\nrun_bd_auto_connect"
    file_contents += "\nrun_bd_automation_rule_processor"
    file_contents += "\nrun_bd_automation_rule_interconnect"
    for io in all_ports:
        file_contents += f"\nrun_bd_automation_rule_io {io[0]}/s_axi_aclk" 
    

    # Run block automation tool
    file_contents += "\nrun_bd_block_automation"

    # (9) Populate Memory Information
    file_contents += "\nrun_addr_editor_auto_assign"
    
    # (10) Validate the Block Diagram
    file_contents += "\nvalidate_bd"
    
    # (11) Create HDL Wrapper and set created wrapper as top
    file_contents += f"\ncreate_hdl_wrapper {path_to_bd} {bd_filename}"
    file_contents += f"\nset_wrapper_top {bd_filename}_wrapper"

    # (12) Run Synthesis, Implementation and Generate Bitstream
    file_contents += "\ngenerate_bitstream"
    file_contents += "\nexport_bd"
    
    # (13) Save and Quit
    file_contents += "\nwait_on_run impl_1"
    file_contents += "\nstop_gui"
    file_contents += "\nclose_design"
    file_contents += "\nexit"
    
    ########## Writing to generate_script.tcl ##########
    with open('generate_script.tcl', 'w') as file:
        # First, we want to source our test file
        file.write(file_contents)
        # print("generate_script.tcl generated!")
    
    
    

# generate_tcl("C:\\masters\\masters_automation\\LukeAND_working\\LukeAND\\HDLGenPrj\\LukeAND.hdlgen")
# source C:/masters/masters_automation/generate_script.tcl