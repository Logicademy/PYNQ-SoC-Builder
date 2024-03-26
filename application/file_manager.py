import pysftp
import xml.dom.minidom
import shutil
import os

other_host_name = "192.168.0.53"
host_name = "pynq"
user_name = "xilinx"
pass_word = "xilinx"

# NOTE: This two cnopts lines are probably big security problems if used in production
#       according to pysftp documentation.
cnopts = pysftp.CnOpts()
cnopts.hostkeys = None

# with pysftp.Connection(host=host_name, username=user_name, password=pass_word, cnopts=cnopts) as sftp:
#     print("Connection Estabilished Successfully\n")
#     sftp.put("C:\\masters\\masters_automation\\tmp.txt", "jupyter_notebooks/live_directory/text.tmp")

class File_Manager:
    # Using the IP address directly or simply "pynq" both work.
    def __init__(self, path_to_hdlgen_project):
        path_to_hdlgen_project = path_to_hdlgen_project
        hdlgen = xml.dom.minidom.parse(path_to_hdlgen_project)
        root = hdlgen.documentElement
        # Project Manager - Settings
        projectManager = root.getElementsByTagName("projectManager")[0]
        projectManagerSettings = projectManager.getElementsByTagName("settings")[0]
        self.name = projectManagerSettings.getElementsByTagName("name")[0].firstChild.data
        self.environment = projectManagerSettings.getElementsByTagName("environment")[0].firstChild.data
        self.location = projectManagerSettings.getElementsByTagName("location")[0].firstChild.data

        # genFolder - VHDL Folders
        genFolder = root.getElementsByTagName("genFolder")[0]
        try:
            self.model_folder_path = genFolder.getElementsByTagName("vhdl_folder")[0].firstChild.data
            self.testbench_folder_path = genFolder.getElementsByTagName("vhdl_folder")[1].firstChild.data
        except Exception:
            self.model_folder_path = genFolder.getElementsByTagName("verilog_folder")[0].firstChild.data
            self.testbench_folder_path = genFolder.getElementsByTagName("verilog_folder")[1].firstChild.data
        # self.ChatGPT_folder = genFolder.getElementsByTagName("vhdl_folder")[2]             # Commented as not needed
        # self.ChatGPT_Backups_folder = genFolder.getElementsByTagName("vhdl_folder")[3]     # Commented as not needed
        try:
            self.AMDproj_folder = genFolder.getElementsByTagName("vhdl_folder")[4]
        except Exception:
            self.AMDproj_folder = genFolder.getElementsByTagName("verilog_folder")[4]
        self.AMDproj_folder_path = self.AMDproj_folder.firstChild.data

        self.pynq_build_path = os.path.join(self.location, "PYNQBuild")
        self.pynq_build_output_path = os.path.join(self.pynq_build_path, "output")



    def copy_bitstream_to_dir(self, dest_path):
        
        # We need better handling of output files and be able to raise errors to the front-end
        # C:\repo\HDLGen-ChatGPT\User_Projects\Backup_led_Working_io_mapping\CB4CLED\VHDL\AMDprj_2023\CB4CLED.gen\sources_1\bd\CB4CLED_bd\hw_handoff
        
        # In brand new Vivado projects, the hwh file is in the .gen folder not the .srcs
        if dest_path==None:
            self.check_path_and_mkdir()
            dest_path = self.pynq_build_output_path


        # HOTFIX: To fix location bug, we are going to pop the last directory from the location variable instead.
        base = os.path.dirname(self.location)

        tcl_location = base + "/" + self.AMDproj_folder_path # path hotfix
        hwh_location = tcl_location + "/" + self.name + ".srcs/sources_1/bd/" + self.name + "_bd/hw_handoff"
        hwh_location_2023 = tcl_location + "/" + self.name + ".gen/sources_1/bd/" + self.name + "_bd/hw_handoff"
        bit_location = tcl_location + "/" + self.name + ".runs/impl_1"

        bit_filename = self.name + "_bd_wrapper.bit"
        hwh_filename = self.name + "_bd.hwh"
        tcl_filename = self.name + "_bd.tcl"
        
        tcl_full_path = tcl_location + "/" + tcl_filename
        hwh_full_path = hwh_location + "/" + hwh_filename
        hwh_full_path_2023 = hwh_location_2023 + "/" + hwh_filename
        bit_full_path = bit_location + "/" + bit_filename

        # Perm temp fix lol
        tcl_full_path = tcl_full_path.replace("\\", "/")
        hwh_full_path = hwh_full_path.replace("\\", "/")
        bit_full_path = bit_full_path.replace("\\", "/")

        if os.path.exists(tcl_full_path):
            shutil.copy(tcl_full_path, dest_path+"/"+self.name+".tcl")

        if os.path.exists(hwh_full_path):
            shutil.copy(hwh_full_path, dest_path+"/"+self.name+".hwh")

        if os.path.exists(hwh_full_path_2023):
            shutil.copy(hwh_full_path_2023, dest_path+"/"+self.name+".hwh")

        if os.path.exists(bit_full_path):
            shutil.copy(bit_full_path, dest_path+"/"+self.name+".bit")
            print(bit_full_path)
            print(dest_path+"/"+self.name+".bit")
            print("Bit copy passed")
            return True
        else:
            print("Binary Copy Failed")
            return False
        
    def check_path_and_mkdir(self):
        try:
            os.makedirs(self.pynq_build_output_path)
        except FileExistsError:
            print("PYNQBuild/output exists already.")

    def copy_to_dir(source_full_path, destination_full_path):
        shutil.copy(source_full_path, destination_full_path)

    # No need to set the port as 22 as this is default.
    # with pysftp.Connection(host=other_host_name, username=user_name, password=pass_word, cnopts=cnopts) as sftp:
    #     print("Connection Estabilished Successfully\n")
    #     print(sftp.pwd)

    def check_bitstream_exists(self):
        tcl_location = os.path.dirname(self.location) + "/" + self.AMDproj_folder_path # path hotfix
        # hwh_location = tcl_location + "/" + self.name + ".srcs/sources_1/bd/" + self.name + "_bd/hw_handoff"
        bit_location = tcl_location + "/" + self.name + ".runs/impl_1"

        # hwh_filename = self.name + "_bd.hwh"
        # tcl_filename = self.name + ".tcl"
        bit_filename = self.name + "_bd_wrapper.bit"


        # tcl_full_path = tcl_location + "/" + tcl_filename
        # hwh_full_path = hwh_location + "/" + hwh_filename
        bit_full_path = bit_location + "/" + bit_filename

        # tcl_full_path = tcl_full_path.replace("\\", "/")
        # hwh_full_path = hwh_full_path.replace("\\", "/")
        bit_full_path = bit_full_path.replace("\\", "/")

        return os.path.exists(bit_full_path)

    def pwd(self):
        with pysftp.Connection(host=host_name, username=user_name, password=pass_word, cnopts=cnopts) as sftp:
            print("Connection Estabilished Successfully\n")
            result = sftp.pwd
            print(result)
            return result
        
    def upload_file(self, local_path, remote_path):
        with pysftp.Connection(host=host_name, username=user_name, password=pass_word, cnopts=cnopts) as sftp:
            print("Connection Estabilished Successfully\n")
            sftp.put(local_path, remote_path)

        
    def download_file(self, remote_path, local_path):
        with pysftp.Connection(host=host_name, username=user_name, password=pass_word, cnopts=cnopts) as sftp:
            print("Connection Estabilished Successfully\n")
            sftp.get(remote_path, local_path)

        
    def upload_bitstream(self, remote_path="jupyter_notebooks/live_directory"):
        tcl_location = self.location + "/" + self.AMDproj_folder_path
        hwh_location = tcl_location + "/" + self.name + ".srcs/sources_1/bd/" + self.name + "_bd/hw_handoff"
        bit_location = tcl_location + "/" + self.name + ".runs/impl_1"

        bit_filename = self.name + "_bd_wrapper.bit"
        hwh_filename = self.name + "_bd.hwh"
        tcl_filename = self.name + ".tcl"
        
        tcl_full_path = tcl_location + "/" + tcl_filename
        hwh_full_path = hwh_location + "/" + hwh_filename
        bit_full_path = bit_location + "/" + bit_filename

        self.upload_file(tcl_full_path, remote_path+"/"+self.name+".tcl") # local_path, remote_path
        self.upload_file(hwh_full_path, remote_path+"/"+self.name+".hwh") # local_path, remote_path
        self.upload_file(bit_full_path, remote_path+"/"+self.name+".bit") # local_path, remote_path

        # with sftp.cd('/allcode'):           # temporarily chdir to allcode
        #     sftp.put('/pycode/filename')  	# upload file to allcode/pycode on remote
        #     sftp.get('remote_file')         # get a remote file


        # hdlgen = xml.dom.minidom.parse(path_to_hdlgen_project)
        # root = hdlgen.documentElement

        # # Project Manager - Settings
        # projectManager = root.getElementsByTagName("projectManager")[0]
        # projectManagerSettings = projectManager.getElementsByTagName("settings")[0]
        # name = projectManagerSettings.getElementsByTagName("name")[0].firstChild.data
        # environment = projectManagerSettings.getElementsByTagName("environment")[0].firstChild.data
        # location = projectManagerSettings.getElementsByTagName("location")[0].firstChild.data

        # # genFolder - VHDL Folders
        # genFolder = root.getElementsByTagName("genFolder")[0]
        # model_folder = genFolder.getElementsByTagName("vhdl_folder")[0]
        # testbench_folder = genFolder.getElementsByTagName("vhdl_folder")[1]
        # # ChatGPT_folder = genFolder.getElementsByTagName("vhdl_folder")[2]             # Commented as not needed
        # # ChatGPT_Backups_folder = genFolder.getElementsByTagName("vhdl_folder")[3]     # Commented as not needed
        # AMDproj_folder = genFolder.getElementsByTagName("vhdl_folder")[4]
        # AMDproj_folder_rel_path = AMDproj_folder.firstChild.data

        # # hdlDesign - entityIOPorts
        # hdlDesign = root.getElementsByTagName("hdlDesign")[0]
        # entityIOPorts = hdlDesign.getElementsByTagName("entityIOPorts")[0]
        # signals = entityIOPorts.getElementsByTagName("signal")

        # all_ports = []
        # for sig in signals:
        #     signame = sig.getElementsByTagName("name")[0]
        #     mode = sig.getElementsByTagName("mode")[0]
        #     type = sig.getElementsByTagName("type")[0]
        #     desc = sig.getElementsByTagName("description")[0]
        #     all_ports.append(
        #         [signame.firstChild.data, mode.firstChild.data, type.firstChild.data, desc.firstChild.data]
        #     )