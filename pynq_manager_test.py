import pynq_manager as pm

pm = pm.Pynq_Manager("D:/Xilinx/Vivado/2019.1/bin/vivado.bat", "C:\\masters\\masters_automation\\LukeAND_working\\LukeAND\\HDLGenPrj\\LukeAND.hdlgen")
pm.generate_tcl()
pm.run_vivado()