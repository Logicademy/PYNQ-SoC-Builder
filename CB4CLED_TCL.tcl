start_gui	;	# Open the Vivado GUI
# Open the project - Why this is set to open twice I do not yet know.
# open_project D:/Vivado/cb4cled-jn-application/CB4CLED/vhdl/xilinxprj/CB4CLED_Top.xpr
open_project D:/Vivado/cb4cled-jn-application/CB4CLED/vhdl/xilinxprj/CB4CLED_Top.xpr
# update the compile order to choose sources_1
update_compile_order -fileset sources_1
# Open Block Design
open_bd_design {D:/Vivado/cb4cled-jn-application/CB4CLED/vhdl/xilinxprj/CB4CLED_Top.srcs/sources_1/bd/cb4cled_design_z2/cb4cled_design_z2.bd}

# Create a new block design cell MODULE called CB4CLED_Top CB4CLED_Top_AUTO
create_bd_cell -type module -reference CB4CLED_Top CB4CLED_Top_AUTO
# Set location for top
set_property location {1.5 270 -116} [get_bd_cells CB4CLED_Top_AUTO]

startgroup ; # Create a group
# Add GPIO IP cell
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_gpio:2.0 axi_gpio_0
endgroup
set_property name TC [get_bd_cells axi_gpio_0]
set_property location {1 114 16} [get_bd_cells TC]

# Load
startgroup
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_gpio:2.0 axi_gpio_0
endgroup
set_property name load [get_bd_cells axi_gpio_0]

# Up
startgroup
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_gpio:2.0 axi_gpio_0
endgroup
set_property name up [get_bd_cells axi_gpio_0]

# CEO
startgroup
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_gpio:2.0 axi_gpio_0
endgroup
set_property name ceo [get_bd_cells axi_gpio_0]

# CE
startgroup
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_gpio:2.0 axi_gpio_0
endgroup
set_property name ce [get_bd_cells axi_gpio_0]

# loadDat
startgroup
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_gpio:2.0 axi_gpio_0
endgroup
set_property name loadDat [get_bd_cells axi_gpio_0]

save_bd_design ; # Save Design

# Reset
startgroup
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_gpio:2.0 axi_gpio_0
endgroup
set_property name rst [get_bd_cells axi_gpio_0]

# Clk
startgroup
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_gpio:2.0 axi_gpio_0
endgroup
set_property name clk [get_bd_cells axi_gpio_0]

# Count
startgroup
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_gpio:2.0 axi_gpio_0
endgroup
set_property name count [get_bd_cells axi_gpio_0]

# Add interconnect
startgroup
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_interconnect:2.1 axi_interconnect_0
endgroup

# Add processing system
startgroup
create_bd_cell -type ip -vlnv xilinx.com:ip:processing_system7:5.5 processing_system7_0
endgroup

# Add System Reset IP
startgroup
create_bd_cell -type ip -vlnv xilinx.com:ip:proc_sys_reset:5.0 proc_sys_reset_0
endgroup
set_property -dict [list CONFIG.C_GPIO_WIDTH {1} CONFIG.C_ALL_OUTPUTS {1}] [get_bd_cells clk]
set_property location {5 1285 -449} [get_bd_cells clk]

# Add BD Connection for clock
connect_bd_net [get_bd_pins clk/gpio_io_o] [get_bd_pins CB4CLED_Top_AUTO/clk]

# Configure block for "all outputs" as "true" and "width" equal to "1"
set_property -dict [list CONFIG.C_GPIO_WIDTH {1} CONFIG.C_ALL_OUTPUTS {1}] [get_bd_cells rst]
set_property location {5 1241 -336} [get_bd_cells rst]

# Make connection for reset pin 
connect_bd_net [get_bd_pins rst/gpio_io_o] [get_bd_pins CB4CLED_Top_AUTO/rst]

# Setting location for up and loadDat
set_property location {6 1633 -272} [get_bd_cells up]
set_property location {5 1291 -204} [get_bd_cells loadDat]

# For loadDat, set as "all outputs" true and make width = 4 bits
set_property -dict [list CONFIG.C_GPIO_WIDTH {4} CONFIG.C_ALL_OUTPUTS {1}] [get_bd_cells loadDat]
# Connect load dat.
connect_bd_net [get_bd_pins loadDat/gpio_io_o] [get_bd_pins CB4CLED_Top_AUTO/loadDat]


startgroup ; # Don't know why this was done 
endgroup
# Set the width and output for load
set_property -dict [list CONFIG.C_GPIO_WIDTH {1} CONFIG.C_ALL_OUTPUTS {1}] [get_bd_cells load]
# Make connection for load pin
connect_bd_net [get_bd_pins load/gpio_io_o] [get_bd_pins CB4CLED_Top_AUTO/load]
# Set width/output for ce pin
set_property -dict [list CONFIG.C_GPIO_WIDTH {1} CONFIG.C_ALL_OUTPUTS {1}] [get_bd_cells ce]
# Connecting ce
connect_bd_net [get_bd_pins ce/gpio_io_o] [get_bd_pins CB4CLED_Top_AUTO/ce]


set_property location {6.5 1866 -186} [get_bd_cells ceo]	; # Setting the physical location on the FPGA. 
# This is done for a reason that I do not know. Maybe these are are coded from what was observed when doing the steps manually in vivado GUI
set_property location {7 1853 -53} [get_bd_cells up]
set_property location {7 1867 108} [get_bd_cells TC]
set_property location {5 1394 220} [get_bd_cells up]
set_property location {7 1787 -339} [get_bd_cells count]
set_property location {6 1859 -29} [get_bd_cells ceo]
set_property location {6 1867 -110} [get_bd_cells TC]
set_property location {6 1874 -302} [get_bd_cells count]
set_property location {4 1335 359} [get_bd_cells TC]
set_property location {4 1329 -626} [get_bd_cells count]
set_property location {4 1347 502} [get_bd_cells ceo]

# Setting properties for count -  The output of CB4CLED which is an input for our processing system
set_property -dict [list CONFIG.C_GPIO_WIDTH {4} CONFIG.C_ALL_INPUTS {1} CONFIG.C_ALL_OUTPUTS {0}] [get_bd_cells count]
connect_bd_net [get_bd_pins count/gpio_io_i] [get_bd_pins CB4CLED_Top_AUTO/count]
# up
set_property -dict [list CONFIG.C_GPIO_WIDTH {1} CONFIG.C_ALL_OUTPUTS {1}] [get_bd_cells up]
connect_bd_net [get_bd_pins up/gpio_io_o] [get_bd_pins CB4CLED_Top_AUTO/up]
# TC
set_property -dict [list CONFIG.C_GPIO_WIDTH {1} CONFIG.C_ALL_INPUTS {1}] [get_bd_cells TC]
connect_bd_net [get_bd_pins TC/gpio_io_i] [get_bd_pins CB4CLED_Top_AUTO/TC]
# ceo
set_property -dict [list CONFIG.C_GPIO_WIDTH {1} CONFIG.C_ALL_INPUTS {1}] [get_bd_cells ceo]
connect_bd_net [get_bd_pins ceo/gpio_io_i] [get_bd_pins CB4CLED_Top_AUTO/ceo]
# Setting interconnect properties for 9 ... forgot word.
set_property -dict [list CONFIG.NUM_MI {9}] [get_bd_cells axi_interconnect_0]
connect_bd_intf_net -boundary_type upper [get_bd_intf_pins axi_interconnect_0/M00_AXI] [get_bd_intf_pins count/S_AXI]
connect_bd_intf_net -boundary_type upper [get_bd_intf_pins axi_interconnect_0/M01_AXI] [get_bd_intf_pins clk/S_AXI]
connect_bd_intf_net -boundary_type upper [get_bd_intf_pins axi_interconnect_0/M02_AXI] [get_bd_intf_pins rst/S_AXI]
connect_bd_intf_net -boundary_type upper [get_bd_intf_pins axi_interconnect_0/M03_AXI] [get_bd_intf_pins loadDat/S_AXI]
connect_bd_intf_net -boundary_type upper [get_bd_intf_pins axi_interconnect_0/M04_AXI] [get_bd_intf_pins load/S_AXI]
connect_bd_intf_net -boundary_type upper [get_bd_intf_pins axi_interconnect_0/M06_AXI] [get_bd_intf_pins ce/S_AXI]
delete_bd_objs [get_bd_intf_nets axi_interconnect_0_M06_AXI]
connect_bd_intf_net -boundary_type upper [get_bd_intf_pins axi_interconnect_0/M05_AXI] [get_bd_intf_pins ce/S_AXI]
connect_bd_intf_net -boundary_type upper [get_bd_intf_pins axi_interconnect_0/M06_AXI] [get_bd_intf_pins up/S_AXI]
connect_bd_intf_net -boundary_type upper [get_bd_intf_pins axi_interconnect_0/M07_AXI] [get_bd_intf_pins TC/S_AXI]
connect_bd_intf_net -boundary_type upper [get_bd_intf_pins axi_interconnect_0/M08_AXI] [get_bd_intf_pins ceo/S_AXI]
connect_bd_intf_net -boundary_type upper [get_bd_intf_pins axi_interconnect_0/S00_AXI] [get_bd_intf_pins processing_system7_0/M_AXI_GP0]
set_property location {2 328 357} [get_bd_cells proc_sys_reset_0]

startgroup
apply_bd_automation -rule xilinx.com:bd_rule:clkrst -config {Clk "/processing_system7_0/FCLK_CLK0 (50 MHz)" }  [get_bd_pins TC/s_axi_aclk]
apply_bd_automation -rule xilinx.com:bd_rule:clkrst -config {Clk "/processing_system7_0/FCLK_CLK0 (50 MHz)" }  [get_bd_pins load/s_axi_aclk]
apply_bd_automation -rule xilinx.com:bd_rule:clkrst -config {Clk "/processing_system7_0/FCLK_CLK0 (50 MHz)" }  [get_bd_pins up/s_axi_aclk]
apply_bd_automation -rule xilinx.com:bd_rule:clkrst -config {Clk "/processing_system7_0/FCLK_CLK0 (50 MHz)" }  [get_bd_pins ceo/s_axi_aclk]
apply_bd_automation -rule xilinx.com:bd_rule:clkrst -config {Clk "/processing_system7_0/FCLK_CLK0 (50 MHz)" }  [get_bd_pins ce/s_axi_aclk]
apply_bd_automation -rule xilinx.com:bd_rule:clkrst -config {Clk "/processing_system7_0/FCLK_CLK0 (50 MHz)" }  [get_bd_pins loadDat/s_axi_aclk]
apply_bd_automation -rule xilinx.com:bd_rule:clkrst -config {Clk "/processing_system7_0/FCLK_CLK0 (50 MHz)" }  [get_bd_pins rst/s_axi_aclk]
apply_bd_automation -rule xilinx.com:bd_rule:clkrst -config {Clk "/processing_system7_0/FCLK_CLK0 (50 MHz)" }  [get_bd_pins clk/s_axi_aclk]
apply_bd_automation -rule xilinx.com:bd_rule:clkrst -config {Clk "/processing_system7_0/FCLK_CLK0 (50 MHz)" }  [get_bd_pins count/s_axi_aclk]
apply_bd_automation -rule xilinx.com:bd_rule:clkrst -config {Clk "/processing_system7_0/FCLK_CLK0 (50 MHz)" }  [get_bd_pins axi_interconnect_0/ACLK]
apply_bd_automation -rule xilinx.com:bd_rule:clkrst -config {Clk "/processing_system7_0/FCLK_CLK0 (50 MHz)" }  [get_bd_pins axi_interconnect_0/S00_ACLK]
endgroup
apply_bd_automation -rule xilinx.com:bd_rule:processing_system7 -config {make_external "FIXED_IO, DDR" Master "Disable" Slave "Disable" }  [get_bd_cells processing_system7_0]
save_bd_design