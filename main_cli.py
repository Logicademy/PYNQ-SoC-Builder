import pynq_manager as pm
import os
import sys
import shutil

def get_hdlgen_path_from_user():
    hdlgen_path_unclean = input("Please Enter Path to HDLGen File (or q to quit): ")
    
    if hdlgen_path_unclean.startswith('"') and hdlgen_path_unclean.endswith('"'):
        hdlgen_path_unclean = hdlgen_path_unclean.strip('"')

    if os.path.isfile(hdlgen_path_unclean):
        print("-> Found HDLGen file opening project")
        return hdlgen_path_unclean
    else:
        if hdlgen_path_unclean == "q":
            quit_app()
        print("-> Could not find HDLGen file")
        return None

def quit_app():
    print("========== Quitting ==========")
    sys.exit()

def print_splash_return_choice():
    print("========== Select an Option ==========")
    print("0) RUN ALL BUILD STEPS")
    print("1) Generate Tcl Build Script")
    print("2) Run Vivado")
    print("3) Copy Bitstream Files")
    # print("4) Generate Notebook with Test Plan")
    # print("5) Generate Notebook without Test Plan")
    print("q) Quit")
    user_choice = input("Option: ")
    possible_options = ["1", "2", "3", "4", "5", "0", "q"]
    if user_choice in possible_options:
        if user_choice == "q":
            quit_app()
        return user_choice
    else:
        while user_choice not in possible_options:
            print("-> Invalid Option Selected")
            user_choice = input("Input: ")
    
def prepare_output_folder():
    folder_path = os.getcwd() + "\\output"
    if os.path.exists(folder_path):
            # If the folder exists, delete its contents
            print(f"-> Folder '{folder_path}' exists. Deleting contents...")
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"Failed to delete {file_path}. Reason: {e}")
    else:
        # If the folder does not exist, create it
        print(f"-> Folder '{folder_path}' does not exist. Creating...")
        os.makedirs(folder_path)



def gen_tcl(pynq_manager):
    print("== Generate Tcl Build Script ==")
    print("-> Generating script")
    regenerate_bd = False # Default
    if pynq_manager.get_bd_exists():
        print("== Block Design already exists, would you like to regenerate a new one (existing BD is deleted)? (y/n)")
        response = input("Input: ")
        while (response != "y") and (response != "n"):
            response = input("Invalid Response (y/n): ")
        if response == "y":
            regenerate_bd = True
        elif response == "n":
            regenerate_bd = False

    pynq_manager.generate_tcl(regenerate_bd)
    print("-> Tcl script generated")

def run_viv(pynq_manager):
    print("== Run Build Script in Vivado ==")
    print("-> Launching Vivado")
    pynq_manager.run_vivado()
    print("-> Script Completed")

def copy_out(pynq_manager):
    print("== Copying Output Bitstream ==")
    print("-> Preparing output folder")
    prepare_output_folder()
    print(f"-> Copying output bitstream to {os.getcwd()}")
    pynq_manager.copy_to_dir(os.getcwd() + "\\output")

def run_all(pynq_manager):
    gen_tcl(pynq_manager)
    run_viv(pynq_manager)
    copy_out(pynq_manager)

def main():
    print("========== PYNQ Automate ==========")
    hdlgen_path = None
    while hdlgen_path == None:
        hdlgen_path = get_hdlgen_path_from_user()

    print("-> Pynq_Manager loaded")
    pynq_manager = pm.Pynq_Manager(
        hdlgen_path
    )

    while True:
        choice = print_splash_return_choice()
        if choice == "1":
            gen_tcl(pynq_manager)
        
        elif choice == "2":
            run_viv(pynq_manager)
        
        elif choice == "3":
            copy_out(pynq_manager)

        elif choice == "4":
            print("Generate with test plan not implemented yet")
            pass
        elif choice == "5":
            print("Generate without test plan not implemented yet")
            pass
        elif choice == "0":
            run_all(pynq_manager)
            pass



if __name__ == "__main__":
    main()