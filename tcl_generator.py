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

xdc_io_property_template = {
    "led0" : "set_property -dict { PACKAGE_PIN R14   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "led1" : "set_property -dict { PACKAGE_PIN P14   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "led2" : "set_property -dict { PACKAGE_PIN N16   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];",
    "led3" : "set_property -dict { PACKAGE_PIN M14   IOSTANDARD LVCMOS33 } [get_ports { signal_name }];"
}

# io_connection_dictionary = {key: None for key in io_suffix}
# {'_led': None, '_led0': None, '_led1': None, '_led2': None, '_led3': None, '_led01': None, '_led02': None, '_led03': None, '_led12': None, '_led13': None, '_led23': None}

io_dictionary = {
    'led0': None,
    'led1': None,
    'led2': None,
    'led3': None
}

# Contraints file contents:
# TODO: Add tag that this has been auto generated by PYNQ SoC Builder
xdc_contents = "" # Instanciate the xdc_contents variable

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


def generate_tcl(path_to_hdlgen_project, regenerate_bd=False, start_gui=True, keep_vivado_open=False, skip_board_config=False):

    ########## Options ##########
    experimental_import_contraints = True

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
    location = location.replace('\\', '/')
    path_to_xpr = location + "/" + AMDproj_folder_rel_path + "/" + name + ".xpr"
    bd_filename = name + "_bd"
    module_source = name
    path_to_bd = location + "/" + AMDproj_folder_rel_path + "/" + name + ".srcs/sources_1/bd"

    ########## Start of Tcl Script Generation ##########

    # (1) Source Procedures File
    current_dir = os.getcwd()
    friendly_current_dir = current_dir.replace("\\", "/")
    file_contents = "source " + friendly_current_dir + "/generated/generate_procs.tcl"  # Source the procedures
    

    # Additional Step: Set if GUI should be opened
    if start_gui:
        file_contents += "\nstart_gui"                              # Open Vivado GUI (option)


    # (2) Open Project
    file_contents += f"\nopen_project {path_to_xpr}"                # Open Project

    # Set Board Part (Project Parameter)
    if not skip_board_config:
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
        path_to_constraints = friendly_current_dir + "generated/physical_contr.xdc"       # This needs to be updated with generated contraints
        file_contents += f"\n    set path_to_constraints \"{path_to_constraints}\""
        file_contents += "\n    add_files -fileset constrs_1 -norecurse {{$path_to_constraints}}"
        file_contents += "\n    import_files -fileset constrs_1 {{$path_to_constraints}}"

        file_contents += "\n}"

        #add_files -fileset constrs_1 -norecurse {{C:/Users/canny/Documents/5th Year ECE/Project/PYNQ Board Files Complete/pynq-z2_v1.0.xdc/PYNQ-Z2 v1.0.xdc}}
        #import_files -fileset constrs_1 {{C:/Users/canny/Documents/5th Year ECE/Project/PYNQ Board Files Complete/pynq-z2_v1.0.xdc/PYNQ-Z2 v1.0.xdc}}
        

    #########################################################################################################
    
    ################### Experimental Check if Block Design Exists (and a Wrapper Exists) ####################

    generate_new_bd_design = regenerate_bd   # Default Consignment
    delete_old_bd_design = False             # Default Consignment

    # Need to check if block design actually exists already,
    # And does a wrapper exist
    
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

    if (wrapper_exists and bd_exists):
        print("-> Wrapper and BD exist")
        if regenerate_bd:
            print("-> New Wrapper and BD will be generated!")
            delete_old_bd_design = True
        else:
            print("-> Generating bitstream using existing BD/Wrapper")
            generate_new_bd_design = False

    elif (not wrapper_exists and bd_exists):
        print("-> WARNING: Wrapper does not exist, BD does exist")
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
        # (3) Create a new BD File
        file_contents += f"\ncreate_bd_file {bd_filename}"              # Create a new BD

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

            if gpio_mode == "out":
                
                ####### Detected the Suffix of the Signal and Connecting I/O
                # proc make_external_connection {component bd_pin external_pin_name}
                
                #run_external_connection(#)
                
                # First: 
                # io_suffix = ["_led", "_led0", "_led1", "_led2", "_led3", "_led01", "_led02", "_led03", "_led12", "_led13", "_led23", "_led3"]
                suffix_detected = None
                for suff in io_suffix:
                    if gpio_name.endswith(suff):
                        suffix_detected = suff
                if suffix_detected:
                    if suffix_detected == io_suffix[0]: #   _led
                        # Automatic assignment
                        # io_dictionary = {
                        #     'led0': None,
                        #     'led1': None,
                        #     'led2': None,
                        #     'led3': None
                        # }
                        
                        # Count the number of LED IO available.
                        count = sum(value == None for value in io_dictionary.values())
                        if count > gpio_width:
                            print(f"The GPIO signal is greater the # of LED pins available - Assigning {count} LSBs.")
                        
                        external_connection = gpio_name + "_ext"
                        file_contents += "run_external_connection {module_source} {gpio_name} {external_connection}"

                        connections_made = 0
                        for key in io_dictionary.keys():    # Cycle thru each key in io dictionary
                            if io_dictionary[key] == None:  # If the I/O is available:
                                board_gpio = key
                                external_connection_pin = external_connection + "[" + connections_made + "]"
                                io_dictionary[key] == external_connection_pin               # Assign the connection (eg: "led0": "count_ext[0]")
                                add_line_to_xdc(board_gpio, external_connection_pin)        # Create connection in Physical Contraints File

                        # Opportunity: Can use the following "highest consecutive sequence" code to try fit a signal consecutively instead.
                        # for value in io_dictionary.values():
                        #     if value == value_to_check:
                        #         current_sequence += 1
                        #         max_sequence = max(max_sequence, current_sequence)
                        #     else:
                        #         current_sequence = 0
 
                        pass
                    elif suffix_detected == io_suffix[1]: # _led0
                        pass
                    elif suffix_detected == io_suffix[2]: # _led1
                        pass
                    elif suffix_detected == io_suffix[3]: # _led2
                        pass
                    elif suffix_detected == io_suffix[4]: # _led01
                        pass
                    elif suffix_detected == io_suffix[5]: # _led01
                        pass
                    elif suffix_detected == io_suffix[6]: # _led02
                        pass 
                    elif suffix_detected == io_suffix[7]: # _led03
                        pass
                    elif suffix_detected == io_suffix[8]: # _led12
                        pass
                    elif suffix_detected == io_suffix[9]: # _led13
                        pass
                    elif suffix_detected == io_suffix[10]: # _led23
                        pass
                    elif suffix_detected == io_suffix[11]: # _led3
                        pass
                    else:
                        print("ERROR: IO Out of range.")
                    






                    pass


                file_contents += f"\nadd_axi_gpio_all_input {gpio_name} {gpio_width}"
                # If the GPIO is added correctly, connect it to the User I/O
                file_contents += f"\nconnect_gpio_all_input_to_module_port {gpio_name} {module_source}_0"
            elif gpio_mode == "in":
                file_contents += f"\nadd_axi_gpio_all_output {gpio_name} {gpio_width}"
                # If the GPIO is added correctly, connect it to the User I/O
                file_contents += f"\nconnect_gpio_all_output_to_module_port {gpio_name} {module_source}_0"
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
        
        ## IF BLOCK ENDS

    # Updated workflow: Check if HDLWrapper exists:
    # If so: Delete and regenerate, if not, generate.
    # Previous workflow only regenerated if BD was generated 
    # Method does not allow user to manually change BD and regenerate using PYNQ SoC Builder
    
    # (11) Create HDL Wrapper and set created wrapper as top
    # file_contents += f"\ncreate_hdl_wrapper {path_to_bd} {bd_filename}"
    # file_contents += f"\nset_wrapper_top {bd_filename}_wrapper"

    # Example Tcl Sequence:
        # export_ip_user_files -of_objects  [get_files C:/repo/HDLGen-ChatGPT/User_Projects/CB4CLED/VHDL/AMDprj/CB4CLED.srcs/sources_1/bd/CB4CLED_bd/hdl/CB4CLED_bd_wrapper.vhd] -no_script -reset -force -quiet
        # remove_files  C:/repo/HDLGen-ChatGPT/User_Projects/CB4CLED/VHDL/AMDprj/CB4CLED.srcs/sources_1/bd/CB4CLED_bd/hdl/CB4CLED_bd_wrapper.vhd
        # file delete -force C:/repo/HDLGen-ChatGPT/User_Projects/CB4CLED/VHDL/AMDprj/CB4CLED.srcs/sources_1/bd/CB4CLED_bd/hdl/CB4CLED_bd_wrapper.vhd
        # update_compile_order -fileset sources_1

    file_contents += f"\nset wrapper_exists [file exists {path_to_bd}/{bd_filename}_wrapper.vhd]"
    file_contents += "\nif {$wrapper_exists} {"
    file_contents += f"\n    export_ip_user_files -of_objects  [get_files {path_to_bd}/{bd_filename}_wrapper.vhd] -no_script -reset -force -quiet"
    file_contents += f"\n    remove_files  {path_to_bd}/{bd_filename}_wrapper.vhd"
    file_contents += f"\n    file delete -force {path_to_bd}/{bd_filename}_wrapper.vhd"
    file_contents += f"\n    update_compile_order -fileset sources_1"
    file_contents += "\n} else {"
    file_contents += f"\n    create_hdl_wrapper {path_to_bd} {bd_filename}"
    file_contents += f"\n    set_wrapper_top {bd_filename}_wrapper"
    file_contents += "\n}"

    ########### END OF BLOCK DIAGRAM / WRAPPER CREATION ########### 


    # (12) Run Synthesis, Implementation and Generate Bitstream
    file_contents += "\ngenerate_bitstream"
    # C:/masters/masters_automation/cb4cled-jn-application_automatic/CB4CLED/vhdl/xilinxprj/automated_bd.tcl

    path_to_bd_export = location + "/" + AMDproj_folder_rel_path + "/" + bd_filename + ".tcl"

    # If BD isn't open, export will fail.
    file_contents += f"\nopen_bd_design {path_to_bd}/{bd_filename}/{bd_filename}.bd"
    file_contents += f"\nexport_bd {path_to_bd_export}"
    
    # (13) Save and Quit
    file_contents += "\nwait_on_run impl_1"

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

    
    ########## Writing to generate_script.tcl ##########
    with open('generated/generate_script.tcl', 'w') as file:
        # Export Tcl Script
        file.write(file_contents)
        # print("generate_script.tcl generated!")

def add_line_to_xdc(board_gpio, external_pin):
    line_to_add = xdc_io_property_template[board_gpio]
    line_to_add.replace("signal_name", external_pin)
    xdc_contents += "\n" + line_to_add
    xdc_contents += f" # {external_pin} connection to {board_gpio}"



def export_xdc_file():
    with open('generated/physical_contr.xdc', 'w') as file:
        # Export contraints file
        file.write(xdc_contents)