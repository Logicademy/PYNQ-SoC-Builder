source C:/masters/masters_automation/generate_procs.tcl
start_gui
open_project C:/masters/masters_automation/cb4cled-jn-application_automatic/CB4CLED/vhdl/xilinxprj/CB4CLED_Top.xpr
create_bd_file automated_bd
add_processing_unit
set_property source_mgmt_mode All [current_project]
add_module CB4CLED_Top CB4CLED_Top_0
update_compile_order -fileset sources_1
update_compile_order -fileset sim_1
add_axi_gpio_all_output clk 1
connect_gpio_all_output_to_module_port clk CB4CLED_Top_0
add_axi_gpio_all_output rst 1
connect_gpio_all_output_to_module_port rst CB4CLED_Top_0
add_axi_gpio_all_output load 1
connect_gpio_all_output_to_module_port load CB4CLED_Top_0
add_axi_gpio_all_output up 1
connect_gpio_all_output_to_module_port up CB4CLED_Top_0
add_axi_gpio_all_output ce 1
connect_gpio_all_output_to_module_port ce CB4CLED_Top_0
add_axi_gpio_all_output loadDat 4
connect_gpio_all_output_to_module_port loadDat CB4CLED_Top_0
add_axi_gpio_all_input ceo 1
connect_gpio_all_input_to_module_port ceo CB4CLED_Top_0
add_axi_gpio_all_input TC 1
connect_gpio_all_input_to_module_port TC CB4CLED_Top_0
add_axi_gpio_all_input count 4
connect_gpio_all_input_to_module_port count CB4CLED_Top_0
add_axi_interconnect 1 9
connect_bd_intf_net -boundary_type upper [get_bd_intf_pins axi_interconnect_0/M00_AXI] [get_bd_intf_pins clk/S_AXI]
connect_bd_intf_net -boundary_type upper [get_bd_intf_pins axi_interconnect_0/M01_AXI] [get_bd_intf_pins rst/S_AXI]
connect_bd_intf_net -boundary_type upper [get_bd_intf_pins axi_interconnect_0/M02_AXI] [get_bd_intf_pins load/S_AXI]
connect_bd_intf_net -boundary_type upper [get_bd_intf_pins axi_interconnect_0/M03_AXI] [get_bd_intf_pins up/S_AXI]
connect_bd_intf_net -boundary_type upper [get_bd_intf_pins axi_interconnect_0/M04_AXI] [get_bd_intf_pins ce/S_AXI]
connect_bd_intf_net -boundary_type upper [get_bd_intf_pins axi_interconnect_0/M05_AXI] [get_bd_intf_pins loadDat/S_AXI]
connect_bd_intf_net -boundary_type upper [get_bd_intf_pins axi_interconnect_0/M06_AXI] [get_bd_intf_pins ceo/S_AXI]
connect_bd_intf_net -boundary_type upper [get_bd_intf_pins axi_interconnect_0/M07_AXI] [get_bd_intf_pins TC/S_AXI]
connect_bd_intf_net -boundary_type upper [get_bd_intf_pins axi_interconnect_0/M08_AXI] [get_bd_intf_pins count/S_AXI]
connect_bd_intf_net [get_bd_intf_pins processing_system7_0/M_AXI_GP0] -boundary_type upper [get_bd_intf_pins axi_interconnect_0/S00_AXI]
run_bd_automation_rule processing_system7_0/M_AXI_GP0_ACLK
run_bd_automation_rule axi_interconnect_0/ACLK
run_bd_automation_rule clk/s_axi_aclk
run_bd_automation_rule rst/s_axi_aclk
run_bd_automation_rule load/s_axi_aclk
run_bd_automation_rule up/s_axi_aclk
run_bd_automation_rule ce/s_axi_aclk
run_bd_automation_rule loadDat/s_axi_aclk
run_bd_automation_rule ceo/s_axi_aclk
run_bd_automation_rule TC/s_axi_aclk
run_bd_automation_rule count/s_axi_aclk
run_bd_block_automation
run_addr_editor_auto_assign
validate_bd
create_hdl_wrapper C:/masters/masters_automation/cb4cled-jn-application_automatic/CB4CLED/vhdl/xilinxprj/CB4CLED_Top.srcs/sources_1/bd automated_bd
set_wrapper_top automated_bd_wrapper
generate_bitstream
export_bd