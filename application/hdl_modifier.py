import shutil
import os
import re


##############################################################
##### Make Copy and Inject from HDLGen Project (and XML) #####
##############################################################
def make_copy_and_inject(hdlgen_prj):
    if hdlgen_prj.project_language == "VHDL":
        extension = ".vhd"
    elif hdlgen_prj.project_language == "Verilog":
        extension = ".v"
    # Given HDLGen Project - Make a backup, inject based on XML config.
    xml_object = hdlgen_prj.pynqbuildxml
    # Signals to inject
    list_of_int_sigs = xml_object.read_internal_to_port_config()
    # We now have a list of signals in the following form:
    # list_of_int_sigs = [
    #   ['name', width],
    #   ['signal_name', 8],     # NOTE: int_ prefix isn't attached.
    #   ['signal_name1', 4]
    # ]
    
    # Get Filepaths for Backup
    model_file = hdlgen_prj.model_file + extension
    backup_file = hdlgen_prj.model_file + ".socbuilder"

    # Create Backup
    make_backup(model_file, backup_file)
    
    # Inject VHDL to the originally named file.
    for signal in list_of_int_sigs:
        new_port_name = f"int_{signal[0]}"
        internal_name = signal[0]
        gpio_wdith = signal[1]
        if hdlgen_prj.project_language == 'VHDL':
            make_internal_vhdl_signal_external(model_file, new_port_name, internal_name, gpio_wdith)
        elif hdlgen_prj.project_language == "Verilog":
            print("VERILOG NOT SUPPORTED YET")
            # make_internal_verilog_signal_external(model_file, new_port_name, internal_name, gpio_wdith)

##############################################
##### Restore from HDLGen Project Object #####
##############################################
def restore(hdlgen_prj):
    if hdlgen_prj.project_language == "VHDL":
        extension = ".vhd"
    elif hdlgen_prj.project_language == "Verilog":
        extension = ".v"
    # Derive the filepaths
    model_file = hdlgen_prj.model_file + extension
    backup_file = hdlgen_prj.model_file + ".socbuilder"
    modified_file_backup = hdlgen_prj.model_file + ".modified"

    make_backup(backup_file, modified_file_backup)
    # Restore backup
    restore_backup(model_file, backup_file)

########################################################
##### Backup Original File (Verilog/VHDL/anything) #####
########################################################
def restore_backup(original_filename, backup_filename):
    try:
        shutil.copy(backup_filename, original_filename)
        # os.remove(backup_filename)    # Don't delete backup for debugging purposes
        print(f"Backup '{backup_filename}' restored as '{original_filename}' and deleted.")
    except FileNotFoundError:
        print("Error: Backup file not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

#########################################################
##### Restore Original File (Verilog/VHDL/anything) #####
#########################################################
def make_backup(original_filename, backup_filename):
    try:
        shutil.copy(original_filename, backup_filename)
        print(f"Backup Created: {original_filename} > {backup_filename}")
    except FileNotFoundError:
        print(f"Error: File {original_filename} not found.")
    except Exception as e:
        print(f"Exception: {e}")

#####################################################################
##### Make an internal signal in VHDL model available as a port #####
#####################################################################
def make_internal_vhdl_signal_external(vhdl_file, port_name, internal_signal_name, internal_signal_size):

    # First, we add to port map.
    inject_vhdl_port_signal(vhdl_file, port_name, internal_signal_size)

    # Then we add the assignation
    inject_vhdl_assignment_statement(vhdl_file, port_name, internal_signal_name)

#####################################
##### Add Port to VHDL Port Map #####
#####################################
def inject_vhdl_port_signal(vhdl_file, port_name, port_size):
    port_definition = ""
    if port_size == 1:
        port_definition += f"\t{port_name} : out std_logic;\n"
    else:
        port_definition += f"\t{port_name} : out std_logic_vector({port_size-1} downto 0);\n"

    target_line = -1
    lines = None
    with open(vhdl_file, 'r') as file:
        lines = file.readlines()
    
        for line in lines:
            if "Port(" in line:
                target_line = lines.index(line)

    with open(vhdl_file, 'w') as file:
        lines.insert(target_line+1, port_definition)
        file.writelines(lines)

############################################
##### Inject VHDL Assignment Statement #####
############################################
def inject_vhdl_assignment_statement(vhdl_file, target_signal, source_signal):
    target_line = -1
    lines = None
    with open(vhdl_file, 'r') as file:
        lines = file.readlines()
    
        for line in lines:
            if "begin" in line:
                target_line = lines.index(line)
                break

    with open(vhdl_file, 'w') as file:
        lines.insert(target_line+1, f"{target_signal} <= {source_signal};\n")
        file.writelines(lines)

########################################################################
##### Make an internal signal in Verilog model available as a port #####
########################################################################
def make_verilog_internal_signal_an_output():
    pass
