import subprocess
import time
import runpy
import application.tcl_generator as tcl_gen
import application.file_manager as file_manager
import application.notebook_generator as nbg
import xml.dom.minidom
import os
import shutil 
import application.checks as checks

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

            projectManager = root.getElementsByTagName("projectManager")[0]
            projectManagerSettings = projectManager.getElementsByTagName("settings")[0]
            self.location = projectManagerSettings.getElementsByTagName("location")[0].firstChild.data
            self.pynq_build_path = os.path.join(self.location, "PYNQBuild")
            self.pynq_build_output_path = os.path.join(self.pynq_build_path, "output")
            self.pynq_build_generated_path = os.path.join(self.pynq_build_path, "generated")
        else:
            self.vivado_bat_path = vivado_bat_path              # Path to vivado .bat file
        
        

    def get_board_config_exists(self):
        # vivado_bat_path = C:\Xilinx\Vivado\2019.1\bin\vivado.bat
        # Add /data/boards/board_files/pynq-z2/
        vivado_dir = os.path.dirname(os.path.dirname(self.vivado_bat_path)) # Using this command twice removes /bin/vivado.bat
        # Add /data/boards/board_files/pynq-z2/
        board_path = vivado_dir + "/data/boards/board_files/pynq-z2/"
        # print(board_path)
        # Check if the path exists and return boolean
        board_files_exists = os.path.exists(board_path)

        # print(board_files_exists)
        # Install the board
        # - 1) Check folders exist
        # - 2) Copy folder
        # - 3) Thats all.
        if not board_files_exists:
            try:
                # print(os.path.dirname(board_path))
                os.makedirs(os.path.dirname(os.path.dirname(board_path)))
            except FileExistsError:
                print("Board_files Vivado directory already exists, copying files")
            
            try:
                # This is the way to fix paths which works for Linux or Windows - Not consistently used in this project
                current_path = os.getcwd()
                current_path = os.path.normpath(current_path).replace(os.sep, '/')

                board_files_folder = os.path.join(current_path, "board_files")

                # Copy the entire directory and its contents
                shutil.copytree(board_files_folder, board_path)
                print(f"Directory copied successfully from {board_files_folder} to {board_path}")
            except shutil.Error as e:
                print(f"Error: {e}")
            except OSError as e:
                print(f"Error: {e}")
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

    def generate_tcl(self, regenerate_bd=True, start_gui=True, keep_vivado_open=False, skip_board_config=False, io_map=None, gui_app=None):
        self.check_generated_path_and_mkdir()
        tcl_gen.generate_tcl(self.hdlgen_project_path, regenerate_bd=regenerate_bd, start_gui=start_gui, keep_vivado_open=keep_vivado_open, skip_board_config=skip_board_config, io_map=io_map, gui_application=gui_app)

    def run_vivado(self):
        try:
            checks.check_for_dashes(self.hdlgen_project_path)
        except checks.DashesInHDLFileError:
            print(f"PYNQ Manager Detected Dashes in HDL File {self.hdlgen_project_path}")
            raise checks.DashesInHDLFileError
        except Exception as e:
            print(f"Expection Occured in Run Vivado: {e}")
            print("Pynq_Manager.run_vivado() returning without action.")
            return
        
        # D:\Xilinx\Vivado\2019.1\bin\vivado.bat -mode tcl -source C:/masters/masters_automation/generate_script.tcl
        try:
            self.check_generated_path_and_mkdir()
            print("Starting Vivado")
            # Need to add a check here to see if the destination tcl file exists.
            vivado_process = subprocess.run([self.vivado_bat_path, "-mode", "tcl", "-source", f"{self.pynq_build_generated_path}/generate_script.tcl"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print("Bit stream generation is complete")
        except Exception as e:
            print("Exception")
            print(e)

    def upload_to_pynq(self):
        pass

    def copy_to_dir(self, destination=None):
        ftp = file_manager.File_Manager(self.hdlgen_project_path)
        res = ftp.copy_bitstream_to_dir(destination)
        print(f"Copied Bitsteam Output to: /PYNQBuild/output")
        return res

    def test_connection(self):
        file_manager.pwd()

    def check_path_and_mkdir(self):
        try:
            os.makedirs(self.pynq_build_output_path)
        except FileExistsError:
            print("PYNQBuild/output exists already.")

    def check_generated_path_and_mkdir(self):
        try:
            os.makedirs(self.pynq_build_generated_path)
        except FileExistsError:
            print("PYNQBuild/generated exists already.")

    def generate_jnb(self, generic=False):
        self.check_path_and_mkdir()
        dest_path = self.pynq_build_output_path
        nbg.create_jnb(self.hdlgen_project_path, generic=generic, output_filename=dest_path)


## Read the docs : https://pysftp.readthedocs.io/en/release_0.2.9/cookbook.html#pysftp-connection-get