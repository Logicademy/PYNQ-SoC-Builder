source C:/repo/PYNQ-SoC-Builder/application/generate_procs.tcl
start_gui
open_project C:/repo/HDLGen-ChatGPT-Latest/User_Projects/ToLuke/FIFOs/FIFO4x64Top/VHDL/AMDprj/FIFO4x64Top.xpr
set_property board_part tul.com.tw:pynq-z2:part0:1.0 [current_project]
set constraint_name "constrs_1"
set xdc_exists [file exists C:/repo/HDLGen-ChatGPT-Latest/User_Projects/ToLuke/FIFOs/FIFO4x64Top/VHDL/AMDprj/FIFO4x64Top.srcs/constrs_1/imports/generated/physical_constr.xdc]
if {$xdc_exists} {
    export_ip_user_files -of_objects  [get_files {{C:/repo/HDLGen-ChatGPT-Latest/User_Projects/ToLuke/FIFOs/FIFO4x64Top/VHDL/AMDprj/FIFO4x64Top.srcs/constrs_1/imports/generated/physical_constr.xdc}}] -no_script -reset -force -quiet
    remove_files  -fileset constrs_1 {{C:/repo/HDLGen-ChatGPT-Latest/User_Projects/ToLuke/FIFOs/FIFO4x64Top/VHDL/AMDprj/FIFO4x64Top.srcs/constrs_1/imports/generated/physical_constr.xdc}}
    file delete -force {C:/repo/HDLGen-ChatGPT-Latest/User_Projects/ToLuke/FIFOs/FIFO4x64Top/VHDL/AMDprj/FIFO4x64Top.srcs/constrs_1/imports/generated/physical_constr.xdc}
}
add_files -fileset constrs_1 -norecurse {C:/repo/PYNQ-SoC-Builder/generated/physical_constr.xdc}
import_files -force -fileset constrs_1 {C:/repo/PYNQ-SoC-Builder/generated/physical_constr.xdc}
delete_file C:/repo/HDLGen-ChatGPT-Latest/User_Projects/ToLuke/FIFOs/FIFO4x64Top/VHDL/AMDprj/FIFO4x64Top.srcs/sources_1/bd/FIFO4x64Top_bd/FIFO4x64Top_bd.bd
create_bd_file FIFO4x64Top_bd
add_processing_unit
set_property source_mgmt_mode All [current_project]
add_module FIFO4x64Top FIFO4x64Top_0
update_compile_order -fileset sources_1
update_compile_order -fileset sim_1
add_axi_gpio_all_output clk 1
connect_gpio_all_output_to_module_port clk FIFO4x64Top_0
add_axi_gpio_all_output rst 1
connect_gpio_all_output_to_module_port rst FIFO4x64Top_0
add_axi_gpio_all_output rd 1
connect_gpio_all_output_to_module_port rd FIFO4x64Top_0
add_axi_gpio_all_output wr 1
connect_gpio_all_output_to_module_port wr FIFO4x64Top_0

# add_axi_gpio_all_output dIn 64                                          ; # Problem Line
# connect_gpio_all_output_to_module_port dIn FIFO4x64Top_0                ; # Problem Line



##
## TO CONNECT AN INPUT, WE CONCAT n SIGNALS TOGETHER
##


add_axi_gpio_all_output dIn_0_31    ; # Make two separate GPIO
add_axi_gpio_all_output dIn_32_63   ; # Make two separate GPIO

# We can't "connect_gpio_all_output_to_module_port" directly, we need a concat IP.
add_concat_ip dIn_concat 2 ; # Create concat component


# Currently dealing with dIn (an ALL OUTPUT signal)
connect_bd_net [get_bd_pins dIn_0_31/gpio_io_o] [get_bd_pins dIn_concat/In0]        ; # Connect GPIO to CONCAT
connect_bd_net [get_bd_pins dIn_32_63/gpio_io_o] [get_bd_pins dIn_concat/In1]       ; # Connect GPIO to CONCAT

connect_bd_net [get_bd_pins dIn_concat/dout] [get_bd_pins FIFO4x64Top_0/dIn]        ; # Connect CONCAT to Input of component


##### This is resonably fine above now.



# Other signals that are not problematic
add_axi_gpio_all_input full 1
connect_gpio_all_input_to_module_port full FIFO4x64Top_0
add_axi_gpio_all_input empty 1
connect_gpio_all_input_to_module_port empty FIFO4x64Top_0
# End


##
## TO CONNECT AN OUTPUT, WE SLICE n SIGNALS APPART INTO SEPARATE GPIO
##


# This is all mistaken, we need to SPLIT then in the reverse. 

# add_axi_gpio_all_input dOut 64                                          ; # Problem Line
# connect_gpio_all_input_to_module_port dOut FIFO4x64Top_0                ; # Problem Line

add_axi_gpio_all_input dOut_0_31    ; # Make two separate GPIO
add_axi_gpio_all_input dOut_32_63   ; # Make two separate GPIO

# We can't "connect_gpio_all_output_to_module_port" directly, we need a concat IP.
add_concat_ip 2 dOut_concat         ; # Create the new CONCAT IP

connect_bd_net [get_bd_pins dOut_0_31/gpio_io_i] [get_bd_pins dOut_concat/In0]      ; # Connect GPIO to CONCAT
connect_bd_net [get_bd_pins dOut_32_63/gpio_io_i] [get_bd_pins dOut_concat/In1]     ; # Connect CONCAT to GPIO

connect_bd_net [get_bd_pins dOut_concat/dout] [get_bd_pins FIFO4x64Top_0/dIn]       ; # Connect Output of component to input of CONCAT













add_axi_interconnect 1 8
connect_bd_intf_net -boundary_type upper [get_bd_intf_pins axi_interconnect_0/M00_AXI] [get_bd_intf_pins clk/S_AXI]
connect_bd_intf_net -boundary_type upper [get_bd_intf_pins axi_interconnect_0/M01_AXI] [get_bd_intf_pins rst/S_AXI]
connect_bd_intf_net -boundary_type upper [get_bd_intf_pins axi_interconnect_0/M02_AXI] [get_bd_intf_pins rd/S_AXI]
connect_bd_intf_net -boundary_type upper [get_bd_intf_pins axi_interconnect_0/M03_AXI] [get_bd_intf_pins wr/S_AXI]
connect_bd_intf_net -boundary_type upper [get_bd_intf_pins axi_interconnect_0/M04_AXI] [get_bd_intf_pins dIn/S_AXI]
connect_bd_intf_net -boundary_type upper [get_bd_intf_pins axi_interconnect_0/M05_AXI] [get_bd_intf_pins full/S_AXI]
connect_bd_intf_net -boundary_type upper [get_bd_intf_pins axi_interconnect_0/M06_AXI] [get_bd_intf_pins empty/S_AXI]
connect_bd_intf_net -boundary_type upper [get_bd_intf_pins axi_interconnect_0/M07_AXI] [get_bd_intf_pins dOut/S_AXI]
add_system_reset_ip
connect_bd_intf_net [get_bd_intf_pins processing_system7_0/M_AXI_GP0] -boundary_type upper [get_bd_intf_pins axi_interconnect_0/S00_AXI]
run_bd_automation_rule_processor
run_bd_automation_rule_interconnect
run_bd_automation_rule_io clk/s_axi_aclk
run_bd_automation_rule_io rst/s_axi_aclk
run_bd_automation_rule_io rd/s_axi_aclk
run_bd_automation_rule_io wr/s_axi_aclk
run_bd_automation_rule_io dIn/s_axi_aclk
run_bd_automation_rule_io full/s_axi_aclk
run_bd_automation_rule_io empty/s_axi_aclk
run_bd_automation_rule_io dOut/s_axi_aclk
run_bd_block_automation
run_addr_editor_auto_assign
validate_bd
set wrapper_exists [file exists C:/repo/HDLGen-ChatGPT-Latest/User_Projects/ToLuke/FIFOs/FIFO4x64Top/VHDL/AMDprj/FIFO4x64Top.srcs/sources_1/bd/FIFO4x64Top_bd_wrapper.vhd]
if {$wrapper_exists} {
    export_ip_user_files -of_objects  [get_files C:/repo/HDLGen-ChatGPT-Latest/User_Projects/ToLuke/FIFOs/FIFO4x64Top/VHDL/AMDprj/FIFO4x64Top.srcs/sources_1/bd/FIFO4x64Top_bd_wrapper.vhd] -no_script -reset -force -quiet
    remove_files  C:/repo/HDLGen-ChatGPT-Latest/User_Projects/ToLuke/FIFOs/FIFO4x64Top/VHDL/AMDprj/FIFO4x64Top.srcs/sources_1/bd/FIFO4x64Top_bd_wrapper.vhd
    file delete -force C:/repo/HDLGen-ChatGPT-Latest/User_Projects/ToLuke/FIFOs/FIFO4x64Top/VHDL/AMDprj/FIFO4x64Top.srcs/sources_1/bd/FIFO4x64Top_bd_wrapper.vhd
    update_compile_order -fileset sources_1
} else {
    create_hdl_wrapper C:/repo/HDLGen-ChatGPT-Latest/User_Projects/ToLuke/FIFOs/FIFO4x64Top/VHDL/AMDprj/FIFO4x64Top.srcs/sources_1/bd FIFO4x64Top_bd
    set_wrapper_top FIFO4x64Top_bd_wrapper
}
generate_bitstream
open_bd_design C:/repo/HDLGen-ChatGPT-Latest/User_Projects/ToLuke/FIFOs/FIFO4x64Top/VHDL/AMDprj/FIFO4x64Top.srcs/sources_1/bd/FIFO4x64Top_bd/FIFO4x64Top_bd.bd
export_bd C:/repo/HDLGen-ChatGPT-Latest/User_Projects/ToLuke/FIFOs/FIFO4x64Top/VHDL/AMDprj/FIFO4x64Top_bd.tcl
wait_on_run impl_1