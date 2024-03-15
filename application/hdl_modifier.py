import shutil
import os
import re

########################################################
##### Backup Original File (Verilog/VHDL/anything) #####
########################################################
def restore_backup(backup_filename, original_filename):
    try:
        shutil.copy(backup_filename, original_filename)
        os.remove(backup_filename)
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
def make_internal_vhdl_signal_external():
    pass

#####################################
##### Add Port to VHDL Port Map #####
#####################################
def inject_vhdl_port_signal(vhdl_file, new_port_signal):
    target_line = -1
    lines = None
    with open(vhdl_file, 'r') as file:
        lines = file.readlines()
    
        for line in lines:
            if "Port(" in line:
                target_line = lines.index(line)

    with open(vhdl_file, 'w') as file:
        lines.insert(target_line+1, new_port_signal)
        file.writelines(lines)

# Example usage:
# inject_port_signal("DSPProc.vhd", "rs1 : out std_logic;")

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
                print("We found line")
                target_line = lines.index(line)
                break

    with open(vhdl_file, 'w') as file:
        lines.insert(target_line+1, f"    {target_signal} <= {source_signal}\n")
        file.writelines(lines)

# Example usage:
# inject_assignment_statement("DSPProc.vhd", "rs1", "DSP_memWr")

########################################################################
##### Make an internal signal in Verilog model available as a port #####
########################################################################
def make_verilog_internal_signal_an_output():
    pass


#####################
##### Test Code #####
#####################
example_file = "Untitled.vhd"
backup_file = "Untitled.vhd.socbuild"
make_backup(example_file, backup_file)
inject_vhdl_port_signal(backup_file, "        o_NS : out std_logic_vector(3 downto 0),\n")
inject_vhdl_port_signal(backup_file, "        o_CS : out std_logic_vector(3 downto 0),\n")
inject_vhdl_assignment_statement(backup_file, "o_NS", "NS")
inject_vhdl_assignment_statement(backup_file, "o_CS", "CS")
restore_backup(backup_file, "Complete.vhd")