import os

#
# # main_cli.py
# Author: Luke Canny
# Date: 10/10/23
#
# Purpose:
#   Driver program for automating synthesis, implementation, bd creation and exportation
#
#

## Options to be set by the user
vivado_bat_location = ""
hdlgen_project_filepath = ""


version = "0.1"
# states = ['init', 'main', 'open_project', 'exit']
ns = 'init'

def init():
    global ns, hdlgen_project_filepath # ns needs to be set in every state function

    # Run the relevant code 
    hdlgen_project_filepath = input("Please Enter the Path to the HDLGen project file: ")       # TODO Is this the only information we need to get this working with HDLGen projects

    if os.path.exists(hdlgen_project_filepath):
        print("Project Found: Proceeding to main state")
        ns = 'main'     # Set the next state before ending the function
    else:
        print("Project Not Found")
        ns = None       # Set the next state before ending the function

def main():
    global ns

    print("== Main ==")
    print("Starting build process")



    # print("\nMain Process Started")
    # print("At this point, a menu of options should appear")
    # print("OR the entire build process should begin, depends if any options exist.")
    ns = None # Quit program

if __name__ == "__main__":
    print(f"===== Masters Automation v{version} =====")
    while(True):
        if ns == 'init':
            init()
        elif ns == 'main':
            main()
        else:
            print("No/Invalid State Selected, closing program")
            break
else:
    pass # Script has been imported as a module

