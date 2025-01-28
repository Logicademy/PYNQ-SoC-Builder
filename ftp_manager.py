import pysftp
import xml.dom.minidom
import shutil

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

class Ftp_Manager:
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
        self.model_folder_path = genFolder.getElementsByTagName("vhdl_folder")[0].firstChild.data
        self.testbench_folder_path = genFolder.getElementsByTagName("vhdl_folder")[1].firstChild.data
        # self.ChatGPT_folder = genFolder.getElementsByTagName("vhdl_folder")[2]             # Commented as not needed
        # self.ChatGPT_Backups_folder = genFolder.getElementsByTagName("vhdl_folder")[3]     # Commented as not needed
        self.AMDproj_folder_path = genFolder.getElementsByTagName("vhdl_folder")[4].firstChild.data

    def copy_bitstream_to_dir(self, dest_path):
        
        tcl_location = self.location + "/" + self.AMDproj_folder_path
        hwh_location = tcl_location + "/" + self.name + ".srcs/sources_1/bd/" + self.name + "_bd/hw_handoff"
        bit_location = tcl_location + "/" + self.name + ".runs/impl_1"

        bit_filename = self.name + "_bd_wrapper.bit"
        hwh_filename = self.name + "_bd.hwh"
        tcl_filename = self.name + ".tcl"
        
        tcl_full_path = tcl_location + "/" + tcl_filename
        hwh_full_path = hwh_location + "/" + hwh_filename
        bit_full_path = bit_location + "/" + bit_filename

        # TODO: Correct for \\ instead of / earlier in the program. This is a quick patch.
        tcl_full_path = tcl_full_path.replace("\\", "/")
        hwh_full_path = hwh_full_path.replace("\\", "/")
        bit_full_path = bit_full_path.replace("\\", "/")


        shutil.copy(tcl_full_path, dest_path+"/"+self.name+".tcl")
        shutil.copy(hwh_full_path, dest_path+"/"+self.name+".hwh")
        shutil.copy(bit_full_path, dest_path+"/"+self.name+".bit")
        
    def copy_to_dir(source_full_path, destination_full_path):
        shutil.copy(source_full_path, destination_full_path)

    # No need to set the port as 22 as this is default.
    # with pysftp.Connection(host=other_host_name, username=user_name, password=pass_word, cnopts=cnopts) as sftp:
    #     print("Connection Estabilished Successfully\n")
    #     print(sftp.pwd)

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