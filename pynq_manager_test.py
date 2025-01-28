import pynq_manager as pm
import os

# Pynq_Manager( Path to Vivado Bat File, Path to HDLGen file )

pm = pm.Pynq_Manager(
    "D:\\HDLGen-ChatGPT\\User_Projects\\LukeAND_used_good\\LukeAND\\HDLGenPrj\\LukeAND.hdlgen",
    "D:/Xilinx/Vivado/2019.1/bin/vivado.bat"
)

# pm.generate_tcl()             # Produce generate_script.tcl
# pm.run_vivado()               # Execute generate_script.tcl in Vivado
# pm.test_connection()          # Print "pwd" from remote in console
# pm.copy_to_dir(os.getcwd())   # Copy bitstream files to the current working directory

# TODO: pm.upload_bitstream(optional: dest)
# TODO: pm.upload_file(local_addr, remote_addr)