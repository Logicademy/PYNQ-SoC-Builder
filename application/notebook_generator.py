import nbformat as nbf
import xml.dom.minidom
import csv
from io import StringIO
import html
import os
import application.xml_manager as xmlman

# Function to generate JNB, takes HDLGen file path and notebook name as parameters
def create_jnb(path_to_hdlgen_file, output_filename=None, generic=False, io_map=None):
    
    # io_map == True is indicator to read from XML file
    # io_map == None means do not configure for IO
    # io_map == io_map means an io_map dictionary was passed and it should be used.
    if io_map == True:
        # This means we need to read from file
        io_map = xmlman.Xml_Manager(path_to_hdlgen_file).read_io_config()

    py_file_contents = ""   # This file is used to store the accompanying Python code for GUI controller, test APIs etc.

    # Py File Imports
    py_file_contents += "import ipywidgets as widgets"
    py_file_contents += "\nfrom IPython.display import SVG, display"
    py_file_contents += "\nfrom ipywidgets import GridspecLayout, Output, HBox"
    py_file_contents += "\nfrom ipywidgets import Button, Layout, jslink, IntText, IntSlider"
    py_file_contents += "\nfrom pynq import Overlay"
    py_file_contents += "\nimport pandas as pd"
    py_file_contents += "\nimport time"
    py_file_contents += "\nimport os"
    py_file_contents += "\nimport threading"

    # Open HDLGen xml and get root node.
    hdlgen = xml.dom.minidom.parse(path_to_hdlgen_file)
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

    parsed_all_ports = parse_all_ports(all_ports)

    # Retrieve TB Data from HDLGen
    testbench = root.getElementsByTagName("testbench")[0]
    try:
        TBNote = testbench.getElementsByTagName("TBNote")[0]
        TBNoteData = TBNote.firstChild.data
    except Exception:
        print("No TBNoteData - asserting generic generation")
        generic = True
    
    
    # Test bench parsing code
    if not generic:
        # Parsing TB data into variables
        # Convert HTML entities into their coorresponding characters
        decoded_string = html.unescape(TBNoteData)
        # Replace &#x9; with actual tabs
        tsv_string = decoded_string.replace("&#x9;", "\t")
        # Read TSV string into a CSV reader
        tsv_reader = csv.reader(StringIO(tsv_string), delimiter='\t')
        
        tsv_data_filtered = []
        for row in tsv_reader:
            if row == []:
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
    
    for io in all_ports:
        gpio_name = io[0]   # GPIO Name
        gpio_mode = io[1]   # GPIO Mode (in/out)
        gpio_type = io[2]   # GPIO Type (single bit/bus/array)
        # Parse GPIO Width 
        if (gpio_type == "single bit"):
                gpio_width = 1
        elif (gpio_type[:3] == "bus"):
            # <type>bus(31 downto 0)</type>     ## Example Type Value
            substring = gpio_type[4:]           # substring = '31 downto 0)'
            words = substring.split()           # words = ['31', 'downto', '0)']
            gpio_width = int(words[0]) + 1           # words[0] = 31
        elif (gpio_type[:5] == "array"):
            print("ERROR: Array mode type is not yet supported :(")
        else:
            print("ERROR: Unknown GPIO Type")
            print(gpio_type)

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
            markdown_cell_contents += f"\n| {pynq_io} | {comp_io} |"

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
        py_file_contents += generate_gui_controller(compName, parsed_all_ports, location)

    ##### Break here if only dealing with skeleton code.
    # Possible To-do here is a "example" cell showing how to use signals

    if not generic:

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

        code_cell_contents += "\n\n# Split Number into Blocks"
        code_cell_contents += "\ndef split_into_blocks(number, num_blocks):"
        code_cell_contents += "\n\tblock_size = 32"
        code_cell_contents += "\n\tmask = (1 << block_size) - 1  # Create a mask with 32 bits set to 1"
        code_cell_contents += "\n\tblocks = []"
        code_cell_contents += "\n\tfor i in range(0, 32*num_blocks, block_size):"
        code_cell_contents += "\n\t\tblock = (number & mask)"
        code_cell_contents += "\n\t\tblocks.append(block)"
        code_cell_contents += "\n\t\tnumber >>= block_size"
        code_cell_contents += "\n\treturn blocks"


        #### END OF PYTHON TEST CASE SET UP CODE BLOCK - SENDING TO PYTHON FILE ####
        py_file_contents += "\n\n# Test Case Set Up Code\n\n" + code_cell_contents

        py_file_contents += "\n" + create_large_classes_from_port_map(parsed_all_ports)
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

    output_file = f'{output_filename}\{name}.ipynb'
    # if output_filename is not None:
    #     output_file = output_filename

    with open(output_file, 'w') as f:
        nbf.write(notebook, f)
        
    print(f"Notebook Generated at: {output_file}")

    output_py_file = f'{output_filename}\{name}.py'
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
        
        if comp_io == "None" or None:
            # If the I/O isn't connected, we skip it. 
            # It will still appear in GUI but have no backend code for updating as no connection.
            continue

        # 1) Read Signal (if not in array)
        #   -> Add already read signals to an array
        # 2) Get Bit
        # 3) Update button
        comp_signal_name = comp_io.split('[')[0]
        if comp_signal_name not in already_scanned_signals:
            py_code += f"\n\t\t\tglobal {comp_signal_name}" # Possibly adds reduces chance an inconsistent bug in Jupyter Notebook where {comp_signal_name} cannot be found
            py_code += f"\n\t\t\t{comp_signal_name}_value = {comp_signal_name}.read(0)"
            already_scanned_signals.append(comp_signal_name)
        comp_bit = 0 # Default assignment
        try:
            comp_bit = comp_io.split('[')[1][:-1]   # We want everything to the right of [] in comp[1] and to drop the tailing ]
        except:
            # If there is an index out of bounds error, it means theres no [x] and therefore its a 1-bit signal.
            # comp_bit = 0
            pass
        py_code += f"\n\t\t\t{pynq_io}_new_value = get_bit({comp_bit}, {comp_signal_name}_value)"
        py_code += f"\n\t\t\tupdate_button({pynq_io}_new_value, {pynq_io}_button)"

    py_code += "\n\tthread = threading.Thread(target=work)"
    py_code += "\n\tthread.start()"

    py_code += "\n\n\thbox_layout = widgets.Layout(display='flex', justify_content='center', align_items='center', flex_flow='row')"
    
    py_code += "\n\n\thbox_led = widgets.HBox([leds_label, led0_button, led1_button, led2_button, led3_button])"
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

    py_code += f"\n\n# Find images in the current directory"
    py_code += f"\ndef find_images():"
    py_code += f"\n\tcurr_dir = os.getcwd()"
    py_code += f"\n\tlist_dir = os.listdir(curr_dir)"
    py_code += f"\n\timg_files = [file for file in list_dir if file.endswith('.png') or file.endswith('.svg') or file.endswith('.jpg')]"
    py_code += f"\n\treturn img_files"

    py_code += "\ndef get_bit(bit_position, num):"
    py_code += "\n\tif bit_position >= num.bit_length():"
    py_code += "\n\t\treturn 0"
    py_code += "\n\telse:"
    py_code += "\n\t\treturn (num >> bit_position) & 1"

    py_code += "\n\n\ndef generate_gui(svg_content):"
    py_code += "\n\timages_found = find_images()"

    py_code += "\n\t# Format SVG Data"
    py_code += "\n\tsvg_content = svg_content.split('<?xml', 1)[-1]"
    py_code += "\n\tsvg_with_tags = f'<svg>{svg_content}</svg>'"
    py_code += "\n\n\t# Create Widget Object for SVG"
    py_code += "\n\toutput_svg = Output()"
    py_code += "\n\twith output_svg:"
    py_code += "\n\t\tdisplay(SVG(data=svg_with_tags))"

    input_setup = ""
    output_setup = ""
    num_input = 0
    num_output = 0

    py_code += "\n\t# Update Button State Function"
    py_code += "\n\tdef update_button_state(change, label, button):"
    py_code += "\n\t\tif change['new']:"
    py_code += "\n\t\t\tbutton.value = True"
    py_code += "\n\t\t\tbutton.description = '1'"
    py_code += "\n\t\t\tbutton.button_style = 'success'  # Green color"
    py_code += "\n\t\telse:"
    py_code += "\n\t\t\tbutton.value = False"
    py_code += "\n\t\t\tbutton.description = '0'"
    py_code += "\n\t\t\tbutton.button_style = 'danger'   # Red color"

    py_code += "\n\n\t# Change Image Button Handler"
    py_code += "\n\tdef update_image(arg, grid):"
    py_code += "\n\t\tglobal image_index # Use global var image_index"
    py_code += "\n\t\tglobal svg_content # Use global var svg_content"
    py_code += "\n\n\t\t# First remove the current image"
    py_code += "\n\t\tgrid[:-1,1].close()"
    py_code += "\n\t\t# If the image_index remainder is 0, we want to set default SVG"
    py_code += "\n\t\tif image_index % (len(images_found)+1) == 0:"
    py_code += "\n\t\t\t# Set SVG"
    py_code += "\n\t\t\tsvg_content = svg_content.split('<?xml', 1)[-1]"
    py_code += "\n\t\t\tsvg_with_tags = f'<svg>{svg_content}</svg>'"
    py_code += "\n\t\t\t# Create Widget Object for SVG"
    py_code += "\n\t\t\toutput_svg = Output()"
    py_code += "\n\t\t\twith output_svg:"
    py_code += "\n\t\t\t\tdisplay(SVG(data=svg_with_tags))"
    py_code += "\n\t\t\t# Set new widget"
    py_code += "\n\t\t\tgrid[:-1,1] = output_svg"
    py_code += "\n\t\telse:"
    py_code += "\n\t\t\t# We are dealing with a new image"
    py_code += "\n\t\t\t# Normalise index to be between 0 and number of images found - 1"
    py_code += "\n\t\t\tindex = (image_index-1) % len(images_found)"
    py_code += "\n\t\t\timage_filename = images_found[index]"
    py_code += "\n\t\t\t# Deal with SVG file"
    py_code += "\n\t\t\tif image_filename[-3:] == 'svg':"
    py_code += "\n\t\t\t\t#Read the SVG content from the file"
    py_code += "\n\t\t\t\twith open(image_filename, 'r') as file:"
    py_code += "\n\t\t\t\t\tsvg_content_temp = file.read()"
    py_code += "\n\t\t\t\tsvg_content_temp = svg_content_temp.split('<?xml', 1)[-1]"
    py_code += "\n\t\t\t\tsvg_content_temp_with_tags = f'<svg>{svg_content_temp}</svg>'"
    py_code += "\n\t\t\t\tuser_svg = Output()"
    py_code += "\n\t\t\t\twith user_svg:"
    py_code += "\n\t\t\t\t\tdisplay(SVG(data=svg_content_temp_with_tags))"
    py_code += "\n\t\t\t\tgrid[:-1,1] = user_svg"
    py_code += "\n\t\t\t# Dealing with JPG or PNG"
    py_code += "\n\t\t\telse:"
    py_code += "\n\t\t\t\tfile = open(image_filename, 'rb')"
    py_code += "\n\t\t\t\timage = file.read()"
    py_code += "\n\t\t\t\timage_widget = widgets.Image("
    py_code += "\n\t\t\t\t\tvalue=image,"
    py_code += "\n\t\t\t\t\tformat=image_filename[-3:],"
    py_code += "\n\t\t\t\t\twidth=300,"
    py_code += "\n\t\t\t\t\theight=400"
    py_code += "\n\t\t\t\t)"
    py_code += "\n\t\t\t\tgrid[:-1,1] = image_widget"
    py_code += "\n\t\timage_index += 1"
    py_code += "\n"


    for port in parsed_all_ports:
        if port[1] == "in":
            if port[2] == 1:
                # Create Button
                input_setup +=  f"\n\t{port[0]}_btn = widgets.ToggleButton("
                input_setup +=  "\n\t\tvalue=False,"
                input_setup +=  f"\n\t\tdescription='0',"
                input_setup +=  "\n\t\tdisabled=False,"
                input_setup +=  "\n\t\tlayout=Layout(width='50px'),"
                input_setup +=  "\n\t\tbutton_style='danger'"
                input_setup +=  "\n\t)"
                # Create Label
                input_setup += f"\n\t{port[0]}_lbl = widgets.Label(value='{port[0]}')"
                # Add Event Listener
                input_setup += f"\n\t{port[0]}_btn.observe(lambda change: update_button_state(change, {port[0]}_lbl, {port[0]}_btn), names='value')"
                # hbox = HBox([label1, toggle_button1, label2, toggle_button2])
                input_setup += f"\n\t{port[0]}_hbox = HBox([{port[0]}_lbl, {port[0]}_btn])"
                input_setup += "\n\thbox_layout = widgets.Layout(display='flex', justify_content='flex-end', flex_flow='row')"
                input_setup += f"\n\t{port[0]}_hbox.layout = hbox_layout"
            else:  
                input_setup +=  f"\n\t{port[0]}_tbox = widgets.Text("
                input_setup +=  "\n\t\tvalue='0x0',"
                input_setup +=  "\n\t\tplaceholder='',"
                # input_setup +=  f"\n\t\tdescription='{port[0]}:',"
                input_setup += "\n\t\tlayout=Layout(width='200px'),"
                input_setup +=  "\n\t\tdisabled=False"
                input_setup +=  "\n\t)"
                input_setup += f"\n\t{port[0]}_lbl = widgets.Label(value='{port[0]}')"
                input_setup += f"\n\t{port[0]}_hbox = HBox([{port[0]}_lbl, {port[0]}_tbox])"
                input_setup += "\n\thbox_layout = widgets.Layout(display='flex', justify_content='flex-end', flex_flow='row')"
                input_setup += f"\n\t{port[0]}_hbox.layout = hbox_layout"
            num_input += 1
        elif port[1] == "out":
            if port[2] == 1:   # This will be used to make red/green light on output later
                # Create Button
                output_setup +=  f"\n\t{port[0]}_btn = widgets.ToggleButton("
                output_setup +=  "\n\t\tvalue=False,"
                output_setup +=  f"\n\t\tdescription='0',"
                output_setup +=  "\n\t\tdisabled=True,"
                output_setup +=  "\n\t\tlayout=Layout(width='50px'),"
                output_setup +=  "\n\t\tbutton_style='danger'"
                output_setup +=  "\n\t)"

                output_setup += f"\n\t{port[0]}_lbl = widgets.Label(value='{port[0]}')"
                output_setup += "\n\thbox_layout = widgets.Layout(display='flex', justify_content='flex-start', flex_flow='row')"
                # hbox = HBox([label1, toggle_button1, label2, toggle_button2])
                output_setup += f"\n\t{port[0]}_hbox = HBox([{port[0]}_btn, {port[0]}_lbl])"
                output_setup += f"\n\t{port[0]}_hbox.layout = hbox_layout"

            elif port[2] <= 8:
                output_setup += "\n\thbox_layout = widgets.Layout(display='flex', justify_content='flex-start', flex_flow='row')"
                output_setup += f"\n\t{port[0]}_lbl = widgets.Label(value='{port[0]}')"
                for i in range(0, port[2]):
                    output_setup +=  f"\n\t{port[0]}_{i}_btn = widgets.ToggleButton("
                    output_setup +=  "\n\t\tvalue=False,"
                    output_setup +=  f"\n\t\tdescription='{i}',"
                    output_setup +=  "\n\t\tdisabled=True,"
                    output_setup +=  "\n\t\tlayout=Layout(width='25px')," 
                    output_setup +=  "\n\t\tbutton_style='danger'"
                    output_setup +=  "\n\t)"
                
                output_setup += f"\n\t{port[0]}_hbox = HBox(["
                for i in range(0, port[2]):
                    output_setup += f"{port[0]}_{port[2]-1-i}_btn, "    # Reverse order
                output_setup += f"{port[0]}_lbl])"
                output_setup += f"\n\t{port[0]}_hbox.layout = hbox_layout"
                # Set up 2-8 bit array of lights
                pass
            else:
                output_setup +=  f"\n\t{port[0]}_tbox = widgets.Text("
                output_setup +=  "\n\t\tvalue='',"
                output_setup +=  "\n\t\tplaceholder='',"
                output_setup += "\n\t\tlayout=Layout(width='200px'),"
                output_setup +=  "\n\t\tdisabled=True"
                output_setup +=  "\n\t)"
                output_setup += f"\n\t{port[0]}_lbl = widgets.Label(value='{port[0]}')"
                output_setup += f"\n\t{port[0]}_hbox = HBox([{port[0]}_tbox, {port[0]}_lbl])"
                output_setup += "\n\thbox_layout = widgets.Layout(display='flex', justify_content='flex-start', flex_flow='row')"
                output_setup += f"\n\t{port[0]}_hbox.layout = hbox_layout"
            num_output += 1

    py_code += "\n\n\t# Create Input Widgets"
    py_code += input_setup

    py_code += "\n\n\t# Create Output Widgets"
    py_code += output_setup

    py_code += "\n\n\t# Create Set Button Widgets"
    
    py_code += "\n\tdef on_button_click(arg):"
    
    # All these checkboxes I meant to say textbox
    read_input_checkbox = ""
    truncated_msgs = ""
    write_inputs = ""

    read_output_ports = ""
    set_output_checkboxes = ""
    set_placeholders = ""

    for port in parsed_all_ports:
        if port[1] == "in":
            if port[2] == 1:
                # Set value int 1 or 0 if true or false respectively.
                read_input_checkbox += f"\n\t\t{port[0]}_value = 1 if {port[0]}_btn.value else 0"
                # No need to run any truncated msgs checks as the value can only be 1/0. 
                # Set the values
                write_inputs += f"\n\t\t{port[0]}.write(0, {port[0]}_value)" 
                # No need to worry about setting placeholders either.
            else:
                # Code to read the value from each input text box
                read_input_checkbox += f"\n\t\t{port[0]}_value = {port[0]}_tbox.value"
                # Code to check if a signal has been truncated and to print relevant msg to user.
                truncated_msgs += f"\n\t\ttruncated, {port[0]}_value = check_max_value({port[0]}_value, {port[2]})"
                truncated_msgs += "\n\t\tif truncated:"
                truncated_msgs += f"\n\t\t\tprint(f\"{port[0]} value provided is > {port[2]} bits, input has been truncated to: "
                truncated_msgs += "{hex("+port[0]+"_value)}\")"
                # Check if the value is None, then we want to print a message and not assert nothing.
                truncated_msgs += f"\n\t\tif {port[0]}_value == None:"
                truncated_msgs += f"\n\t\t\tprint(f\'{port[0]} value provided is invalid, no signals have been asserted.')"
                truncated_msgs += "\n\t\t\treturn"
                # Write inputs
                write_inputs += f"\n\t\t{port[0]}.write(0, {port[0]}_value)" 
                # Set placeholder values of textboxes to last pushed value
                set_placeholders += f"\n\t\t{port[0]}_tbox.placeholder = str({port[0]}_tbox.value)"
            
        elif port[1] == "out":
            read_output_ports += f"\n\t\t{port[0]}_value = {port[0]}.read(0)"
            if port[2] == 1:
                # Set value int 1 or 0 if true or false respectively.
                set_output_checkboxes += f"\n\t\t{port[0]}_btn.button_style = 'success' if {port[0]}_value==1 else 'danger'"
                set_output_checkboxes += f"\n\t\t{port[0]}_btn.description = '1' if {port[0]}_value==1 else '0'"
                # No need to run any truncated msgs checks as the value can only be 1/0. 
                # Set the values
                # No need to worry about setting placeholders either.
            elif port[2] <= 8:
                for i in range(0, port[2]):
                    set_output_checkboxes += f"\n\t\t{port[0]}_{i}_btn.button_style = 'success' if get_bit({i}, {port[0]}_value)==1 else 'danger'"
                    set_output_checkboxes += f"\n\t\t{port[0]}_{i}_btn.description = '1' if get_bit({i}, {port[0]}_value)==1 else '0'"
                # 2-8 bit array of buttons
                pass
            else:                
                set_output_checkboxes += f"\n\t\t{port[0]}_tbox.value = hex({port[0]}_value)"

    py_code += "\n\t\t# Read Values from User Inputs"
    py_code += read_input_checkbox
    py_code += "\n\n\t\t# Check Validity of Inputs"
    py_code += truncated_msgs
    py_code += "\n\n\t\t# Write Inputs"
    py_code += write_inputs
    py_code += "\n\n\t\t# Set input placeholders"
    py_code += set_placeholders
    py_code += "\n\n\t\ttime.sleep(0.00000002)"
    py_code += "\n\n\t\t# Read Output Signals"
    py_code += read_output_ports
    py_code += "\n\n\t\t# Update Textboxes"
    py_code += set_output_checkboxes


    py_code += "\n\n\tset_signal = Button(description='Set Signals', button_style='info')"
    py_code += "\n\tset_signal.on_click(on_button_click)"
    py_code += "\n\tdisplay_button = HBox([set_signal], layout=Layout(justify_content='flex-end'))"


    py_code += "\n\n\t# Define Grid Layout"
    grid_depth = max(num_input, num_output)
    if num_input > num_output:
        grid_depth += 1
    py_code += f"\n\tgrid = GridspecLayout({grid_depth},3)"

    

    py_code += "\n\n\t# Set the Grid Widgets\n\t# Set Image (Centre, Full Height)"

    py_code += "\n\tif len(images_found) > 0:"
    py_code += "\n\t\tgrid[:-1,1] = output_svg # If there is images found, we want to make room for the toggle button."
    py_code += "\n\t\ttoggle_image_button = Button(description='Change Image', button_style='info', layout=Layout(width='auto', margin='auto'))"
    py_code += "\n\t\ttoggle_image_button.on_click(lambda b: update_image(b, grid))"
    py_code += "\n\t\tgrid[-1,1] = toggle_image_button"
    py_code += "\n\telse:"
    py_code += "\n\t\tgrid[:,1] = output_svg"


    input_grid_depth_index = 0
    input_widgets_placement = ""
    output_grid_depth_index = 0
    output_widgets_placement = ""

    # Form Placement Code    
    for port in parsed_all_ports:
        if port[1] == "in":
            if port[2] == 1:
                input_widgets_placement += f"\n\tgrid[{input_grid_depth_index}, 0] = {port[0]}_hbox"
            else:
                input_widgets_placement += f"\n\tgrid[{input_grid_depth_index}, 0] = {port[0]}_hbox"
            input_grid_depth_index += 1
        elif port[1] == "out":
            if port[2] <= 8:
                output_widgets_placement += f"\n\tgrid[{output_grid_depth_index}, 2] = {port[0]}_hbox"
            else:
                output_widgets_placement += f"\n\tgrid[{output_grid_depth_index}, 2] = {port[0]}_hbox"
            output_grid_depth_index += 1
    
    # Place button at end of inputs after loop
    input_widgets_placement += f"\n\tgrid[{input_grid_depth_index}, 0] = display_button"
    
    py_code += "\n\n\t# Input Widgets"
    py_code += input_widgets_placement
    py_code += "\n\n\t# Output Widgets"
    py_code += output_widgets_placement

    py_code += "\n\n\treturn grid"

    py_code += "\n\n\ndef check_max_value(number_str, num_bits):"
    py_code += "\n\ttry:"
    py_code += "\n\t\t# Extracting the base and value from the input string"
    py_code += "\n\t\tif number_str.startswith('0x'):"
    py_code += "\n\t\t\tbase = 16"
    py_code += "\n\t\t\tvalue = int(number_str, base)"
    py_code += "\n\t\telif number_str.startswith('0b'):"
    py_code += "\n\t\t\tbase = 2"
    py_code += "\n\t\t\tvalue = int(number_str, base)"
    py_code += "\n\t\telse:"
    py_code += "\n\t\t\tbase = 10"
    py_code += "\n\t\t\tvalue = int(number_str, base)"
    py_code += "\n"
    py_code += "\n\t\t# Calculating the maximum representable value based on the number of bits"
    py_code += "\n\t\tmax_value = 2**num_bits - 1"
    py_code += "\n"
    py_code += "\n\t\t# Checking if the value exceeds the maximum"
    py_code += "\n\t\tif value > max_value:"
    py_code += "\n\t\t\t# Truncate the value to fit within the specified number of bits"
    py_code += "\n\t\t\ttruncated_value = value % (2**num_bits)"
    py_code += "\n\t\t\treturn True, truncated_value"
    py_code += "\n\t\telse:"
    py_code += "\n\t\t\treturn False, value"
    py_code += "\n\texcept ValueError:"
    py_code += "\n\t\treturn False, None"
    

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