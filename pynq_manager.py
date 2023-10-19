import subprocess
import time
import runpy

# Define location of vivado exe, this might need to be the bat file we will see.
# D:\Xilinx\Vivado\2019.1\bin\vivado.bat -mode tcl
# vivado_cmd = "D:\\Xilinx\\Vivado\\2019.1\\bin\\vivado.bat"

class Pynq_Manager:

    # Sample Configuration Declaration
    compName = "AND2_1"
    title = "AND2_1 2-input AND"
    description = "AND2_1 2-input AND &amp;#10;AndOut asserted when ANDIn1 and ANDIn0 are both asserted&amp;#44; otherwise deasserted"
    authors = "Fearghal Morgan"
    company = "University of Galway"
    email = "fearghal.mogran1@gmail.com"
    date = "12/09/2023"

    input_ports = [
        ["AND2In1", "in", "single bit", "datapath signal 1"],
        ["AND2In0", "in", "single bit", "datapath single 0"]
    ]   

    output_ports = [
        ["AndOut", "out", "single bit", "Output datapath signal"]
    ]

    testbench_cols = []
    for i in input_ports:
        testbench_cols.append(i[0])

    for o in output_ports:
        testbench_cols.append(o[0])

    test_cases = [
        [0,0,0],
        [0,1,0],
        [1,0,0],
        [1,1,1]
    ]




    def __init__(self, vivado_bat_path, hdlgen_project_path):
        self.vivado_bat_path = vivado_bat_path              # Path to vivado .bat file
        self.hdlgen_project_path = hdlgen_project_path      # Path to .hdlgen file

    def generate_tcl(self):
        # runpy.run_path(path_name='tcl_generator.py') # using runpy really isn't an ideal implementation.
        
        pass

    def run_vivado(self):
        # D:\Xilinx\Vivado\2019.1\bin\vivado.bat -mode tcl -source C:/masters/masters_automation/generate_script.tcl
        try:
            print("Starting Process")
            vivado_process = subprocess.run([self.vivado_bat_path, "-mode", "tcl", "-source", "generate_script.tcl"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
        except Exception as e:
            print("Exception")
            print(e)

    def upload_to_pynq(self):
        pass
        # __init__ will also need to contain the path of the project.
        # upload files function could be allowed to automatically find the files given the relative filepath should remain the same.

    def copy_to_dir(self):
        pass
        # this function is responsible for moving the output in the event that direct upload isn't available.



## Read the docs : https://pysftp.readthedocs.io/en/release_0.2.9/cookbook.html#pysftp-connection-get