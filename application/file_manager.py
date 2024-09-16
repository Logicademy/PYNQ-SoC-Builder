# import pysftp
import xml.dom.minidom
import shutil
import os
import application.hdlgen_project as hdlgenproject
# import webbrowser

# host_name = "192.168.2.99"
# host_name = "pynq"
# user_name = "xilinx"
# pass_word = "xilinx"

# NOTE: This two cnopts lines are probably big security problems if used in production
#       according to pysftp documentation.
# cnopts = pysftp.CnOpts()
# cnopts.hostkeys = None

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
        pass
#        with pysftp.Connection(host=host_name, username=user_name, password=pass_word, cnopts=cnopts) as sftp:
#            print("Connection Estabilished Successfully\n")
#            result = sftp.pwd
#            print(result)
#            return result
        
    def upload_file(self, local_path, remote_path):
        pass
#        with pysftp.Connection(host=host_name, username=user_name, password=pass_word, cnopts=cnopts) as sftp:
#            print("Connection Estabilished Successfully\n")
#            sftp.put(local_path, remote_path)
#
        
    def download_file(self, remote_path, local_path):
        pass
#        with pysftp.Connection(host=host_name, username=user_name, password=pass_word, cnopts=cnopts) as sftp:
#            print("Connection Estabilished Successfully\n")
#            sftp.get(remote_path, local_path)

        
    def upload_bitstream(self, remote_path="jupyter_notebooks/live_directory"):
        pass

        # # HOTFIX: To fix location bug, we are going to pop the last directory from the location variable instead.
        # base = os.path.dirname(self.location)

        # tcl_location = base + "/" + self.AMDproj_folder_path # path hotfix
        # hwh_location = tcl_location + "/" + self.name + ".srcs/sources_1/bd/" + self.name + "_bd/hw_handoff"
        # hwh_location_2023 = tcl_location + "/" + self.name + ".gen/sources_1/bd/" + self.name + "_bd/hw_handoff"
        # bit_location = tcl_location + "/" + self.name + ".runs/impl_1"

        # bit_filename = self.name + "_bd_wrapper.bit"
        # hwh_filename = self.name + "_bd.hwh"
        # tcl_filename = self.name + "_bd.tcl"
        
        # tcl_full_path = tcl_location + "/" + tcl_filename
        # hwh_full_path = hwh_location + "/" + hwh_filename
        # hwh_full_path_2023 = hwh_location_2023 + "/" + hwh_filename
        # bit_full_path = bit_location + "/" + bit_filename

        # # Perm temp fix lol
        # tcl_full_path = tcl_full_path.replace("\\", "/")
        # hwh_full_path = hwh_full_path.replace("\\", "/")
        # bit_full_path = bit_full_path.replace("\\", "/")

        # if os.path.exists(tcl_full_path):
        #     self.upload_file(tcl_full_path, remote_path+"/"+self.name+".tcl") # local_path, remote_path

        # if os.path.exists(hwh_full_path):
        #     self.upload_file(hwh_full_path, remote_path+"/"+self.name+".hwh") # local_path, remote_path

        # if os.path.exists(hwh_full_path_2023):
        #     self.upload_file(hwh_full_path_2023, remote_path+"/"+self.name+".hwh") # local_path, remote_path


        # if os.path.exists(bit_full_path):
        #     self.upload_file(bit_full_path, remote_path+"/"+self.name+".bit") # local_path, remote_path
        #     print(bit_full_path)
        #     print("Bit Upload passed")
        #     return True
        # else:
        #     print("Binary Upload Failed")
        #     return False







    # Script ran directly - run this test code:
    # file_manager = File_Manager("C:/repo1/March27/DSPProc/DSPProc/HDLGenPrj/DSPProc.hdlgen")


    # # with pysftp.Connection(host=host_name, username=user_name, password=pass_word, port=22) as sftp:
    # with pysftp.Connection(host=host_name, username=user_name, password=pass_word, cnopts=cnopts) as sftp:

    #     print("Connection established")

    #     # Change to the remote directory
    #     sftp.chdir("jupyter_notebooks/")

    #     print(sftp.getcwd())

    #     # Create a new folder
    #     try:
    #         sftp.mkdir("live_directory")
    #         print(f"Folder 'live_directory' created")
    #     except OSError as oserror:
    #         print(oserror)
    #         print("fodler prolly existing")
    #     except Exception as e:
    #         print(e)

    #     # # Change permissions of the newly created folder (e.g., setting permissions to 755)
    #     # permissions = 0o777
    #     sftp.chmod("live_directory", '755')
    #     print(f"Permissions of 'live_directory' changed to 0o755")


    # file_manager.upload_bitstream()
    
    
def upload_output_folder_to_direct_connect_pynq(hdlgen_prj):
    pass
    # host_name = "192.168.2.99"  # Default Consignment Always
    # user_name = "xilinx"        # Default Username
    # pass_word = "xilinx"        # Default Password

    # # NOTE: This two cnopts lines are probably big security problems if used in production
    # #       according to pysftp documentation.
    # cnopts = pysftp.CnOpts()
    # cnopts.hostkeys = None
    # try:
    #     with pysftp.Connection(host=host_name, username=user_name, password=pass_word, cnopts=cnopts) as pynq_ftp:
    #         print("Connected to FPGA!")
    #         hdlgen_prj.add_to_build_log("\nConnected to FPGA!")
            
    #         print("Moved to Jupyter Notebook folder")
    #         hdlgen_prj.add_to_build_log("\nMoved to Jupyter Notebook folder")
    #         pynq_ftp.chdir("jupyter_notebooks/")

    #         if pynq_ftp.exists('SoC-Builder-Uploads'):
    #             hdlgen_prj.add_to_build_log("\nSoC-Builder-Uploads folder exists")
    #             print("SoC-Builder-Uploads folder exists")

    #             permissions = pynq_ftp.stat('SoC-Builder-Uploads').st_mode & 0o777

    #             if permissions == 0o755:
    #                 print("SoC-Builder-Uploads permissions are configured correctly.")
    #                 hdlgen_prj.add_to_build_log("\nSoC-Builder-Uploads permissions are configured correctly.")
    #             else:
    #                 print("SoC-Builder-Uploads permissions are NOT configured correctly - Please delete folder and allow SoC Builder to create it automatically.")
    #                 hdlgen_prj.add_to_build_log("\nSoC-Builder-Uploads permissions are NOT configured correctly - Please delete folder and allow SoC Builder to create it automatically.")
    #                 return # Leave function

    #         else:
    #             # Create the folder

    #             print("Attempting to create SoC-Builder-Uploads folder")
    #             hdlgen_prj.add_to_build_log("\nAttempting to create SoC-Builder-Uploads folder")

    #             pynq_ftp.mkdir("SoC-Builder-Uploads")
    #             pynq_ftp.chmod("SoC-Builder-Uploads", '755')
    #             print(f"Permissions of 'SoC-Builder-Uploads' changed to 0o755")
    #             hdlgen_prj.add_to_build_log(f"\nPermissions of 'SoC-Builder-Uploads' changed to 0o755")
    
    #         hdlgen_prj.add_to_build_log(f"\nMoving to SoC-Builder-Uploads folder")
    #         print(f"Moving to SoC-Builder-Uploads folder")         
    #         pynq_ftp.chdir("SoC-Builder-Uploads/")

            # hdlgen_prj.add_to_build_log("\nCreating Project Folder")
            # print("Creating Project Folder")         
            # # pynq_ftp.chdir("SoC-Builder-Uploads/")
            # extension_integer = 0
            # prj_name = hdlgen_prj.name.replace(" ", "")
            # folder_name = prj_name
            # while pynq_ftp.exists(folder_name):
            #     # Folder exists, try the next folder name
            #     folder_name = f"{prj_name}_{extension_integer}"
            #     extension_integer += 1

            # # Once we leave this loop we finally have a good name for our folder.
            # hdlgen_prj.add_to_build_log(f"\nCreating {folder_name} directory, setting permissions and moving into it.")
            # print(f"\nCreating {folder_name} directory, setting permissions and moving into it.")   
            # pynq_ftp.mkdir(folder_name)
            # pynq_ftp.chmod(folder_name, '755')
            # pynq_ftp.chdir(folder_name)


            # # Folder is now created and ready.
            # # We need to find the PYNQBuild/output folder locally, then transfer all of it to the board.
            # build_output_path = hdlgen_prj.pynq_build_output_path
            # hdlgen_prj.add_to_build_log(f"\nLoading {build_output_path} folder contents")
            # print(f"Loading {build_output_path} folder contents")

            # for filename in os.listdir(build_output_path):
            #     local_file = os.path.join(build_output_path, filename)
            #     hdlgen_prj.add_to_build_log(f"\nFound {filename}")
            #     print(f"Found {filename}")
            
            #     if os.path.isfile(local_file):
            #         hdlgen_prj.add_to_build_log(f"\nUploading {filename}")
            #         print(f"Uploading {filename}")
            #         pynq_ftp.put(local_file)
            #     else:
            #         hdlgen_prj.add_to_build_log(f"\n{filename} isn't a file - skipping")
            #         print(f"{filename} isn't a file - skipping")

            # url = f"http://{host_name}:9090/tree/SoC-Builder-Uploads/{folder_name}"
            # webbrowser.open(url)


    # except Exception as e:
    #     print(f"Could not upload to PYNQ - {e}")

