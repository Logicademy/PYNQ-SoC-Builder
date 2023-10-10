import subprocess
import time
# Define location of vivado exe, this might need to be the bat file we will see.
print("Creating CMD")
vivado_cmd = "D:\\Xilinx\\Vivado\\2019.1\\bin\\vivado.bat"

try:
    print("Starting Process")
    vivado_process = subprocess.Popen([vivado_cmd, "-mode", "tcl"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print("Generating and Sending Puts command")
    # Example: Send a Tcl command to Vivado
    tcl_command = "puts \"Hello from Python\"\n"
    vivado_process.stdin.write(tcl_command)
    vivado_process.stdin.flush()
    
    print("Starting Sleep")
    time.sleep(5)
    print("End of Sleep")

    # vivado_response = vivado_process.stdout.readline()
    #for line in vivado_response:
    
    
    
    
    
    
    # Example: Receive and print the response from Vivado
    # vivado_response = vivado_process.stdout.readline()
    # print(vivado_response)
    # vivado_response = vivado_process.stdout.readline()
    # print(vivado_response)
    # vivado_response = vivado_process.stdout.readline()
    # print(vivado_response)
    # vivado_response = vivado_process.stdout.readline()
    # print(vivado_response)
    # vivado_response = vivado_process.stdout.readline()
    # print(vivado_response)
    # vivado_response = vivado_process.stdout.readline()
    # print(vivado_response)
    # vivado_response = vivado_process.stdout.readline()
    # print(vivado_response)
    # vivado_response = vivado_process.stdout.readline()
    # print(vivado_response)
    # vivado_response = vivado_process.stdout.readline()
    # print(vivado_response)
    # vivado_response = vivado_process.stdout.readline()
    # print(vivado_response)
    # vivado_response = vivado_process.stdout.readline()
    # print(vivado_response)
    # vivado_response = vivado_process.stdout.readline()
    # print(vivado_response)
    # You can send more Tcl commands as needed
    # ...
    
    vivado_process.stdin.write("exit\n")
    vivado_process.stdin.flush()
    vivado_process.wait()
    
    print("Tcl commands executed successfully")
except subprocess.CalledProcessError as e:
    print(f"Error running Vivado: {e}")
