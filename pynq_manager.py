import subprocess
import time
import runpy
import tcl_generator
import ftp_manager
import notebook_generator as nbg
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
        model_folder = genFolder.getElementsByTagName("vhdl_folder")[0]
        testbench_folder = genFolder.getElementsByTagName("vhdl_folder")[1]
        # ChatGPT_folder = genFolder.getElementsByTagName("vhdl_folder")[2]             # Commented as not needed
        # ChatGPT_Backups_folder = genFolder.getElementsByTagName("vhdl_folder")[3]     # Commented as not needed
        AMDproj_folder = genFolder.getElementsByTagName("vhdl_folder")[4]
        AMDproj_folder_rel_path = AMDproj_folder.firstChild.data

        bd_filename = name + "_bd"
        path_to_bd = location + "/" + AMDproj_folder_rel_path + "/" + name + ".srcs/sources_1/bd"
        path_to_bd_folder_check = path_to_bd + "/" +  bd_filename
        path_to_bd_file_check = path_to_bd_folder_check + "/" + bd_filename + ".bd"
        path_to_wrapper_file_check = path_to_bd_folder_check + "/hdl/" + bd_filename + "_wrapper.vhd"
        bd_exists = os.path.exists(path_to_bd_file_check)
        wrapper_exists = os.path.exists(path_to_wrapper_file_check)

        return bd_exists

    def generate_tcl(self, regenerate_bd=False):
        tcl_generator.generate_tcl(self.hdlgen_project_path, regenerate_bd=regenerate_bd)

    def run_vivado(self):
        # D:\Xilinx\Vivado\2019.1\bin\vivado.bat -mode tcl -source C:/masters/masters_automation/generate_script.tcl
        try:
            print("Starting Vivado")
            vivado_process = subprocess.run([self.vivado_bat_path, "-mode", "tcl", "-source", "generate_script.tcl"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print("Bit stream generation is complete")
        except Exception as e:
            print("Exception")
            print(e)

    def upload_to_pynq(self):
        pass

    def copy_to_dir(self, destination):
        ftp = ftp_manager.Ftp_Manager(self.hdlgen_project_path)
        ftp.copy_bitstream_to_dir(destination)
        print(f"Copied Bitsteam Output to: {destination}")
        # this function is responsible for moving the output in the event that direct upload isn't available.

    def test_connection(self):
        ftp_manager.pwd()

    def generate_jnb(self):
        nbg.create_jnb(self.hdlgen_project_path)


## Read the docs : https://pysftp.readthedocs.io/en/release_0.2.9/cookbook.html#pysftp-connection-get