import subprocess
import time
import runpy
import application.tcl_generator as tcl_gen
import application.file_manager as file_manager
import application.notebook_generator as nbg
import xml.dom.minidom
import os
# Define location of vivado exe, this might need to be the bat file we will see.
# D:\Xilinx\Vivado\2019.1\bin\vivado.bat -mode tcl
# vivado_cmd = "D:\\Xilinx\\Vivado\\2019.1\\bin\\vivado.bat"

class Pynq_Manager:

    def __init__(self, hdlgen_project_path, vivado_bat_path=None):
        self.hdlgen_project_path = hdlgen_project_path      # Path to .hdlgen file
        if vivado_bat_path == None:
            # If the Vivado bat path isn't defined, extract it from the HDLGen XML
            hdlgen = xml.dom.minidom.parse(hdlgen_project_path)
            root = hdlgen.documentElement
            projectManager = root.getElementsByTagName("projectManager")[0]
            projectManagerEda = projectManager.getElementsByTagName("EDA")[0]
            projectManagerEdaTool = projectManagerEda.getElementsByTagName("tool")[0]
            projectManagerEdaToolDir = projectManagerEdaTool.getElementsByTagName("dir")[0]
            self.vivado_bat_path = projectManagerEdaToolDir.firstChild.data
        else:
            self.vivado_bat_path = vivado_bat_path              # Path to vivado .bat file

    def get_board_config_exists(self):
        # vivado_bat_path = C:\Xilinx\Vivado\2019.1\bin\vivado.bat
        vivado_dir = os.path.dirname(os.path.dirname(self.vivado_bat_path)) # Using this command twice removes /bin/vivado.bat
        # Add /data/boards/board_files/pynq-z2/
        board_path = vivado_dir + "/data/boards/board_files/pynq-z2/"
        # print(board_path)
        # Check if the path exists and return boolean
        board_files_exists = os.path.exists(board_path)
        return board_files_exists

    def get_bd_exists(self):
        ## This function is highly inefficient and could be condensed easily, for sake of
        ## speed the function was ripped from tcl_generator.py as quick as possible so that
        ## this API is available to main_cli.py to ask user if they'd like to upgrade or not
        hdlgen = xml.dom.minidom.parse(self.hdlgen_project_path)
        root = hdlgen.documentElement

        # Project Manager - Settings
        projectManager = root.getElementsByTagName("projectManager")[0]
        projectManagerSettings = projectManager.getElementsByTagName("settings")[0]
        name = projectManagerSettings.getElementsByTagName("name")[0].firstChild.data
        environment = projectManagerSettings.getElementsByTagName("environment")[0].firstChild.data
        location = projectManagerSettings.getElementsByTagName("location")[0].firstChild.data

        # genFolder - VHDL Folders
        genFolder = root.getElementsByTagName("genFolder")[0]
        # model_folder = genFolder.getElementsByTagName("vhdl_folder")[0]
        # testbench_folder = genFolder.getElementsByTagName("vhdl_folder")[1]
        # ChatGPT_folder = genFolder.getElementsByTagName("vhdl_folder")[2]             # Commented as not needed
        # ChatGPT_Backups_folder = genFolder.getElementsByTagName("vhdl_folder")[3]     # Commented as not needed
        try:
            AMDproj_folder = genFolder.getElementsByTagName("vhdl_folder")[4]
        except Exception:
            AMDproj_folder = genFolder.getElementsByTagName("verilog_folder")[4]
        AMDproj_folder_rel_path = AMDproj_folder.firstChild.data


        bd_filename = name + "_bd"
        path_to_bd = environment + "/" + AMDproj_folder_rel_path + "/" + name + ".srcs/sources_1/bd"    # hotfix environment var instead of location
        path_to_bd_folder_check = path_to_bd + "/" +  bd_filename
        path_to_bd_file_check = path_to_bd_folder_check + "/" + bd_filename + ".bd"
        path_to_wrapper_file_check = path_to_bd_folder_check + "/hdl/" + bd_filename + "_wrapper.vhd"
        bd_exists = os.path.exists(path_to_bd_file_check)
        wrapper_exists = os.path.exists(path_to_wrapper_file_check)

        return bd_exists

    def generate_tcl(self, regenerate_bd=True, start_gui=True, keep_vivado_open=False, skip_board_config=False, io_map=None):
        tcl_gen.generate_tcl(self.hdlgen_project_path, regenerate_bd=regenerate_bd, start_gui=start_gui, keep_vivado_open=keep_vivado_open, skip_board_config=skip_board_config, io_map=io_map)

    def run_vivado(self):
        # D:\Xilinx\Vivado\2019.1\bin\vivado.bat -mode tcl -source C:/masters/masters_automation/generate_script.tcl
        try:
            print("Starting Vivado")
            vivado_process = subprocess.run([self.vivado_bat_path, "-mode", "tcl", "-source", "./generated/generate_script.tcl"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print("Bit stream generation is complete")
        except Exception as e:
            print("Exception")
            print(e)

    def upload_to_pynq(self):
        pass

    def copy_to_dir(self, destination=None):
        ftp = file_manager.Ftp_Manager(self.hdlgen_project_path)
        res = ftp.copy_bitstream_to_dir(destination)
        print(f"Copied Bitsteam Output to: /PYNQBuild/output")
        return res

    def test_connection(self):
        file_manager.pwd()

    def generate_jnb(self, generic=False):
        nbg.create_jnb(self.hdlgen_project_path, generic=generic)


## Read the docs : https://pysftp.readthedocs.io/en/release_0.2.9/cookbook.html#pysftp-connection-get