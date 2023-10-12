# This file will generate a large Tcl script that will be launched automatically.

#
# Need to learn how to set the board etc etc.
#

# source C:/masters/masters_automation/generate_script.tcl

## Configurable Switches
start_gui = True
path_to_xpr = "C:/masters/masters_automation/cb4cled-jn-application_automatic/CB4CLED/vhdl/xilinxprj/CB4CLED_Top.xpr"
bd_filename = "automated_bd"

## This is the same information available in the JNB Generator file.
# Information from the header element
compName = "CB4CLED"
title = "CB4CLED"
description = "CB4CLED"
authors = "LC"
company = "University of Galway"
email = "lcanny8@gmail.com"
date = "12/10/23"

# Info from entityIOPorts -> Updated as if its for the counter project
input_ports = [
    ["clk", "in", "1", "Clock input"],
    ["rst", "in", "1", "Reset input"],
    ["load", "in", "1", "load enable input"],
    ["up", "in", "1", "up or down signal"],
    ["ce", "in", "1", "chip enable"],
    ["loadDat", "in", "4", "load 4 bit data to count"]
]

output_ports = [
    ["ceo", "out", "1", "chip enable out"],
    ["TC", "out", "1", "terminal count"],
    ["count", "out", "4", "counter value"]
]

all_ports = [
    ["clk", "in", "1", "Clock input"],
    ["rst", "in", "1", "Reset input"],
    ["load", "in", "1", "load enable input"],
    ["up", "in", "1", "up or down signal"],
    ["ce", "in", "1", "chip enable"],
    ["loadDat", "in", "4", "load 4 bit data to count"],
    ["ceo", "out", "1", "chip enable out"],
    ["TC", "out", "1", "terminal count"],
    ["count", "out", "4", "counter value"]
]

# # # Some more custom set variables that should normally be available from HDLGen
module_source = "CB4CLED_Top"


# testbench_cols = []
# for i in input_ports:
#     testbench_cols.append(i[0])
    
# for o in output_ports:
#     testbench_cols.append(o[0])

# test_cases = [
#     [0,0,0],
#     [0,1,0],
#     [1,0,0],
#     [1,1,1]
# ]

########## Start of Tcl Script Generation ##########

# 1. Source the procedures file
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



file_contents = "source C:/masters/masters_automation/generate_procs.tcl"                     # Source the procedures

if start_gui:
    file_contents += "\nstart_gui"                              # Open Vivado GUI (option)

file_contents += f"\nopen_project {path_to_xpr}"                # Open Project

file_contents += f"\ncreate_bd_file {bd_filename}"              # Create a new BD

file_contents += "\nadd_processing_unit"                        # Import Processing Unit to the BD

file_contents += "\nset_property source_mgmt_mode All [current_project]"

file_contents += f"\nadd_module {module_source} {module_source}_0"

# Running this as safety
file_contents += "\nupdate_compile_order -fileset sources_1"
file_contents += "\nupdate_compile_order -fileset sim_1"

# Adding AXI GPIO Components 
for io in all_ports:
    gpio_name = io[0]
    gpio_width = io[2]
    if io[1] == "out":
        file_contents += f"\nadd_axi_gpio_all_input {gpio_name} {gpio_width}"
        # If the GPIO is added correctly, connect it to the User I/O
        file_contents += f"\nconnect_gpio_all_input_to_module_port {io[0]} {module_source}_0"
    elif io[1] == "in":
        file_contents += f"\nadd_axi_gpio_all_output {gpio_name} {gpio_width}"
        # If the GPIO is added correctly, connect it to the User I/O
        file_contents += f"\nconnect_gpio_all_output_to_module_port {io[0]} {module_source}_0"
    else:
        print("Error Adding GPIO Connection, in/out not specified correctly")
        break
    
# Add the AXI Interconnect to the IP Block Design
file_contents += f"\nadd_axi_interconnect 1 {len(all_ports)}"

# Connect each GPIO to the Interconnect
for x in range(len(all_ports)):
    file_contents += f"\nconnect_bd_intf_net -boundary_type upper [get_bd_intf_pins axi_interconnect_0/M{x:02d}_AXI] [get_bd_intf_pins {all_ports[x][0]}/S_AXI]"
		
# Connect M_AXI_GP0 of the Processing System to S00_AXI connection of the AXI Interconnect.
# TODO: Add this line to the proc file instead maybe
file_contents += "\nconnect_bd_intf_net [get_bd_intf_pins processing_system7_0/M_AXI_GP0] -boundary_type upper [get_bd_intf_pins axi_interconnect_0/S00_AXI]"

# Run auto-connection tool
# file_contents += "\nrun_bd_auto_connect"
file_contents += "\nrun_bd_automation_rule processing_system7_0/M_AXI_GP0_ACLK"
file_contents += "\nrun_bd_automation_rule axi_interconnect_0/ACLK"
for io in all_ports:
    file_contents += f"\nrun_bd_automation_rule {io[0]}/s_axi_aclk" 

# Run block automation tool
file_contents += "\nrun_bd_block_automation"

# Run Auto Assignment Memory Addresses
file_contents += "\nrun_addr_editor_auto_assign"

# Validate the design
file_contents += "\nvalidate_bd"

# Create HDL Wrapper
file_contents += "\ncreate_hdl_wrapper"

# Set VHDL Wrapper as Top
file_contents += "\nset_wrapper_top"

# Synthesis, Implementation and Generate Bitstream
file_contents += "\ngenerate_bitstream"

# Finally, export the block diagram
file_contents += "\nexport_bd"

# Close and Quit
file_contents += "\nclose_and_quit"

########## Write to Tcl File ##########
with open('generate_script.tcl', 'w') as file:
    # First, we want to source our test file
    file.write(file_contents)



    # New lines aren't automatic.
    # file.write("Testing if this is a new line or not")

    # Need some conditional code here to get started.