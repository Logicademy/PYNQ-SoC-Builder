import os
import xml.dom.minidom

class DashesInHDLFileError(Exception):
    def __init__(self, message="Error: --- Dashes found in HDL Source File, have you completed HDLGen-ChatGPT workflow?"):
        self.message = message
        super().__init__(self.message)

def check_for_dashes(hdlgen_project):
    
    hdlgen = xml.dom.minidom.parse(hdlgen_project)
    root = hdlgen.documentElement

    # Project Manager - Settings
    projectManager = root.getElementsByTagName("projectManager")[0]
    projectManagerSettings = projectManager.getElementsByTagName("settings")[0]
    name = projectManagerSettings.getElementsByTagName("name")[0].firstChild.data
    environment = projectManagerSettings.getElementsByTagName("environment")[0].firstChild.data
    location = projectManagerSettings.getElementsByTagName("location")[0].firstChild.data

    # Project Manager - HDL
    projectManagerHdl = projectManager.getElementsByTagName("HDL")[0]
    language = projectManagerHdl.getElementsByTagName("language")[0]
    project_language = language.getElementsByTagName("name")[0].firstChild.data

    # genFolder - VHDL Folders
    genFolder = root.getElementsByTagName("genFolder")[0]
    mode = ""
    try:
        model_folder = genFolder.getElementsByTagName("vhdl_folder")[0]
        mode = ".vhd"
    except Exception:
        model_folder = genFolder.getElementsByTagName("verilog_folder")[0]
        mode = ".v"
    model_folder_rel_path = model_folder.firstChild.data    
    
    path_to_hdl = environment + "/" + model_folder_rel_path + "/" + name + mode
    path_to_hdl = path_to_hdl.replace("\\", "/")
    print(path_to_hdl)
    
    try:
        with open(path_to_hdl, 'r') as file:
            # Flag to check if "architecture" has been found
            architecture_found = False

            for line in file:
                if line.startswith("architecture"):
                    architecture_found = True
                    print("Found line starting with 'architecture':", line)
                    continue  # Skip processing further for lines before "architecture"

                if architecture_found and line.startswith("---"):
                    print("Found line starting with '---' after 'architecture':", line)
                    raise DashesInHDLFileError
                    # You can add further processing or break out of the loop here if needed

        print(f"{path_to_hdl} passed --- check.")
    except FileNotFoundError:
        print(f"Error: File '{path_to_hdl}' not found.")
        raise FileNotFoundError

    except Exception as e:
        print(f"An error occurred: {e}")
        raise e