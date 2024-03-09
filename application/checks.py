import os

class DashesInHDLFileError(Exception):
    def __init__(self, message="Error: --- Dashes found in HDL Source File, have you completed HDLGen-ChatGPT workflow?"):
        self.message = message
        super().__init__(self.message)

def check_for_dashes(path_to_hdl):
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