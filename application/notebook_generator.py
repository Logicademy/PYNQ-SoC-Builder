import nbformat as nbf
import xml.dom.minidom
import csv
from io import StringIO
import html
import os
import application.xml_manager as xmlman
import copy 

# Function to generate JNB, takes HDLGen file path and notebook name as parameters
def create_jnb(hdlgen_prj, add_to_log_box, force_gen=False):
    # Read from XML.
    proj_config = hdlgen_prj.pynqbuildxml.read_proj_config()
    io_map = hdlgen_prj.pynqbuildxml.read_io_config()

    try:
        gen_jnb = proj_config['gen_jnb']
    except Exception as e:
        add_to_log_box("\nCouldn't load gen_jnb setting from XML - using default: True")
    finally:
        if not isinstance(gen_jnb, bool): # Check if the value is a boolean when finishing 
            gen_jnb = True
            add_to_log_box("\ngen_jnb not loaded as boolean, ignoring and using default: True")

    if not gen_jnb and not force_gen:
        add_to_log_box("\nGenerate JNB is False, quitting notebook_generate.py")
        return


    # Try to load from XML and sanitize the response
    use_board_io = False
    try:
        use_board_io = proj_config['use_board_io']
    except Exception as e:
        add_to_log_box("\nCouldn't load use_board_io setting from XML - using default: False")
    finally:
        if not isinstance(use_board_io, bool): # Check if the value is a boolean when finishing 
            use_board_io = False
            add_to_log_box("\nuse_board_io not loaded as boolean, ignoring and using default: False")



    # Try to load from XML and sanitize the response
    use_testplan = False
    try:
        use_testplan = proj_config['use_tstpln']
    except Exception as e:
        add_to_log_box("\nCouldn't load use_tstpln setting from XML - using default: False")
    finally:
        if not isinstance(use_board_io, bool): # Check if the value is a boolean when finishing 
            use_testplan = False
            add_to_log_box("\nuse_tstpln not loaded as boolean, ignoring and using default: False")

    # io_map == None means do not configure for IO
    # io_map == dictionary with io mapping, configure as such.
    if not use_board_io:
        io_map = None

    py_file_contents = ""   # This file is used to store the accompanying Python code for GUI controller, test APIs etc.

    # Py File Imports
    py_file_contents += "import ipywidgets as widgets"
    py_file_contents += "\nfrom IPython.display import SVG, display, HTML"
    py_file_contents += "\nfrom ipywidgets import GridspecLayout, Output, HBox"
    py_file_contents += "\nfrom ipywidgets import Button, Layout, jslink, IntText, IntSlider"
    py_file_contents += "\nfrom pynq import Overlay"
    py_file_contents += "\nimport pandas as pd"
    py_file_contents += "\nimport time"
    py_file_contents += "\nimport os"
    py_file_contents += "\nimport threading"

    ###############################################################################################################################
    ###### Whilst it is less efficient to let the Notebook Generator parse the HDLGen XML itself, it will take too long       #####
    ###### to update it to use hdlgen_prj object as there is a LOT of custom parsing which is only needed by the Notebook Gen #####
    ###### Therefore, for now, this is going to be left. It could be updated in the future although their may not be any need #####
    ###############################################################################################################################


    # Open HDLGen xml and get root node.
    hdlgen = xml.dom.minidom.parse(hdlgen_prj.hdlgen_path)
    root = hdlgen.documentElement

    # Project Manager - Settings
    projectManager = root.getElementsByTagName("projectManager")[0]
    projectManagerSettings = projectManager.getElementsByTagName("settings")[0]
    
    # Settings Data
    name = projectManagerSettings.getElementsByTagName("name")[0].firstChild.data
    environment = projectManagerSettings.getElementsByTagName("environment")[0].firstChild.data
    location = projectManagerSettings.getElementsByTagName("location")[0].firstChild.data

    # hdlDesign - header
    hdlDesign = root.getElementsByTagName("hdlDesign")[0]
    hdlDesignHeader = hdlDesign.getElementsByTagName("header")[0]
    compName = hdlDesignHeader.getElementsByTagName("compName")[0].firstChild.data
    title = hdlDesignHeader.getElementsByTagName("title")[0].firstChild.data
    description = hdlDesignHeader.getElementsByTagName("description")[0].firstChild.data
    authors = hdlDesignHeader.getElementsByTagName("authors")[0].firstChild.data
    company = hdlDesignHeader.getElementsByTagName("company")[0].firstChild.data
    email = hdlDesignHeader.getElementsByTagName("email")[0].firstChild.data
    date = hdlDesignHeader.getElementsByTagName("date")[0].firstChild.data
    # hdlDesign - entityIOPorts 
    entityIOPorts = hdlDesign.getElementsByTagName("entityIOPorts")[0]
    signals = entityIOPorts.getElementsByTagName("signal")

    all_ports = []
    for sig in signals:
        signame = sig.getElementsByTagName("name")[0]
        mode = sig.getElementsByTagName("mode")[0]
        type = sig.getElementsByTagName("type")[0]
        desc = sig.getElementsByTagName("description")[0]
        all_ports.append(
            [signame.firstChild.data, mode.firstChild.data, type.firstChild.data, desc.firstChild.data]
        )

    # Separating signals into input and outputs, enable clock mode if clk exists;
    clock_enabled = False
    input_ports = []
    output_ports = []
    output_ports_names = []
    for port in all_ports:
        if port[0] == 'clk':
            clock_enabled = True
        if port[1] == "in":
            input_ports.append(port)
        elif port[1] == "out":
            output_ports.append(port)
            output_ports_names.append(port[0])
        else:
            print("Line 59 NBG: Invalid Port")

    # parsed_all_ports = parse_all_ports(all_ports)
    # Being extra careful, I want to copy the values
            # next_var = copy.deepcopy(object.its_var)
    parsed_all_ports = []

    # parsed_internal_sigs = copy.deepcopy(hdlgen_prj.parsed_internal_sigs)
    parsed_internal_sigs = hdlgen_prj.pynqbuildxml.read_internal_to_port_config()


    original_ports = parse_all_ports(all_ports)

    for int in parsed_internal_sigs:
        gpio_name = f"int_{int[0]}"
        gpio_mode = "out"
        gpio_width = int[1]
        parsed_all_ports.append([gpio_name, gpio_mode, gpio_width])

    for port in original_ports:
        gpio_name = port[0]
        gpio_mode = port[1]
        gpio_width = port[2]
        parsed_all_ports.append([gpio_name, gpio_mode, gpio_width])

    # Retrieve TB Data from HDLGen
    testbench = root.getElementsByTagName("testbench")[0]
    try:
        TBNote = testbench.getElementsByTagName("TBNote")[0]
        TBNoteData = TBNote.firstChild.data
    except Exception:
        print("No TBNoteData - asserting no testplan generation")
        use_testplan = False
    
    
    # Test bench parsing code
    if use_testplan:
        # Parsing TB data into variables
        # Convert HTML entities into their coorresponding characters
        decoded_string = html.unescape(TBNoteData)
        # Replace &#x9; with actual tabs
        tsv_string = decoded_string.replace("&#x9;", "\t")
        # Read TSV string into a CSV reader
        tsv_reader = csv.reader(StringIO(tsv_string), delimiter='\t')
        
        tsv_data_filtered = []
        for row in tsv_reader:
            if all(element == "" for element in row):
                pass    # Skip empty lines
            elif row == []:
                pass
            elif row and row[0] and row[0][0] == '#':
                pass
            else:
                tsv_data_filtered.append(row)
        # Convert CSV reader into a list of lists
        tsv_data = [row for row in tsv_reader]

        # for row in tsv_data_filtered:
        #     print(row)

        signals_line = ""
        mode_line = ""
        radix_line = ""
        test_cases = []

        for row in tsv_data_filtered:
            if row[0] == '#':
                pass
            elif row[0] == '=':
                pass
            elif row[0] == 'Signals':
                signals_line = row
            elif row[0] == 'Mode':
                mode_line = row
            elif row[0] == 'Radix':
                radix_line = row
            else:
                test_cases.append(row)

        # Need to add checks here that if Signals, Mode, or Radix are empty to crash gracefully.



        # print("Signals: ", signals_line)
        # print("Mode: ", mode_line)
        # print("Radix: ", radix_line)

        signals_tb = []
        for i in range(len(signals_line)):  # range(1, len(signals_line)-3)
            signals_tb.append([signals_line[i], mode_line[i], radix_line[i]])
    
        # print("Test Cases")
        # for t in test_cases:
        #     print(t)

    ####### Start of JNB Generation #######
    
    # Create new Jupyter Notebook
    notebook = nbf.v4.new_notebook()

    # Title Cell
    markdown_cell = nbf.v4.new_markdown_cell(f"# {title}")
    notebook.cells.append(markdown_cell) # Add cell to notebook

    # Python Set Up Markdown Block
    markdown_cell = nbf.v4.new_markdown_cell(f"#### Python Environment Set Up")
    notebook.cells.append(markdown_cell)
    
    code_cell_contents = f"%run {compName}.py"
    code_cell = nbf.v4.new_code_cell(code_cell_contents)
    notebook.cells.append(code_cell)

    # Component Description
    markdown_cell = nbf.v4.new_markdown_cell(f"## Component Description\n\n{description}")
    notebook.cells.append(markdown_cell) 

    # Entity IO
    markdown_cell_contents = f"## Entity I/O\n\n| Name | Mode | Type | Description |\n|:----:|:----:|:----:|:------------|"
    for s in all_ports:
        markdown_cell_contents += f"\n| {s[0]} | {s[1]} | {s[2]} | {s[3]} |"
    markdown_cell = nbf.v4.new_markdown_cell(markdown_cell_contents)
    notebook.cells.append(markdown_cell)



    # Python Set Up Code Block
    # Import Overlay
    py_file_contents += "\n\n# Import Overlay"
    py_file_contents += f"\n{compName} = Overlay(\"{compName}.bit\")"

    # This portion needs to be remodelled to support >32 bit signals which have been divided.

    # code_cell_contents += "\n# Inputs:"
    # for i in input_ports:
    #     code_cell_contents += f"\n{i[0]} = {compName}.{i[0]}"
    # code_cell_contents += "\n# Outputs:"
    # for o in output_ports: 
    #     code_cell_contents += f"\n{o[0]} = {compName}.{o[0]}"

    split_signals = []  # This is the sublist which is used to declare all signals
    large_output_signals = []   # This stores an array of arrays containing the split signals [ ["dIn_0_31", "dIn_32_63"], ["data_0_31", "data_32_63"] ]
    large_input_signals = []    # This does the exact same but split for inputs.
    small_output_signals = []   # Smaller signals that can be stored alone.
    small_input_signals = []    # Smaller signals that can be stored alone (<32 bits)
    
    # for io in all_ports:
    #     gpio_name = io[0]   # GPIO Name
    #     gpio_mode = io[1]   # GPIO Mode (in/out)
    #     gpio_type = io[2]   # GPIO Type (single bit/bus/array)
    #     # Parse GPIO Width 
    #     if (gpio_type == "single bit"):
    #             gpio_width = 1
    #     elif (gpio_type[:3] == "bus"):
    #         # <type>bus(31 downto 0)</type>     ## Example Type Value
    #         substring = gpio_type[4:]           # substring = '31 downto 0)'
    #         words = substring.split()           # words = ['31', 'downto', '0)']
    #         gpio_width = int(words[0]) + 1           # words[0] = 31
    #     elif (gpio_type[:5] == "array"):
    #         print("ERROR: Array mode type is not yet supported :(")
    #     else:
    #         print("ERROR: Unknown GPIO Type")
    #         print(gpio_type)

    for io in parsed_all_ports:
        gpio_name = io[0]
        gpio_mode = io[1]
        gpio_width = io[2]

        if gpio_width <= 32:
            # If less than 32, declare signal as normal.
            
            split_signals.append([gpio_name, gpio_width])
            if gpio_mode == "out":
                small_output_signals.append(gpio_name)
            elif gpio_mode == "in":
                small_input_signals.append(gpio_name)


        elif gpio_width > 32:
            # If greater than 32, split signals and declare.
            pin_counter = 0
            output_split = [gpio_name]
            input_split = [gpio_name]
            while gpio_width - pin_counter > 0:
                if gpio_width - pin_counter  > 32:
                    signal_name = f"{gpio_name}_{pin_counter+31}_{pin_counter}"
                    signal_width = 32
                    split_signals.append([signal_name, signal_width])
                    if gpio_mode == "out":
                        output_split.append(signal_name)
                    else:
                        input_split.append(signal_name)
                    pin_counter += 32
                elif gpio_width - pin_counter <= 32:
                    # signal_name = gpioName_X_downto_Y -> gpio_name_X_Y
                    signal_name = f"{gpio_name}_{gpio_width-1}_{pin_counter}"
                    signal_width = gpio_width-pin_counter
                    split_signals.append([signal_name, signal_width])
                    if gpio_mode == "out":
                        output_split.append(signal_name)
                    else:
                        input_split.append(signal_name)
                    pin_counter += gpio_width - pin_counter
                    
            if len(output_split) > 1:
                large_output_signals.append(output_split)
            if len(input_split) > 1:
                large_input_signals.append(input_split)
                    
        
    py_file_contents += "\n\n# Declare Signal Objects"
    for sig in split_signals:
        py_file_contents += f"\n{sig[0]} = {compName}.{sig[0]}"

    # Create large classes from Port Map
    py_file_contents += "\n\n# Class wrappers for large (>32bit) signals\n" + create_large_classes_from_port_map(parsed_all_ports)

    py_file_contents += "\n\n# Split Number into Blocks Function"
    py_file_contents += "\ndef split_into_blocks(number, num_blocks):"
    py_file_contents += "\n\tblock_size = 32"
    py_file_contents += "\n\tmask = (1 << block_size) - 1  # Create a mask with 32 bits set to 1"
    py_file_contents += "\n\tblocks = []"
    py_file_contents += "\n\tfor i in range(0, 32*num_blocks, block_size):"
    py_file_contents += "\n\t\tblock = (number & mask)"
    py_file_contents += "\n\t\tblocks.append(block)"
    py_file_contents += "\n\t\tnumber >>= block_size"
    py_file_contents += "\n\treturn blocks"


    if clock_enabled:
        py_file_contents += "\n\n# Set-Up Clock Function\ndef run_clock_pulse():"
        py_file_contents += "\n\ttime.sleep(0.0000002)"
        py_file_contents += "\n\tclk.write(0,1)"
        py_file_contents += "\n\ttime.sleep(0.0000002)"
        py_file_contents += "\n\tclk.write(0,0)\n"
    
    # This step checks if the IO is configured or just completely empty.
    # If completely empty, lets just skip.
    gen_io_gui = False
    if io_map:
        for key, value in io_map.items():
            if value != "None" and value != None:
                gen_io_gui = True
                break
    
    if io_map and gen_io_gui:
        markdown_cell_contents = f"## IO Visualised\n\n"

        markdown_cell_contents += "\n| PYNQ I/O | Component Signal |"
        markdown_cell_contents += "\n|:----:|:----:|"

        for pynq_io, comp_io in io_map.items():
            if comp_io == "None" or comp_io == None:
                continue    # Skip non-connections
            markdown_cell_contents += f"\n| {pynq_io} | {comp_io[0]}[{str(comp_io[1])}] |"

        markdown_cell = nbf.v4.new_markdown_cell(markdown_cell_contents)
        notebook.cells.append(markdown_cell)
        
        code_cell = nbf.v4.new_code_cell(f"display(generate_io_gui())")
        notebook.cells.append(code_cell)

        py_file_contents += generate_io_visuals(io_map)

    # Here we need to insert GUI Controller.
    gui_controller = True
    if gui_controller:
        markdown_cell = nbf.v4.new_markdown_cell(f"## Component Controller")
        notebook.cells.append(markdown_cell)
        code_cell = nbf.v4.new_code_cell(f"display(generate_gui(svg_content))")
        notebook.cells.append(code_cell)

        # Here we need to write the GUI based code and add it to the py_code_contents

        # FIX: This needs to contain the UPDATED parsed ports including internal signals.
        # NOTE: It would be better to convert this script to use hdlgen_prj only but I'm not doing that right now.
 

        py_file_contents += generate_gui_controller(compName, parsed_all_ports, location)

    ##### Break here if only dealing with skeleton code.
    # Possible To-do here is a "example" cell showing how to use signals

    if use_testplan:

        # Testbench Plan Title Cell
        markdown_cell = nbf.v4.new_markdown_cell("# Test Plan")
        notebook.cells.append(markdown_cell) 

        # Testbench Plan Cell
        markdown_cell_contents = ""
        # Row 1 Signals:
        markdown_cell_contents += "| "
        for s in signals_line:
            markdown_cell_contents += s + " | "
        markdown_cell_contents += "\n|"
        for s in signals_line:
            markdown_cell_contents += ":----:|"
        # Row 2 Mode:
        markdown_cell_contents += "\n| "
        for m in mode_line:
            markdown_cell_contents += m + " | "
        # Row 3 Radix:
        markdown_cell_contents += "\n| "
        for r in radix_line:
            markdown_cell_contents += r + " | "
        # Row 4+ Test Cases:
        for test in test_cases:
            markdown_cell_contents += "\n| "
            for t in test:
                markdown_cell_contents += t + " | "

        markdown_cell = nbf.v4.new_markdown_cell(markdown_cell_contents)
        notebook.cells.append(markdown_cell)


        # Test Set Up Python Code Block
        # markdown_cell = nbf.v4.new_markdown_cell("# Test Execution Set-Up Code")
        # notebook.cells.append(markdown_cell) 

        ############################## TEST CASE SET UP PYTHON BLOCK #################################
        ######## This section looks like it is generating for a code block but it is actually ########
        ######## being sent to the supplementary Python file.                                 ########
        ##############################################################################################

        code_cell_contents = "# Test Case Set Up"
        code_cell_contents += f"\n# Number Of Test Cases: {len(test_cases)}"
        code_cell_contents += f"\ntest_results = [None] * {len(test_cases)}"
        
        # 1) Create output signals array
        # 2) Read each output signal signal.read(0)
        # 3) Store results as test_results[test] = [signal1_val, signal2_val, signal3_val]
        sub_signals = signals_line[1:-3]
        sub_modes = mode_line[1:-3]
        sub_radix = radix_line[1:-3]  
        output_radix = []

        # Generate output_signals = ["signal1", "signal2", "signal3"...]
        output_signals_string = "\noutput_signals = ["
        for i in range(len(sub_signals)):
                if sub_modes[i] == "out":
                    output_signals_string += "'"+sub_signals[i] + "', " # signal1, 
        output_signals_string = output_signals_string[:-2] + "]" # delete the last ", " and add "]" instead
        code_cell_contents += output_signals_string

        # Loop Outputs
                    
        code_cell_contents += "\nexpected_results = ["
        
        for test_num in range(0,len(test_cases)):
            
            code_cell_contents += " ["
            for i in range(len(sub_signals)):
                if sub_modes[i] == "out":
                    try:
                        if sub_radix[i][-1] == "h":
                            code_cell_contents += f"\"0x{test_cases[test_num][i+1]}\", "
                        elif sub_radix[i][-1] == "b":
                            code_cell_contents += f"\"0b{test_cases[test_num][i+1]}\", "
                        if sub_radix[i][-1] == "d":
                            code_cell_contents += f"\"{test_cases[test_num][i+1]}\", "
                    except Exception:
                        pass   

            code_cell_contents = code_cell_contents[:-2] + " ], "
        code_cell_contents = code_cell_contents[:-2] + " ]"

        code_cell_contents += "\n# Functions for Storing/Printing Test Results"
        code_cell_contents += "\ndef color_test_passed(val):"
        code_cell_contents += "\n\tcolor = 'green' if val else 'red'"
        code_cell_contents += "\n\treturn f'background-color: {color}; color: white;'"

        code_cell_contents += "\n\n# Pad Hex or Binary Values to Same Length as Reference"
        #### PAD HEX OR BINARY VALUES
        # Twp different functions were made to do this. I choose first as it was shorter.
        # The second option accepts number of bits instead of a comparative view. I think comparative is better for this.
        code_cell_contents += "\ndef pad_hex_or_bin(val_to_pad, comparison_val):"
        code_cell_contents += "\n\tpadded_hex = f\"{val_to_pad[:2]}{val_to_pad[2:].zfill(len(comparison_val[2:]))}\" # Pad if necessary"
        code_cell_contents += "\n\treturn padded_hex"

        # def pad_hex_or_bin(val_to_pad, bits)
        #     if val_to_pad[1] == "x":
        #         padded_hex = f"0x{val_to_pad[2:].zfill(bits // 4 + 1 if bits % 4 > 1 else bits // 4)}"
        #     elif val_to_pad[1] == "b": # pad
        #         padded_hex = f"0b{val_to_pad[2:].zfill(bits)}"
        #     else
        #         return val_to_pad # If its neither binary or hex just return number again



        code_cell_contents += "\n\ndef save_and_print_test(test=None):"
        code_cell_contents += "\n\tif None:"
        code_cell_contents += "\n\t\tprint('No Test Number Provided')"
        code_cell_contents += f"\n\telif test >= 0 and test <= {len(test_cases)-1}: # number of tests"

        read_signals_string = ""
        
        for sig in small_output_signals:
            read_signals_string += "\n\t\t" + sig + "_val = " + sig + ".read(0)"    # reading each (small <32 bit) signal
        
        for sig_array in large_output_signals:
            top_level_signal = sig_array[0]
            for sig in sig_array[1:]:
                read_signals_string += "\n\t\t" + sig + "_val = " + sig + ".read(0)"    # reading each (small <32 bit) signal
            read_signals_string += "\n\t\t" + top_level_signal + "_val =" 
            read_sigs_substring = ""
            for x in range(1, len(sig_array)): # 1 as first element is top_level name
                read_sigs_substring = f" | ({sig_array[x]}_val << {32*(x-1)})" + read_sigs_substring
            read_signals_string += read_sigs_substring[2:]

        code_cell_contents += read_signals_string

        # for i in range(len(sub_signals)):
        #     if sub_modes[i] == "out":

        #         # dOut_32_63_val = dOut_32_63.read(0)
        #         # dOut_0_31_val = dOut_0_31.read(0)
        #         # dOut_val = (dOut_32_63_val << 32) | dOut_0_31_val

        #         # String 2 here 

        #         read_signals_string += "\n\t\t" + sub_signals[i] + "_val = " + sub_signals[i] + ".read(0)"    # reading each signal   <- Working perfectly
                    
        
        test_results_string = "\n\t\ttest_results[test] = ["
        out_count = 0
        for i in range(len(sub_signals)):
                if sub_modes[i] == "out":
                    try:
                        if sub_radix[i][-1] == "h":
                            test_results_string += f"pad_hex_or_bin(hex({sub_signals[i]}_val), expected_results[test][{out_count}]), "
                        elif sub_radix[i][-1] == "b":
                            test_results_string += f"pad_hex_or_bin(bin({sub_signals[i]}_val), expected_results[test][{out_count}]), "
                        if sub_radix[i][-1] == "d":
                            test_results_string += f"str({sub_signals[i]}_val), "
                        out_count += 1
                    except Exception:
                        pass                    
                    output_radix.append(sub_radix[i])

        test_results_string = test_results_string[:-2] + "]" # delete the last 

        code_cell_contents += test_results_string
        
        code_cell_contents += "\n\t\tdf = pd.DataFrame({"
        code_cell_contents += "\n\t\t\t'Signal': output_signals,"
        code_cell_contents += "\n\t\t\t'Expected Result': expected_results[test],"
        code_cell_contents += "\n\t\t\t'Observed Result': test_results[test],"
        code_cell_contents += "\n\t\t\t'Test Passed?': [a == b for a, b in zip(expected_results[test], test_results[test])]"
        code_cell_contents += "\n\t\t})"
        code_cell_contents += "\n\t\treturn df.style.applymap(color_test_passed, subset=['Test Passed?'])"
        code_cell_contents += "\n\telse:"
        code_cell_contents += "\n\t\tprint('Invalid Test Number Provided')"

        #### END OF PYTHON TEST CASE SET UP CODE BLOCK - SENDING TO PYTHON FILE ####
        py_file_contents += "\n\n# Test Case Set Up Code\n\n" + code_cell_contents

        # code_cell = nbf.v4.new_code_cell(code_cell_contents)
        # notebook.cells.append(code_cell)

        # Loop to Generate each test case
        test_number = 0
        delay_total = 0 


        # signals_line
        

        for test in test_cases:

            # print(f"Generating for test case {test_number}")
            # print(test)
            
            filtered_test = list(filter(None, test))

            test_converted_to_decimal_from_radix_dictionary = {}
            test_converted_to_decimal_from_radix = []
            for val in range(0, len(filtered_test)-3): # minus three to ignore note, test no, and delay.
                radix_val = radix_line[val+1]   # This should be fine, +1 to skip "Radix" at start of line
                radix_form = radix_val.strip()    # trim whatever whitespace that might be there
                radix_form = radix_form[-1]        # Radix form is the last letter in value
                radix_number = radix_val.split("'")[0]  # Number in radix


                value = filtered_test[val]
                signal_name = signals_line[val+1]

                if radix_form == 'h':
                    # If the signal is short, just story it, if the signal is large then we want to divide it into 32 bit chunks
                    
                    # Bypassing splits
                    
                    # if signal_name in small_input_signals:
                    if True:
                        test_converted_to_decimal_from_radix_dictionary[signal_name] = f"int(\"{value}\", 16)"
                    else:
                        test_converted_to_decimal_from_radix_dictionary[signal_name] = hex_to_padded_chunks(value, radix_number)
                    

                    # Convert for hexidecimal
                    # decimal_value = int(value, 16)
                    # test_converted_to_decimal_from_radix.append(str(decimal_value))
                    test_converted_to_decimal_from_radix.append(f"int(\"{value}\", 16)")
                elif radix_form == 'b':
                    # Bypassing splitting now
                    # if signal_name in small_input_signals:
                    if True:
                        test_converted_to_decimal_from_radix_dictionary[signal_name] = f"int(\"{value}\", 2)"
                    # Convert for binary
                    # decimal_value = int(value, 2)
                    # test_converted_to_decimal_from_radix.append(str(decimal_value))
                    test_converted_to_decimal_from_radix.append(f"int(\"{value}\", 2)")
                elif radix_form == "d":
                    # if signal_name in small_input_signals:
                    if True:
                        test_converted_to_decimal_from_radix_dictionary[signal_name] = f"{value}"

                    
                    # Convert for binary
                    # decimal_value = int(value, 2)
                    # test_converted_to_decimal_from_radix.append(str(decimal_value))
                    test_converted_to_decimal_from_radix.append(f"{value}")
                else:
                    print(f"Warning: Could not detect radix form for: {radix_val}")
                
            # print(test_converted_to_decimal_from_radix)

            # Create title cell.
            

            # Testbench Plan Cell
            markdown_cell_contents = f"## Test Case: {test_number}\n\n"
            # Row 1 Signals:
            markdown_cell_contents += "| "
            for s in signals_line:
                markdown_cell_contents += s + " | "
            markdown_cell_contents += "\n|"
            for s in signals_line:
                markdown_cell_contents += ":----:|"
            # Row 2 Mode:
            markdown_cell_contents += "\n| "
            for m in mode_line:
                markdown_cell_contents += m + " | "
            # Row 3 Radix:
            markdown_cell_contents += "\n| "
            for r in radix_line:
                markdown_cell_contents += r + " | "
            # Row 4+ Test Cases:
            markdown_cell_contents += "\n| "
            for t in test_cases[test_number]:
                markdown_cell_contents += t + " | "

            markdown_cell = nbf.v4.new_markdown_cell(markdown_cell_contents)
            notebook.cells.append(markdown_cell)

            # Code Cell:
            # Generating Inputs:
            code_cell_contents = "# Asserting Inputs\n" 

            
            delay_total += float(filtered_test[-3])

            sub_signals = signals_line[1:-3]
            sub_modes = mode_line[1:-3]

            # for i in range(len(sub_signals)):
            #     if sub_modes[i] == "in":
            #         code_cell_contents += f"{sub_signals[i]}.write(0, {test_converted_to_decimal_from_radix[i]})\n"

            # test_converted_to_decimal_from_radix_dictionary
            for key, value in test_converted_to_decimal_from_radix_dictionary.items():
                # if isinstance(value, list):
                #     # Find the array in large_input_signals that has same name [1]
                #     for sig in large_input_signals:
                #         if sig[0] == key:
                #             # Found the signal names.
                #             for i in range(0, len(sig)-1):
                #                 code_cell_contents += f"{sig[i+1]}.write(0, int(\"{value[i]}\", 16))\n"
                    
                #     pass # deal with array
                # else:

                # If the port is NOT in the output GPIO then we should write to it
                if key not in output_ports_names:
                    code_cell_contents += f"{key}.write(0, {value})\n"

            while delay_total >= 1 and clock_enabled:
                # run clock 
                code_cell_contents += "\nrun_clock_pulse()"
                delay_total = delay_total - 1


            # Break
            code_cell_contents += "\n\n# Recording Outputs"
            code_cell_contents += f"\nsave_and_print_test({test_number})"

            test_number += 1    # Increment Test Number after use.
            code_cell = nbf.v4.new_code_cell(code_cell_contents)
            notebook.cells.append(code_cell)


        # Finally, presenting the results in a presentable fashion:
        # Title Markdown Cell
        # markdown_cell = nbf.v4.new_markdown_cell("# Test Results - Needs to be improved")
        # notebook.cells.append(markdown_cell)

        # code_cell_contents = "import pandas as pd\n"
        # code_cell_contents += "\ndf = pd.DataFrame({'Result': test_results})"
        # code_cell_contents += "\npd.set_option('display.notebook_repr_html', False)"
        # code_cell_contents += "\ndef highlight_cells(val):"
        # code_cell_contents += "\n\tif val == True:"
        # code_cell_contents += "\n\t\treturn 'background-color: green'"
        # code_cell_contents += "\n\telif val == False:"
        # code_cell_contents += "\n\t\treturn 'background-color: red'"
        # code_cell_contents += "\n\telse:"
        # code_cell_contents += "\n\t\treturn 'background-color: darkorange'"
        # code_cell_contents += "\nstyled_df = df.style.applymap(highlight_cells, subset=['Result'])"
        # code_cell_contents += "\nstyled_df"
        # code_cell = nbf.v4.new_code_cell(code_cell_contents)
        # notebook.cells.append(code_cell)

    # else: # I think this is doubling %run {compName}.py cell
    #     code_cell = nbf.v4.new_code_cell(code_cell_contents)
    #     notebook.cells.append(code_cell)
    
    output_file = f'{hdlgen_prj.pynq_build_output_path}\{name}.ipynb'
    # if output_filename is not None:
    #     output_file = output_filename
    print(output_file)  
    with open(output_file, 'w') as f:
        nbf.write(notebook, f)
        
    print(f"Notebook Generated at: {output_file}")

    output_py_file = f'{hdlgen_prj.pynq_build_output_path}\{name}.py'
    py_file_contents = py_file_contents.replace("\t", "    ")
    with open(output_py_file, 'w') as pyf:
        pyf.write(py_file_contents)

def hex_to_padded_chunks(hex_number, desired_bits):
    # Convert hex to binary and remove the '0b' prefix
    binary_representation = bin(int(hex_number, 16))[2:]
    # print(binary_representation)

    # Ensure the binary representation has a length that is a multiple of 32
    binary_representation = binary_representation.zfill(desired_bits)
    # print(binary_representation)

    # Calculate the number of chunks needed
    num_chunks = (len(binary_representation) + 31) // 32
    # print(num_chunks)

    flipped_binary = binary_representation[::-1]

    # Split the binary representation into 32-bit chunks and pad each chunk
    chunks = [flipped_binary[i*32:(i+1)*32] for i in range(num_chunks)]
    # print(chunks)

    flipped_chunks = chunks[::-1]
    # print(flipped_chunks)
    
    normalized_chunks = [element[::-1] for element in flipped_chunks]
    # print(normalized_chunks)
    # Convert each padded chunk back to hexadecimal
    # hex_chunks = [hex(int(chunk, 2))[2:].zfill(8) for chunk in padded_chunks]

    hex_arrays = [hex(int(binary, 2))[2:].zfill(len(binary) // 4) for binary in normalized_chunks]

    # print(hex_arrays)

    return hex_arrays

def generate_io_visuals(io_map):
    py_code = "\ndef generate_io_gui():"
    py_code += "\n\t# We need to create the LEDs."
    py_code += "\n\tled0_button = widgets.ToggleButton("
    py_code += "\n\t\tvalue=False,"
    py_code += "\n\t\tdescription='0',"
    py_code += "\n\t\tdisabled=True,"
    py_code += "\n\t\tbutton_style='danger'"
    py_code += "\n\t)"
    py_code += "\n\tled1_button = widgets.ToggleButton("
    py_code += "\n\t\tvalue=False,"
    py_code += "\n\t\tdescription='1',"
    py_code += "\n\t\tdisabled=True,"
    py_code += "\n\t\tbutton_style='danger'"
    py_code += "\n\t)"
    py_code += "\n\tled2_button = widgets.ToggleButton("
    py_code += "\n\t\tvalue=False,"
    py_code += "\n\t\tdescription='2',"
    py_code += "\n\t\tdisabled=True,"
    py_code += "\n\t\tbutton_style='danger'"
    py_code += "\n\t)"
    py_code += "\n\tled3_button = widgets.ToggleButton("
    py_code += "\n\t\tvalue=False,"
    py_code += "\n\t\tdescription='3',"
    py_code += "\n\t\tdisabled=True,"
    py_code += "\n\t\tbutton_style='danger'"
    py_code += "\n\t)"
    py_code += "\n\tleds_label = widgets.Label(value='LEDs')"

    py_code += "\n\tled4_r_button = widgets.ToggleButton("
    py_code += "\n\t\tvalue=False,"
    py_code += "\n\t\tdescription='r',"
    py_code += "\n\t\tdisabled=True,"
    py_code += "\n\t\tbutton_style='danger'"
    py_code += "\n\t)"
    py_code += "\n\tled4_g_button = widgets.ToggleButton("
    py_code += "\n\t\tvalue=False,"
    py_code += "\n\t\tdescription='g',"
    py_code += "\n\t\tdisabled=True,"
    py_code += "\n\t\tbutton_style='danger'"
    py_code += "\n\t)"
    py_code += "\n\tled4_b_button = widgets.ToggleButton("
    py_code += "\n\t\tvalue=False,"
    py_code += "\n\t\tdescription='b',"
    py_code += "\n\t\tdisabled=True,"
    py_code += "\n\t\tbutton_style='danger'"
    py_code += "\n\t)"
    py_code += "\n\tled4_label = widgets.Label(value='RBG LED 4')"

    py_code += "\n\tled5_r_button = widgets.ToggleButton("
    py_code += "\n\t\tvalue=False,"
    py_code += "\n\t\tdescription='r',"
    py_code += "\n\t\tdisabled=True,"
    py_code += "\n\t\tbutton_style='danger'"
    py_code += "\n\t)"
    py_code += "\n\tled5_g_button = widgets.ToggleButton("
    py_code += "\n\t\tvalue=False,"
    py_code += "\n\t\tdescription='g',"
    py_code += "\n\t\tdisabled=True,"
    py_code += "\n\t\tbutton_style='danger'"
    py_code += "\n\t)"
    py_code += "\n\tled5_b_button = widgets.ToggleButton("
    py_code += "\n\t\tvalue=False,"
    py_code += "\n\t\tdescription='b',"
    py_code += "\n\t\tdisabled=True,"
    py_code += "\n\t\tbutton_style='danger'"
    py_code += "\n\t)"
    py_code += "\n\tled5_label = widgets.Label(value='RBG LED 5')"

    py_code += "\n\n\n\tdef update_button(new_value, button):"
    py_code += "\n\t\tif new_value == 1:"
    py_code += "\n\t\t\tbutton.value=True"
    py_code += "\n\t\t\tbutton.button_style='success'"
    py_code += "\n\t\telif new_value == 0:"
    py_code += "\n\t\t\tbutton.value=False"
    py_code += "\n\t\t\tbutton.button_style='danger'"

    py_code += "\n\n\tdef work():"
    py_code += "\n\t\twhile True:"
    py_code += "\n\t\t\ttime.sleep(0.1)"
    py_code += "\n\t\t\t"

    # Here we need to use the IO map.

    # self.io_configuration = {
    #     "led0":"None",
    #     "led1":"None",
    #     "led2":"None",
    #     "led3":"None",
    #     "led4_b":"None",
    #     "led4_g":"None",
    #     "led4_r":"None",
    #     "led5_b":"None",
    #     "led5_g":"None",
    #     "led5_r":"None"
    # }

    already_scanned_signals = []
    for pynq_io, comp_io in io_map.items():
        
        if comp_io == "None" or comp_io == None or comp_io[0] == '':
            # If the I/O isn't connected, we skip it. 
            # It will still appear in GUI but have no backend code for updating as no connection.
            continue

        # 1) Read Signal (if not in array)
        #   -> Add already read signals to an array
        # 2) Get Bit
        # 3) Update button
        comp_signal_name = comp_io[0]
        if comp_signal_name not in already_scanned_signals:
            py_code += f"\n\t\t\tglobal {comp_signal_name}" # Possibly adds reduces chance an inconsistent bug in Jupyter Notebook where {comp_signal_name} cannot be found
            py_code += f"\n\t\t\t{comp_signal_name}_value = {comp_signal_name}.read(0)"
            already_scanned_signals.append(comp_signal_name)
        comp_bit = 0 # Default assignment
        try:
            comp_bit = comp_io[1]   # We want everything to the right of [] in comp[1] and to drop the tailing ]
        except:
            # If there is an index out of bounds error, it means theres no [x] and therefore its a 1-bit signal.
            # comp_bit = 0
            pass
        py_code += f"\n\t\t\t{pynq_io}_new_value = get_bit({comp_bit}, {comp_signal_name}_value)"
        py_code += f"\n\t\t\tupdate_button({pynq_io}_new_value, {pynq_io}_button)"

    py_code += "\n\tthread = threading.Thread(target=work)"
    py_code += "\n\tthread.start()"

    py_code += "\n\n\thbox_layout = widgets.Layout(display='flex', justify_content='center', align_items='center', flex_flow='row')"
    
    py_code += "\n\n\thbox_led = widgets.HBox([leds_label, led3_button, led2_button, led1_button, led0_button])"
    py_code += "\n\thbox_led.layout = hbox_layout"
    
    py_code += "\n\thbox_led4 = widgets.HBox([led4_label, led4_r_button, led4_g_button, led4_b_button])"
    py_code += "\n\thbox_led4.layout = hbox_layout"

    py_code += "\n\thbox_led5 = widgets.HBox([led5_label, led5_r_button, led5_g_button, led5_b_button])"
    py_code += "\n\thbox_led5.layout = hbox_layout"
        
    py_code += "\n\n\tvbox = widgets.VBox([hbox_led, hbox_led4, hbox_led5])"
    py_code += "\n\n\treturn vbox"

    return py_code

def generate_gui_controller(compName, parsed_all_ports, location):
    py_code = ""

    current_cwd = os.getcwd().replace("\\", "/")
    svg_path = location.replace("\\", "/") + f"/PYNQBuild/generated/{compName}.svg"
     
    svg_data = ""
    try:
        with open(svg_path, 'r') as file:
            svg_data = file.read()
    except Exception:
        print("Could not find SVG file.")

    svg_data = svg_data.replace("\"", "'")
    svg_data = svg_data.replace('\n', r'\n')
    py_code += f"\nsvg_content = \"{svg_data}\""
    py_code += f"\nimage_index = 1  # Tracks next image to show so that it can be cycled"

    py_code += "\ndef get_bit(bit_position, num):"
    py_code += "\n\tif bit_position >= num.bit_length():"
    py_code += "\n\t\treturn 0"
    py_code += "\n\telse:"
    py_code += "\n\t\treturn (num >> bit_position) & 1"

    py_code += "\n\n\ndef generate_gui(svg_content):"
    py_code += "\n\t# Format SVG Data"
    py_code += "\n\tsvg_content = svg_content.split('<?xml', 1)[-1]"
    py_code += "\n\tsvg_with_tags = f'<svg style=\"display: block; margin: 50px auto; max-width: 100%; height: auto;\"{svg_content}</svg>'"

    svg_content = svg_data.split('<?xml', 1)[-1] 
    SVG = f'<svg style="display: block; margin: 50px auto; max-width: 100%; height: auto;"{svg_data}</svg>' # work in progress

    py_code += create_html_css_js(SVG, parsed_all_ports)

    return py_code

########################################################################
########## Parse all ports format from XML into useful format ##########
########################################################################
def parse_all_ports(all_ports):
    # All ports recieved as in HDLGen XML.
    #    signame = sig.getElementsByTagName("name")[0]
    #    mode = sig.getElementsByTagName("mode")[0]
    #    type = sig.getElementsByTagName("type")[0]
    #    desc = sig.getElementsByTagName("description")[0]
    # Job here is to convert into:
    # [signal_name, gpio_mode, gpio_width]
    new_array = []
    for io in all_ports:
        gpio_name = io[0]   # GPIO Name
        gpio_mode = io[1]   # GPIO Mode (in/out)
        gpio_type = io[2]   # GPIO Type (single bit/bus/array)

        if (gpio_type == "single bit"):
            gpio_width = 1
        elif (gpio_type[:3] == "bus"):
            # <type>bus(31 downto 0)</type> - Example Type Value
            substring = gpio_type[4:]           # substring = '31 downto 0)'
            words = substring.split()           # words = ['31', 'downto', '0)']
            gpio_width = int(words[0]) + 1      # eg. words[0] = 31
        elif (gpio_type[:5] == "array"):
            print("ERROR: Array mode type is not yet supported :(")
        else:
            print("ERROR: Unknown GPIO Type")
            print(gpio_type)
        new_array.append([gpio_name, gpio_mode, gpio_width])
    return new_array


def large_signal_split_names(gpio_name, gpio_width):
    pin_counter = 0
    return_array = []
    while gpio_width - pin_counter > 0:
        if gpio_width - pin_counter > 32:
            return_array.append(f"{gpio_name}_{pin_counter+31}_{pin_counter}")
            pin_counter += 32
        elif gpio_width - pin_counter <= 32:
            return_array.append(f"{gpio_name}_{gpio_width-1}_{pin_counter}")
            pin_counter += gpio_width - pin_counter        
    return return_array

def create_class_for_large_signal(gpio_name, gpio_mode, gpio_width):
    code_string = ""
    code_string += f"\n\nclass {gpio_name}_class:"

    array_of_signal = large_signal_split_names(gpio_name, gpio_width)
    code_string += "\n\tdef __init__(self):"
    code_string += f"\n\t\tpass\n"
    code_string += "\n\tdef read(self, offset):"
    code_string += f"\n\t\tblocks = {len(array_of_signal)} * [None]"
    for x in range(0, len(array_of_signal)):
        code_string += f"\n\t\tblocks[{x}] = {array_of_signal[x]}.read(offset)"
    code_string += "\n\t\tresult = 0"
    code_string += "\n\t\tfor block in blocks:"
    code_string += "\n\t\t\tresult = (result << 32) | block"
    code_string += "\n\t\treturn result\n"

    if gpio_mode == "in":
        code_string += "\n\tdef write(self, offset, value):"
        code_string += f"\n\t\tblocks = split_into_blocks(value, {len(array_of_signal)})"
        for x in range(0, len(array_of_signal)):
            code_string += f"\n\t\t{array_of_signal[x]}.write(offset, blocks[{x}])"

    # Instanciate the class
    code_string += f"\n{gpio_name} = {gpio_name}_class()"

    return code_string

def create_large_classes_from_port_map(parsed_port_map):
    code = ""
    for signal in parsed_port_map:
        gpio_name = signal[0]
        gpio_mode = signal[1]
        gpio_width = signal[2]

        if gpio_width > 32:
            code += create_class_for_large_signal(gpio_name, gpio_mode, gpio_width)

    return code

# The following functions are responsible for generating the HTML, CSS and JavaScript for the interavtive sandbox
def create_html_css_js(svg: str, parsed_all_ports: list[dict]) -> str:
    """
    This function takes an input SVG string that represents the default circuit diagram 
    for the Pynq-Soc-Builder project and generates the HTML, CSS and JavaScript code for 
    creating an interactive sandbox. The returned string contains:

    - HTML structure for rendering the sandbox
    - CSS for styling the sandbox elements.
    - JavaScript for event handling within the sandbox.

    Parameters:
    svg (str): A string representing the SVG data of the circuit diagram.
    parsed_all_ports (list[dict]): A list of all port dicts

    Returns:
    str: A string combining the HTML, CSS, and JavaScript required for the interactive sandbox.
    """

    html_css_js = f"""
    html_code = \"\"\"
        <!-- Styling the output area with a scrollable content box, a black border, and ensuring the content fits within the defined box size -->
        <style>
            .output-content-area {{
                position: relative;
                border: 1px solid black;
                overflow: scroll;
                box-sizing: border-box;
            }}

            <!-- Styling .custom-div to display content inline, align items in the center, and remove gaps between elements -->
            .custom-div{{
                display: inline-flex;
                align-items: center;
                gap: 0;
            }} 
        </style>

        <!-- Output area for interactive sandbox -->
        <div class="output-content-area" id="output-content-area">
    \"\"\"+svg_with_tags+\"\"\"
    """
    
    input_buttons = []
    output_buttons = []
    input_textboxes = []
    output_textboxes = []

    for port in parsed_all_ports:
        name, mode, width = port
        if mode == "in":
            if width == 1:
                input_buttons.append(name)
            else:
                input_textboxes.append({"name": name, "bits": width})  
        elif mode == "out":
            if width == 1: 
                output_buttons.append(name)
            else:
                output_textboxes.append(name)

    # Generate HTML for input buttons, output buttons, input textboxes, output textboxes and the set signals button
    html_css_js += '\n'.join(create_input_button(btn) for btn in input_buttons)
    html_css_js += '\n'.join(create_output_button(btn) for btn in output_buttons)
    html_css_js += '\n'.join(create_input_textbox(tb["name"]) for tb in input_textboxes)
    html_css_js += '\n'.join(create_output_textbox(tb) for tb in output_textboxes)
    html_css_js += create_set_signals_button()

    # Generate the JavaScript for event handling
    html_css_js += """
        <script>
            /**
            * Makes an HTML element draggable within a specified container.
            * @param {HTMLElement} element - The element to be made draggable.
            */
            function makeElementDraggable(element) {
                let isDragging = false,
                    offsetX = 0,
                    offsetY = 0;

                element.addEventListener('mousedown', event => {
                    isDragging = true;
                    offsetX = event.clientX - element.getBoundingClientRect().left;
                    offsetY = event.clientY - element.getBoundingClientRect().top;
                });

                document.addEventListener('mousemove', event => {
                    if (isDragging) {
                        const containerRect = document.querySelector('.output-content-area').getBoundingClientRect();
                        element.style.position = 'absolute';
                        element.style.left = `${Math.max(containerRect.left, Math.min(event.clientX - offsetX, containerRect.right - element.offsetWidth)) - containerRect.left}px`;
                        element.style.top = `${Math.max(containerRect.top, Math.min(event.clientY - offsetY, containerRect.bottom - element.offsetHeight)) - containerRect.top}px`;
                    }
                });

                document.addEventListener('mouseup', () => isDragging = false);
            }

            /**
            * Sets up a button with a click handler
            * @param {HTMLElement} button - The button element to be set up.
            * @param {Function} callback - The function to be executed when the button is clicked.
            */            
            function setupButton(button, callback) {
                let isClick = true;
                button.onmousedown = () => {
                    isClick = true;
                    setTimeout(() => isClick = false, 250); // differentiate a drag from a click
                };

                button.onclick = event => {
                    if (!isClick) {
                        event.preventDefault();
                    } else {
                        callback(button);
                    }
                };
            }

            /**
            * Toggles the state of a button between two values and updates its styling.
            * @param {HTMLElement} button - The button element whose state will be toggled.
            */            
            function toggleButtonState(button) {
                button.textContent = button.textContent === '0' ? '1' : '0';
                button.classList.toggle('mod-danger');
                button.classList.toggle('mod-success');
            }

            /**
            * Converts the input numeric string into an integer and checks if it exceeds the maximum value             
            * @param {string} numberStr - The numeric string to be evaluated, can be positive or negative and in decimal, hexadecimal, or binary format
            * @param {number} numBits - The number of bits used to represent the maximum value
            * @returns {[boolean, number|null]} - An array where the first element indicates whether the value exceeded 
            *          the maximum limit (true if exceeded, false otherwise), and the second element is either the 
            *          truncated value if it exceeded the limit, or the original value if it did not. Returns null if 
            *          an error occurs during conversion.
            */
            function checkMaxValue(numberStr, numBits) {
                function userStringToInt(numberStr){
                    let radix = 10;
                    if (numberStr.startsWith("0x")) {
                        radix = 16;
                    } else if (numberStr.startsWith("0b")) {
                        radix = 2;
                    } else if (numberStr.slice(1).startsWith("0x")) {
                        radix = 16;
                    } else if (numberStr.slice(1).startsWith("0b")) {
                        radix = 2;
                    } else{
                        return parseInt(numberStr)
                    }

                    const skipSign = (numberStr[0] === '+' || numberStr[0] === '-') ? 1 : 0;
                    const noRadixString = numberStr.slice(0, skipSign) + numberStr.slice(skipSign + 2);
                    return parseInt(noRadixString, radix);
                }

                const value = userStringToInt(numberStr)
                try {
                    let maxValue = 2**numBits - 1
                    
                    if (value > maxValue) {
                        let truncatedValue = value % (2**numBits)
                        return [true, truncatedValue];
                    } else {
                        return [false, value];
                    }
                } catch (error) {
                    return [false, null];
                }
            }
    """
    html_css_js += generate_set_signals_function(input_textboxes, input_buttons, output_textboxes, output_buttons)

    # Add the event handlers tp the widgets
    html_css_js += """
    }
            document.querySelectorAll('.input-button').forEach(button => setupButton(button, toggleButtonState));
            document.querySelectorAll('.set-signal-button').forEach(button => setupButton(button, setSignals));
            document.querySelectorAll('.draggable').forEach(makeElementDraggable);
        </script>
\"\"\"
"""

    html_css_js += "\n\n\treturn HTML(html_code)"    

    return html_css_js

def create_input_button(name: str) -> str:
    """
    Generates an HTML string for a draggable div containing a label and a button that serves as an input element.

    Args:
        name (str): The name/id of the button.

    Returns:
        str: The HTML string for the input button widget.
    """
    return f"""
    <div class="draggable" class="custom-div">
        <div class="lm-Widget p-Widget jupyter-widgets">{name}</div>
        <button class="input-button lm-Widget p-Widget jupyter-widgets jupyter-button widget-toggle-button mod-danger" style="width: 50px;" id="{name}">0</button>
    </div>
    """


def create_output_button(name: str) -> str:
    """
    Generates an HTML string for a draggable div containing a disabled output button with a label.

    Args:
        name (str): The name/id of the output button.

    Returns:
        str: The HTML string for the output button widget.
    """
    return f"""
    <div class="draggable" class="custom-div">
        <button class="lm-Widget p-Widget jupyter-widgets jupyter-button widget-toggle-button mod-danger" disabled="" title="" style="width: 50px;" id="{name}">0</button>
        <div class="lm-Widget p-Widget jupyter-widgets">{name}</div>
    </div>
    """


def create_set_signals_button() -> str:
    """
    Generates an HTML string for a draggable 'Set Signals' button.

    Returns:
        str: The HTML string for the set signals button widget.
    """
    return """
    <button class="set-signal-button draggable lm-Widget p-Widget jupyter-widgets jupyter-button widget-button mod-info" title="">Set Signals</button>
    """


def create_input_textbox(name: str) -> str:
    """
    Generates an HTML string for a draggable div containing a text input box with a label.

    Args:
        name (str): The name/id of the text input box.

    Returns:
        str: The HTML string for the input text box widget.
    """
    return f"""
    <div class="draggable" class="custom-div">
        <div class="lm-Widget p-Widget jupyter-widgets widget-label">{name}</div>
        <div class="lm-Widget p-Widget jupyter-widgets widget-inline-hbox widget-text" style="width: 200px;">
            <label class="widget-label" title="" for="{name}" style="display: none;"></label>
            <input type="text" id="{name}" placeholder="" value="0x0">
        </div>
    </div>
    """


def create_output_textbox(name: str) -> str:
    """
    Generates an HTML string for a draggable div containing a disabled output text box with a label.

    Args:
        name (str): The name/id of the text box.

    Returns:
        str: The HTML string for the output text box widget.
    """
    return f"""
    <div class="draggable" class="custom-div">
        <div class="lm-Widget p-Widget jupyter-widgets widget-inline-hbox widget-text" style="width: 200px;">
        <label class="widget-label" title="" for="{name}" style="display: none;"></label>
        <input type="text" id="{name}" disabled="" placeholder="" value="0x0"></div>
        <div class="lm-Widget p-Widget jupyter-widgets widget-label">{name}</div>
    </div>
    """

def generate_set_signals_function(input_textboxes: list[dict], input_buttons: list[str], output_textboxes: list[str], output_buttons: list[str]) -> str:
    """
    Generates JavaScript code for the setSignals() event handler

    Args:
        input_textboxes (list[dict]): A list of dictionaries representing input textboxes,
                                       each containing 'name' (str) and 'bits' (int).
        input_buttons (list[str]): A list of strings representing the names of input buttons.
        output_textboxes (list[str]): A list of strings representing the names of output textboxes.
        output_buttons (list[str]): A list of strings representing the names of output buttons.

    Returns:
        str: A string containing the generated JavaScript function to set signals.
    
    The generated function retrieves values from input textboxes and buttons, checks for 
    maximum values, writes values to a backend, reads output values, and updates 
    the corresponding HTML elements.
    """    
    textbox_names = [item["name"] for item in input_textboxes]
    textbox_names_str = ', '.join([f"'{name}'" for name in textbox_names])
    value_names_str = ', '.join([f"{name}_value" for name in textbox_names])
    
    truncated_checks = []
    for item in input_textboxes:
        name = item["name"]
        bits = item["bits"]
        truncated_check = f"""
                        let [{name}_truncated, new_{name}Value] = checkMaxValue({name}_value, {bits});
            {name}_value = new_{name}Value;
            if ({name}_truncated) {{
                console.log(`{name} value provided is > {bits} bits, input has been truncated to: 0x${{{name}_value.toString(16)}}`);
            }}
        """
        truncated_checks.append(truncated_check.strip())
    
    truncated_checks_str = "\n\n".join(truncated_checks)
    button_names_str = ', '.join([f"'{name}'" for name in input_buttons])
    button_value_names_str = ', '.join([f"{name}_value" for name in input_buttons])
    write_statements = []
    if(input_textboxes):
        for item in input_textboxes:
            write_statements.append(f"                {item['name']}.write(0, ${{{item['name']}_value}})")
    
    if(input_buttons):
        for name in input_buttons:
            write_statements.append(f"                {name}.write(0, ${{{name}_value}})")
    write_statements_str = "\n".join(write_statements)
    output_reads = []
    if(output_textboxes):
        for name in output_textboxes:
            output_reads.append(f"                {name}_value = {name}.read(0)")
    
    if(output_buttons):
        for name in output_buttons:
            output_reads.append(f"                {name}_value = {name}.read(0)")
    output_reads_str = "\n".join(output_reads)
    print_statements = []
    if(output_textboxes):
        for name in output_textboxes:
            print_statements.append(f"{name}:{{{name}_value}}")
    
    if(output_buttons):
        for name in output_buttons:
            print_statements.append(f"{name}:{{{name}_value}}")
    
    print_statement_str = ",".join(print_statements)
    generated_code = """function setSignals(){"""
    if(input_textboxes):
        generated_code += f"""
            const textbox_values = [{textbox_names_str}].map(id => document.getElementById(id).value);
            let [{value_names_str}] = textbox_values;
    {truncated_checks_str}
"""
    if(input_buttons):
        generated_code += f"""
            const values = [{button_names_str}].map(id => document.getElementById(id).textContent === '1' ? 1 : 0);
            const [{button_value_names_str}] = values;
"""    
    
    generated_code += f"""
            IPython.notebook.kernel.execute(`
    {write_statements_str}
            time.sleep(0.00000002)
    {output_reads_str}
            print(f"{print_statement_str}")
            `, {{
                iopub: {{
                    output: data => {{
                        let output = data.content.text.trim().split(",")
                        output.forEach(output => {{
                            output  = output.split(":")
                            const element = document.getElementById(output[0])
                            const value = parseInt(output[1], 10)
                            if (element.tagName === "INPUT") {{
                                element.value = "0x" + value.toString(16)
                            }} else if (element.tagName === ("BUTTON")){{
                                element.textContent = value === 1 ? '1' : '0';
                                element.classList.remove('mod-success', 'mod-danger');
                                element.classList.add(value === 1 ? 'mod-success' : 'mod-danger');  
                            }}
                        }})
                    }}
                }}
            }});
"""        
                
    return generated_code.strip()