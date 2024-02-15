#
# generate_procs.tcl
#
# Date: 28/09/23
# Author: Luke Canny
#

# Open Vivado Project given path to xpr file.
proc open_vivado_project {path_to_project_xpr} {
	open_project $path_to_project_xpr
	update_compile_order -fileset sources_1
}

# Creates a new BD file
# If file already exists, message is printed and no action is taken.
proc create_bd_file {bd_filename} {
	if {[file exists $bd_filename]} {
		puts "$bd_filename exists."
	} else {
		puts "$bd_filename does not exist. Creating..."
		create_bd_design $bd_filename
		update_compile_order -fileset sources_1
		puts "$bd_filename created."
	}
}

# Imports ZYNQ7 Processing System to BD
proc add_processing_unit {} {

	startgroup
	create_bd_cell -type ip -vlnv xilinx.com:ip:processing_system7:5.5 processing_system7_0
	endgroup
	
}

# Add user created module to project
# Inputs:
# 	module_source: name of module to be added.
#	module_name: name to be given to the module within the BD.
proc add_module {module_source module_name} {
	
	startgroup
	create_bd_cell -type module -reference $module_source $module_name
	endgroup
	
}

# Add AXI GPIO IP Component to the BD
# Input:
#	name: name to be given to the module within the BD
#	gpio_width: width of gpio bus {bits}
#	all_input: boolean, 1 for ALL INPUT, 0 for ALL OUTPUT
proc add_axi_gpio_all_input {gpio_name gpio_width} {
	startgroup
	create_bd_cell -type ip -vlnv xilinx.com:ip:axi_gpio:2.0 $gpio_name
	set_property -dict [list CONFIG.C_GPIO_WIDTH $gpio_width CONFIG.C_ALL_INPUTS {1}] [get_bd_cells $gpio_name]
	endgroup
}
proc add_axi_gpio_all_output {gpio_name gpio_width} {
	startgroup
	create_bd_cell -type ip -vlnv xilinx.com:ip:axi_gpio:2.0 $gpio_name
	set_property -dict [list CONFIG.C_GPIO_WIDTH $gpio_width CONFIG.C_ALL_OUTPUTS {1}] [get_bd_cells $gpio_name]
	endgroup
}

# Connect AXI GPIO to Module Port
# Input:
#	gpio_name: name of GPIO {or name of port on the module} - NB MUST BE THE SAME NAME.
#	module_name: name of user imported module to connect GPIO to.
proc connect_gpio_all_output_to_module_port {gpio_name module_name} {
	connect_bd_net [get_bd_pins $gpio_name/gpio_io_o] [get_bd_pins $module_name/$gpio_name]
}
# TODO: This doesn't need to be two different procedures. I would like to add a check to determine if input or output instead.
proc connect_gpio_all_input_to_module_port {gpio_name module_name} {
	connect_bd_net [get_bd_pins $gpio_name/gpio_io_i] [get_bd_pins $module_name/$gpio_name]
}

# Add AXI Interconnect
# Input:
# 	num_slave: number of slave interfaces on interconnect
#	num_master: number of master interfaces on interconnect
proc add_axi_interconnect {num_slave num_master} {
	startgroup
	create_bd_cell -type ip -vlnv xilinx.com:ip:axi_interconnect:2.1 axi_interconnect_0
	endgroup
	set_property -dict [list CONFIG.NUM_SI $num_slave CONFIG.NUM_MI $num_master] [get_bd_cells axi_interconnect_0]
}

# Connect AXI Interconnect to Processing System
#
#
#
#
proc connect_interconnect_to_processing_sys {} {


}

# Add "Processor System Reset IP"
#
#
#
proc add_system_reset_ip {} {
	startgroup
	create_bd_cell -type ip -vlnv xilinx.com:ip:proc_sys_reset:5.0 proc_sys_reset_0
	endgroup
}

# Run Auto-Connection Tool in Vivado
proc run_bd_auto_connect {} {
	# Hard Coding for the CB4CLED Example First
	startgroup
	apply_bd_automation -rule xilinx.com:bd_rule:clkrst -config {Clk "/processing_system7_0/FCLK_CLK0 (50 MHz)" }  [get_bd_pins processing_system7_0/M_AXI_GP0_ACLK]
	apply_bd_automation -rule xilinx.com:bd_rule:clkrst -config {Clk "/processing_system7_0/FCLK_CLK0 (50 MHz)" }  [get_bd_pins clk/s_axi_aclk]
	apply_bd_automation -rule xilinx.com:bd_rule:clkrst -config {Clk "/processing_system7_0/FCLK_CLK0 (50 MHz)" }  [get_bd_pins rst/s_axi_aclk]
	apply_bd_automation -rule xilinx.com:bd_rule:clkrst -config {Clk "/processing_system7_0/FCLK_CLK0 (50 MHz)" }  [get_bd_pins load/s_axi_aclk]
	apply_bd_automation -rule xilinx.com:bd_rule:clkrst -config {Clk "/processing_system7_0/FCLK_CLK0 (50 MHz)" }  [get_bd_pins up/s_axi_aclk]
	apply_bd_automation -rule xilinx.com:bd_rule:clkrst -config {Clk "/processing_system7_0/FCLK_CLK0 (50 MHz)" }  [get_bd_pins ce/s_axi_aclk]
	apply_bd_automation -rule xilinx.com:bd_rule:clkrst -config {Clk "/processing_system7_0/FCLK_CLK0 (50 MHz)" }  [get_bd_pins loadDat/s_axi_aclk]
	apply_bd_automation -rule xilinx.com:bd_rule:clkrst -config {Clk "/processing_system7_0/FCLK_CLK0 (50 MHz)" }  [get_bd_pins ceo/s_axi_aclk]
	apply_bd_automation -rule xilinx.com:bd_rule:clkrst -config {Clk "/processing_system7_0/FCLK_CLK0 (50 MHz)" }  [get_bd_pins TC/s_axi_aclk]
	apply_bd_automation -rule xilinx.com:bd_rule:clkrst -config {Clk "/processing_system7_0/FCLK_CLK0 (50 MHz)" }  [get_bd_pins count/s_axi_aclk]
	apply_bd_automation -rule xilinx.com:bd_rule:clkrst -config {Clk "/processing_system7_0/FCLK_CLK0 (50 MHz)" }  [get_bd_pins axi_interconnect_0/ACLK]
	endgroup
}

# Running on the Processor:
# apply_bd_automation -rule xilinx.com:bd_rule:clkrst -config {Clk "/processing_system7_0/FCLK_CLK0 (50 MHz)" }  [get_bd_pins processing_system7_0/M_AXI_GP0_ACLK]

# Running on the Interconnect:
# apply_bd_automation -rule xilinx.com:bd_rule:clkrst -config {Clk "/processing_system7_0/FCLK_CLK0 (50 MHz)" }  [get_bd_pins axi_interconnect_0/ACLK]

# On all the remaining I/O
# apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config { Clk_master {/processing_system7_0/FCLK_CLK0 (50 MHz)} Clk_slave {Auto} Clk_xbar {/processing_system7_0/FCLK_CLK0 (50 MHz)} Master {/processing_system7_0/M_AXI_GP0} Slave {/ANDOut/S_AXI} intc_ip {/axi_interconnect_0} master_apm {0}}  [get_bd_intf_pins ANDOut/S_AXI]

proc run_bd_automation_rule_processor {} {
	apply_bd_automation -rule xilinx.com:bd_rule:clkrst -config {Clk "/processing_system7_0/FCLK_CLK0 (50 MHz)" }  [get_bd_pins processing_system7_0/M_AXI_GP0_ACLK]
}

proc run_bd_automation_rule_interconnect {} {
	apply_bd_automation -rule xilinx.com:bd_rule:clkrst -config {Clk "/processing_system7_0/FCLK_CLK0 (50 MHz)" }  [get_bd_pins axi_interconnect_0/ACLK]
}

proc run_bd_automation_rule_io {bd_pin} {
	apply_bd_automation -rule xilinx.com:bd_rule:clkrst -config {Clk "/processing_system7_0/FCLK_CLK0 (50 MHz)" }  [get_bd_pins $bd_pin]
}


# Run Block Automation {for use after connection automation}
proc run_bd_block_automation {} {
	apply_bd_automation -rule xilinx.com:bd_rule:processing_system7 -config {make_external "FIXED_IO, DDR" apply_board_preset "1" Master "Disable" Slave "Disable" }  [get_bd_cells processing_system7_0]
}

# Auto Assignment Memory Addresses
proc run_addr_editor_auto_assign {} {
	assign_bd_address
}

# Validate Block Design
proc validate_bd {} {
	validate_bd_design
}

# Create HDL Wrapper
proc create_hdl_wrapper {path_to_bd bd_filename} {
	# C:/masters/masters_automation/cb4cled-jn-application_automatic/CB4CLED/vhdl/xilinxprj/CB4CLED_Top.srcs/sources_1/bd/automated_bd/automated_bd.bd
	# C:/masters/masters_automation/cb4cled-jn-application_automatic/CB4CLED/vhdl/xilinxprj/CB4CLED_Top.srcs/sources_1/bd/automated_bd/hdl/automated_bd_wrapper.vhd
	make_wrapper -files [get_files $path_to_bd/${bd_filename}/${bd_filename}.bd] -top 
	add_files -norecurse ${path_to_bd}/${bd_filename}/hdl/${bd_filename}_wrapper.vhd
	update_compile_order -fileset sources_1
}

# Set the VHDL wrapper as top.
proc set_wrapper_top {wrapper_name} {
	set_property top $wrapper_name [current_fileset]
	update_compile_order -fileset sources_1
}

# Generate Bitstream - synth_2 and impl_2 used in counter program but these should both be "_1"
proc generate_bitstream {} {	
	reset_run synth_1
	launch_runs impl_1 -to_step write_bitstream -jobs 2
}



proc export_bd {bd_tcl_path} {
	write_bd_tcl -force $bd_tcl_path
}


# Close project and Quit Vivado.
proc close_and_quit {} {
	close_project
	exit
}

proc delete_file {path_to_file} {
	export_ip_user_files -of_objects  [get_files $path_to_file] -no_script -reset -force -quiet
	remove_files  $path_to_file
	file delete -force $path_to_file
	update_compile_order -fileset sources_1 
}

proc make_external_connection {component bd_pin external_pin_name} {
	startgroup
	make_bd_pins_external [ get_bd_pins $component/$bd_pin ]
	endgroup
	# connect_bd_net [get_bd_pins $bd_pin]
	set ext_connector $bd_pin\_0
	set_property name $external_pin_name [get_bd_ports $ext_connector]
}