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
    py_file_contents += "\nfrom IPython.display import display, HTML, Javascript"
    py_file_contents += "\nfrom pynq import Overlay, PL"
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
    

    if io_map:
        # If any INPUT board I/O are used, switches, buttons and the likes
        # TESTPLAN is not possible as inputs cannot be asserted by the processing system AND an input IO.
        # Hence we check, and if necessary, deassert use_testplan and add explanatory text if a testplan was expected.
        input_io = ["sw0", "sw1", "btn0", "btn1", "btn2", "btn3"]
        io_cfg_blocked_testplan_generation = False
        for pynq_io, comp_io in io_map.items():
            if (comp_io == "None" or comp_io == None):
                continue
            if (pynq_io in input_io):
                print(f"Detected that {input_io} is connected to the following PYNQ board INPUT device - {pynq_io} \nWARNING: Cannot generate testplan in Jupyter Notebook as result (Cannot have two drivers)")
                if use_testplan:
                    use_testplan = False
                    print("Detected that 'use_testplan' was asserted - Deasserting do to incompatibility with current configuration")
                    io_cfg_blocked_testplan_generation = True


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

    py_file_contents += """
    
# Kill unnecessary threads
threads = threading.enumerate()
for thread in threads:
    if(thread.name in ["work"]):
        thread.join()"""
    # Python Set Up Code Block
    # Import Overlay
    py_file_contents += "\n\n# Import Overlay"
    py_file_contents += "\nPL.reset()"
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
    py_file_contents += "\ncurrentIndex = 0\n" + create_large_classes_from_port_map(parsed_all_ports)

    py_file_contents += "\n# Split Number into Blocks Function"
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

        py_file_contents += f"\n{generate_io_visuals(io_map)}"

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
 

        py_file_contents += generate_gui_controller(compName, parsed_all_ports, location, clock_enabled, io_map)

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

    elif io_cfg_blocked_testplan_generation:
        # In this instance, a testplan was requested but could not be generated due to IO config. Need to add markdown to communicate this to the user.
        markdown_cell_content = "#### Could not generate automated testplan as model input controlled by PYNQ Input Device\n\n"
        for pynq_io, comp_io in io_map.items():
            if pynq_io in input_io:
                markdown_cell_content += f"Cannot generate testplan as signal {comp_io} is controlled by {pynq_io}\n\n"
        markdown_cell_content += "\nWhen a signal is controlled by an input mentioned above, it cannot be controlled by the PYNQ's processing system to run tests.\nThis has no impact on any other functionality in this notebook."
        markdown_cell = nbf.v4.new_markdown_cell(markdown_cell_content)
        notebook.cells.append(markdown_cell)

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
    py_code = """
def generate_io_gui():
    def create_led_button(description):
        return widgets.ToggleButton(
            value=False,
            description=description,
            disabled=True,
            button_style='danger'
        )

    def read_and_update(input_device, bit_index, button):
        value = input_device.read(0)
        new_value = get_bit(bit_index, value)
        button.button_style = 'success' if new_value == 1 else 'danger'
    
    led_buttons = [create_led_button(str(i)) for i in range(4)]
    rgb_led4_buttons = {f"led4{i}": create_led_button(i) for i in 'rgb'}
    rgb_led5_buttons = {f"led5{i}": create_led_button(i) for i in 'rgb'}
    switch_buttons = [create_led_button(f"{i}") for i in range(2)]
    button_buttons = [create_led_button(f"{i}") for i in range(4)]

    # Labels
    leds_label = widgets.Label(value='LEDs')
    led4_label = widgets.Label(value='RGB LED 4')
    led5_label = widgets.Label(value='RGB LED 5')
    swlabel = widgets.Label(value='Switches')
    btnlabel = widgets.Label(value='Buttons')

    def work():
        while True:
            try:
                time.sleep(0.1)
    """

    already_scanned_signals = []
    for pynq_io, comp_io in io_map.items():
        if not comp_io or comp_io == "None":
            # If the I/O isn't connected, we skip it. 
            # It will still appear in GUI but have no backend code for updating as no connection.
            continue

        # 1) Read Signal (if not in array)
        #   -> Add already read signals to an array
        # 2) Get Bit
        # 3) Update button
        comp_signal_name = comp_io[0]
        comp_bit = comp_io[1] if len(comp_io) > 1 else 0

        if comp_signal_name not in already_scanned_signals:
            already_scanned_signals.append(comp_signal_name)

        # Determine widget type and index for each signal
        if "led4" in pynq_io:
            button_ref = f"rgb_led4_buttons.get(\"{pynq_io}\")"
        elif "led5" in pynq_io:
            button_ref = f"rgb_led5_buttons.get(\"{pynq_io}\")"
        elif "led" in pynq_io:
            button_ref = f"led_buttons[{pynq_io[-1]}]"
        elif "sw" in pynq_io:
            button_ref = f"switch_buttons[{pynq_io[-1]}]"
        elif "btn" in pynq_io:
            button_ref = f"button_buttons[{pynq_io[-1]}]"
            
        py_code += f"""
                read_and_update({comp_signal_name}, {comp_bit}, {button_ref})"""

    py_code += """
            except NameError:
                break  # Exit if variables are undefined after notebook re-run

    thread = threading.Thread(target=work, name="work", daemon=True)
    thread.start()

    hbox_layout = widgets.Layout(display='flex', justify_content='center', align_items='center', flex_flow='row')
    hbox_led = widgets.HBox([leds_label] + list(reversed(led_buttons)), layout=hbox_layout)
    hbox_led4 = widgets.HBox([led4_label] + list(rgb_led4_buttons.values()), layout=hbox_layout)
    hbox_led5 = widgets.HBox([led5_label] + list(rgb_led5_buttons.values()), layout=hbox_layout)
    hbox_btn = widgets.HBox([btnlabel] + list(reversed(button_buttons)), layout=hbox_layout)
    hbox_sw = widgets.HBox([swlabel] + list(reversed(switch_buttons)), layout=hbox_layout)

    vbox = widgets.VBox([hbox_led, hbox_led4, hbox_led5, hbox_btn, hbox_sw])

    return vbox
    """

    return py_code

def generate_gui_controller(compName, parsed_all_ports, location, clock_enabled, io_map):

    py_code = ""

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

    py_code += create_html_css_js(parsed_all_ports, clock_enabled, io_map)

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

# This function takes an input SVG string that represents the default circuit diagram for the Pynq-Soc-Builder project and generates the HTML, CSS and JavaScript code for creating an interactive sandbox
def create_html_css_js(parsed_all_ports: list[dict], clock_enabled: bool, io_map: dict) -> str:
    html_css_js = """"""

    controlled_by_board_inputs = []
    board_input_io = ["sw0", "sw1", "btn0", "btn1", "btn2", "btn3"]
    if io_map:
        for board_io, signal in io_map.items():
            # Key is the IO, Value is the port (signal_name, pin_index)
            if board_io in board_input_io:
                controlled_by_board_inputs.append(signal[0])
    
    input_buttons, output_buttons, input_textboxes, output_textboxes = [], [], [], []

    for port in parsed_all_ports:
        name, mode, width = port
        if mode == "in":
            if width == 1: input_buttons.append({"name": name, "disabled": name in controlled_by_board_inputs})
            else: input_textboxes.append({"name": name, "bits": width})  
        elif mode == "out":
            if width == 1: output_buttons.append(name)
            else: output_textboxes.append(name)

    html_css_js += (
    (f"\n{input_button_generation()}" if input_buttons else '') +
    (f"\n{input_textbox_generation()}" if input_textboxes else '') +
    (f"\n{output_button_generation()}" if output_buttons else '') +
    (f"\n{output_textbox_generation()}" if output_textboxes else '')
)

    html_css_js += generate_get_image_files_function()

    html_css_js += "\n\ndef generate_gui(svg_content):"
    
    html_css_js += """
    image_list = get_image_files()
    image_list_js = '["' + '", "'.join([img.replace('"', '\\\\"') for img in image_list]) + '"]'

    html_code = \"\"\""""

    html_css_js += generate_css() 
    html_css_js += generate_image_scale_selector()
    html_css_js += generate_output_area()

    # Generate HTML for input buttons, output buttons, input textboxes, output textboxes and the set signals button
    html_css_js += '\n\t' + '\t'.join([f'html_code += create_input_button("{input_button["name"]}", {input_button["name"]}.read(0), {input_button["disabled"]})\n' for input_button in input_buttons]) if input_buttons else ""
    html_css_js += '\n\t' + '\t'.join([f'html_code += create_output_button("{output_button}", {output_button}.read(0))\n' for output_button in output_buttons]) if output_buttons else ""
    html_css_js += '\n\t' + '\t'.join([f'html_code += create_input_textbox("{input_textbox["name"]}", {input_textbox["bits"]})\n' for input_textbox in input_textboxes]) if input_textboxes else ""
    html_css_js += '\n\t' + '\t'.join([f'html_code += create_output_textbox("{output_textbox}")\n' for output_textbox in output_textboxes]) if output_textboxes else ""

    html_css_js += generate_change_image_button()

    # Generate the JavaScript for event handling
    html_css_js += """
    html_code += \"\"\"
<div id="error-message" class="error-message"></div> 
<script type="text/javascript">
"""
    disabled_buttons = [btn['name'] for btn in input_buttons if btn['disabled']]
    buttons = output_buttons + disabled_buttons

    html_css_js += generate_make_element_draggable_function()
    html_css_js += generate_check_max_value_function()
    html_css_js += generate_set_signals_or_run_clock_period_function(output_textboxes, buttons)

    # Add the event handlers to the widgets
    html_css_js += generate_background_image_functions()

    html_css_js += """
    html_code += \"\"\""""

    html_css_js += f"""
    {create_input_button_event_handler() if input_buttons else ''}
    {create_input_textbox_event_handler() if input_textboxes else ''}
    document.querySelectorAll('.set-signal-button').forEach(button => button.onclick = () => {{setSignals()}});
    """

    html_css_js += """
        document.querySelectorAll('.draggable').forEach(makeElementDraggable);
</script>
\"\"\"

    return HTML(html_code)

display(Javascript(\"\"\"
        for (let i = 0; i < 10000; i++) {
            clearInterval(i);
        }
    \"\"\"))
"""

    return html_css_js

# Generates a JS string for the input button event handler
def create_input_button_event_handler() -> str:
    return """
function inputButtonEventHandler(id) {
    const button = document.getElementById(`${id}`)
    let isClick = true;
    button.onmousedown = () => {
        isClick = true;
        setTimeout(() => isClick = false, 250); // differentiate a drag from a click
    };

    button.onclick = event => {
        if (!isClick) {
            event.preventDefault();
        } else {
            button.textContent = button.textContent === '0' ? '1' : '0';
            const value = button.textContent === '1' ? 1 : 0;

            IPython.notebook.kernel.execute(`
                ${id}.write(0, ${value})
            `);

            button.classList.toggle('mod-danger');
            button.classList.toggle('mod-success');
        }
    };
}

document.querySelectorAll('.input-button-enabled').forEach(button =>inputButtonEventHandler(button.id));

"""
# Generates the HTML string to dynamically generate the "Change Image" button
def generate_change_image_button() -> str:
    return """
    if len(image_list) > 1:
        html_code += \"\"\"
<div id="change-image-button-wrapper" style="display: flex; justify-content: center;">
    <button id="changeImageButton" class="lm-Widget p-Widget jupyter-widgets jupyter-button widget-button mod-warning" title="Click me">
        <i class="fa fa-picture-o"></i>
        Change Image
    </button>
</div>
\"\"\"
    """

# Generates a JS string for the input textbox event handler
def create_input_textbox_event_handler() -> str:
    return """
function inputTextboxEventHandler(name, bits){
    let errors = [];
    const errorArea = document.getElementById("error-message");
    errorArea.innerHTML = "";

    let value = document.getElementById(`${name}`).value;
    let [truncated, new_value] = checkMaxValue(value, 4);
    value = new_value;

    if (truncated) {
        errors.push(`${name} value provided is > ${bits} bits, input has been truncated to: 0x${value.toString(16)}`);
    }

    if(errors.length > 0){
        errors = errors.map(error => `<div style='color: var(--jp-error-color1);'>${error}</div>`);
        const errorMessages = errors.join("\\\\n")
        errorArea.innerHTML = errorMessages
    }

    IPython.notebook.kernel.execute(`${name}.write(0, ${value})`);
}

document.querySelectorAll('.input-textbox').forEach(textbox => textbox.onchange = () => {{inputTextboxEventHandler(textbox.id, textbox.dataset.bits)}});
"""

# Generates a HTML string for a draggable div containing a disabled output text box with a label
def create_output_textbox(name: str) -> str:
    return f"""
    <div class="draggable" style="display: inline-flex;align-items: center;gap: 0;">
        <div class="lm-Widget p-Widget jupyter-widgets widget-inline-hbox widget-text" style="width: 200px;">
        <label class="widget-label" title="" for="{name}" style="display: none;"></label>
        <input type="text" id="{name}" disabled="" placeholder="" value="0x0"/></div>
        <div class="lm-Widget p-Widget jupyter-widgets widget-label" onmousedown="this.style.cursor = 'grabbing';" onmouseover="this.style.cursor = 'grab';">{name}</div>
    </div>
    """

# Generates an HTML string for an image scale selector using a loop
def generate_image_scale_selector() -> str:
    options = '\n\t\t'.join(
        f'\t\t<option value="{i}" data-value="{i}"{" selected" if i == 1 else ""}>{i}x</option>'
        for i in [x * 0.25 for x in range(1, 17)]
    )

    return f"""
    <div id="image-size-selector-wrapper" class="output_subarea jupyter-widgets-view" style="display: flex; justify-content: center;" dir="auto">
        <div class="lm-Widget p-Widget jupyter-widgets widget-inline-hbox widget-dropdown">
            <label class="widget-label" title="Image Size:" for="image-size-selector">Image Size:</label>
            <select id="image-size-selector" onchange="changeImageSize()">
{options}
            </select>
        </div>
    </div>
    """

def generate_get_image_files_function(): 
    return """
    
def get_image_files():
    global svg_content
    image_extensions = ['.png', '.jpg', '.jpeg', '.svg']  # Add more if needed
    files = os.listdir()
    image_tags = []
    
    # add the initial svg file
    svg_content = svg_content.split('<?xml', 1)[-1]
    svg_content = svg_content.replace("\\n", "").replace("</script>", "</scr"+"ipt>")
    formatted_svg_content = f'<svg style="display: block; margin: 50px auto; max-width: 100%; height: auto; transform: scale(1); transform-origin: center;"{svg_content}</svg>'
    image_tags.append(formatted_svg_content)
    
    for f in files:
        ext = os.path.splitext(f)[1].lower()
        if ext == '.svg':
            with open(f, 'r') as svg_file:
                new_svg_content = svg_file.read()
                new_svg_content = new_svg_content.split('<?xml', 1)[-1]
                new_svg_content = new_svg_content.replace("\\n", "").replace("</script>", "</scr"+"ipt>")
                image_tags.append(f'<svg style="display: block; margin: 50px auto; max-width: 100%; height: auto; transform: scale(1); transform-origin: center;"{new_svg_content}</svg>')
        elif ext in image_extensions:
            image_tags.append(f'<img src="{f}" style="display: block; margin: 50px auto; max-width: 100%; height: auto; transform: scale(1); transform-origin: center;"">')
    
    return image_tags
"""

def generate_make_element_draggable_function():
    return"""
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
    }"""

def generate_check_max_value_function():
    return """
    function checkMaxValue(numberStr, numBits) {
        function userStringToInt(numberStr) {
            let radix = 10;
            if (numberStr.startsWith("0x")) {
                radix = 16;
            } else if (numberStr.startsWith("0b")) {
                radix = 2;
            } else if (numberStr.slice(1).startsWith("0x")) {
                radix = 16;
            } else if (numberStr.slice(1).startsWith("0b")) {
                radix = 2;
            } else {
                return parseInt(numberStr)
            }

            const skipSign = (numberStr[0] === '+' || numberStr[0] === '-') ? 1 : 0;
            const noRadixString = numberStr.slice(0, skipSign) + numberStr.slice(skipSign + 2);
            return parseInt(noRadixString, radix);
        }

        const value = userStringToInt(numberStr)
        try {
            let maxValue = 2 ** numBits - 1

            if (value > maxValue) {
                let truncatedValue = value % (2 ** numBits)
                return [true, truncatedValue];
            } else {
                return [false, value];
            }
        } catch (error) {
            return [false, null];
        }
    }
    """

def generate_background_image_functions():
    return """
    function changeImageSize() {
        const scaleSelector = document.getElementById('image-size-selector');
        currentScale = parseFloat(scaleSelector.value);
        const imageWrapper = document.getElementById('image-wrapper');
        imageWrapper.style.transform = `scale(${currentScale})`;
    }

    function changeImage() {
        let currentIndex = 0;
        const images = \"\"\" + image_list_js + \"\"\";
        IPython.notebook.kernel.execute(`
        currentIndex = (currentIndex + 1) % \"\"\" + str(len(image_list)) + \"\"\"
        print(currentIndex)
        `, {
            iopub: {
                output: data => {
                    currentIndex = parseInt(data.content.text, 10);
                    document.getElementById('image-wrapper').innerHTML = images[currentIndex];
                }
            }
        })
    }
\"\"\"
    # Dynamically add the "Change Image" button if image_list has more than 1 image
    if len(image_list) > 1:
        html_code += \"\"\"
    document.getElementById('changeImageButton').addEventListener('click', changeImage);
\"\"\"
    """

def generate_css():
    return     """
<!-- Styling the output area with a scrollable content box, a black border, and ensuring the content fits within the defined box size -->
<style>
    .output-content-area {
        position: relative;
        border: 1px solid black;
        overflow: scroll;
        box-sizing: border-box;
    }
</style>
"""

def generate_output_area():
    return """
    <!-- Output area for interactive sandbox -->
<div class="output-content-area" id="output-content-area">
    <div id="image-wrapper">
    \"\"\"+image_list[0]+\"\"\"
    </div>\"\"\"
    """

# Generates JavaScript code for the setSignals() event handler
def generate_set_signals_or_run_clock_period_function(output_textboxes: list[str], output_buttons: list[str]) -> str:          
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
    generated_code = f"""\nfunction setSignals(){{
            IPython.notebook.kernel.execute(`
{output_reads_str}
                print(f"{print_statement_str}")
            `, {{
                iopub: {{
                    output: data => {{
                        if (data.content.text && data.content.text.trim() !== '') {{

                            let output = data.content.text.trim().split(",")
                            output.forEach(output => {{
                                output = output.split(":")
                                const element = document.getElementById(output[0])
                                const value = parseInt(output[1], 10)
                                if (element.tagName === "INPUT") {{
                                    element.value = "0x" + value.toString(16)
                                }} else if (element.tagName === ("BUTTON")) {{
                                    element.textContent = value === 1 ? '1' : '0';
                                    element.classList.remove('mod-success', 'mod-danger');
                                    element.classList.add(value === 1 ? 'mod-success' : 'mod-danger');
                                }}
                            }})
                        }}
                    }}
                }}
            }});
        }}

    setInterval(setSignals, 100);
"""        
                
    return generated_code.strip()

def input_button_generation():
    return """def create_input_button(button_id, read_value, is_disabled):
    status_class = "mod-success" if str(read_value) == "1" else "mod-danger"
    disabled_attr = "disabled" if is_disabled else ""
    
    return \"\"\"
    <div class="draggable" style="display: inline-flex; align-items: center; gap: 0;">
        <div class="lm-Widget p-Widget jupyter-widgets"
             onmousedown="this.style.cursor = 'grabbing';"
             onmouseover="this.style.cursor = 'grab';">
            {id}
        </div>
        <button class="input-button-enabled lm-Widget p-Widget jupyter-widgets jupyter-button widget-toggle-button {status_class}" 
                style="width: 50px;" 
                id="{id}"
                {disabled}>{button_text}</button>
    </div>
    \"\"\".format(
        status_class=status_class,
        id=button_id,
        disabled=disabled_attr,
        button_text=str(read_value)
    )"""

def input_textbox_generation():
        return """def create_input_textbox(textbox_id, data_bits):
    return \"\"\"
    <div class="draggable" style="display: inline-flex; align-items: center; gap: 0;">
        <div class="lm-Widget p-Widget jupyter-widgets widget-label"
             onmousedown="this.style.cursor = 'grabbing';"
             onmouseover="this.style.cursor = 'grab';">
            {id}
        </div>
        <div class="lm-Widget p-Widget jupyter-widgets widget-inline-hbox widget-text" style="width: 200px;">
            <label class="widget-label" title="" for="{id}" style="display: none;"></label>
            <input class="input-textbox" type="text" id="{id}" data-bits="{bits}" placeholder="" value="0x0"/>
        </div>
    </div>
    \"\"\".format(
        id=textbox_id,
        bits=data_bits,
    )"""
        
def output_button_generation():
    return """def create_output_button(button_id, read_value):
    status_class = "mod-success" if str(read_value) == "1" else "mod-danger"
    
    return \"\"\"
    <div class="draggable" style="display: inline-flex; align-items: center; gap: 0;">
        <button class="lm-Widget p-Widget jupyter-widgets jupyter-button widget-toggle-button {status_class}" 
                disabled title="" style="width: 50px;" id="{id}">{button_text}</button>
        <div class="lm-Widget p-Widget jupyter-widgets"
             onmousedown="this.style.cursor = 'grabbing';"
             onmouseover="this.style.cursor = 'grab';">
            {id}
        </div>
    </div>
    \"\"\".format(
        status_class=status_class,
        id=button_id,
        button_text=str(read_value),
    )"""

def output_textbox_generation():
    return """def create_output_textbox(textbox_id):
    return \"\"\"
    <div class="draggable" style="display: inline-flex; align-items: center; gap: 0;">
        <div class="lm-Widget p-Widget jupyter-widgets widget-inline-hbox widget-text" style="width: 200px;">
            <label class="widget-label" title="" for="{id}" style="display: none;"></label>
            <input type="text" id="{id}" disabled placeholder="" value="0x0"/>
        </div>
        <div class="lm-Widget p-Widget jupyter-widgets widget-label" 
             onmousedown="this.style.cursor = 'grabbing';" 
             onmouseover="this.style.cursor = 'grab';">
            {id}
        </div>
    </div>
    \"\"\".format(
        id=textbox_id,
    )"""