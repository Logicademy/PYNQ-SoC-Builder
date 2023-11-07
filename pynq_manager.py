import subprocess
import time
import runpy
import tcl_generator
import ftp_manager
import xml.dom.minidom

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
        






    def generate_tcl(self):
        tcl_generator.generate_tcl(self.hdlgen_project_path)
        print("Generated Tcl script")

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



## Read the docs : https://pysftp.readthedocs.io/en/release_0.2.9/cookbook.html#pysftp-connection-get