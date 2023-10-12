import subprocess
import time
import runpy

# Define location of vivado exe, this might need to be the bat file we will see.
# D:\Xilinx\Vivado\2019.1\bin\vivado.bat -mode tcl
# vivado_cmd = "D:\\Xilinx\\Vivado\\2019.1\\bin\\vivado.bat"

class Tcl_Manager:
    def __init__(self, vivado_bat_path):
        self.vivado_bat_path = vivado_bat_path

    def generate_tcl(self):
        runpy.run_path(path_name='tcl_generator.py')

    def run_vivado(self):
        # D:\Xilinx\Vivado\2019.1\bin\vivado.bat -mode tcl -source C:/masters/masters_automation/generate_script.tcl
        try:
            print("Starting Process")
            vivado_process = subprocess.run([self.vivado_bat_path, "-mode", "tcl", "-source", "generate_script.tcl"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
        except Exception as e:
            print("Exception")
            print(e)

    def upload_files(self):
        # __init__ will also need to contain the path of the project.
        # upload files function could be allowed to automatically find the files given the relative filepath should remain the same.



## Read the docs : https://pysftp.readthedocs.io/en/release_0.2.9/cookbook.html#pysftp-connection-get

## Sample code.

# try:
#     print("Starting Process")
#     vivado_process = subprocess.Popen([vivado_cmd, "-mode", "tcl"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
#     print("Generating and Sending Puts command")
#     # Example: Send a Tcl command to Vivado
#     tcl_command = "puts \"Hello from Python\"\n"
#     vivado_process.stdin.write(tcl_command)
#     vivado_process.stdin.flush()
    
#     print("Starting Sleep")
#     time.sleep(5)
#     print("End of Sleep")

#     # vivado_response = vivado_process.stdout.readline()
#     #for line in vivado_response:

#     # Example: Receive and print the response from Vivado
#     # vivado_response = vivado_process.stdout.readline()
#     # print(vivado_response)

    
#     vivado_process.stdin.write("exit\n")
#     vivado_process.stdin.flush()
#     vivado_process.wait()
    
#     print("Tcl commands executed successfully")
# except subprocess.CalledProcessError as e:
#     print(f"Error running Vivado: {e}")

# class tcl_manager:
#     def __init__(self, vivado_bat_path):
#         self.vivado_bat_path = vivado_bat_path
#         # self.vivado_process = ""
#         try:
#             print("Attempting to launch vivado...")
#             self.vivado_process = subprocess.Popen([self.vivado_bat_path, "-mode", "tcl"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
#             print("Are we getting hung up here?")
#         except subprocess.CalledProcessError as e:
#             print(f"Error running Vivado: {e}")


#     def open_project(self, vivado_xpr_path):
#         self.vivado_xpr_path = vivado_xpr_path
#         print("Opening Project")

#     def read_terminal(self):
#         print("Read Terminal")
#         time.sleep(10)
#         self.vivado_response = self.vivado_process.stdout.readline()
#         print(self.vivado_response)
        

#     def print_vivado_path(self):
#         print(self.vivado_bat_path)
