import nbformat as nbf
import xml.dom.minidom
import csv
from io import StringIO
import html

# Function to generate JNB, takes HDLGen file path and notebook name as parameters
def create_jnb(path_to_hdlgen_file, output_filename=None, generic=False):

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
    for port in all_ports:
        if port[0] == 'clk':
            clock_enabled = True
        if port[1] == "in":
            input_ports.append(port)
        elif port[1] == "out":
            output_ports.append(port)
        else:
            print("Line 59 NBG: Invalid Port")


    # Retrieve TB Data from HDLGen
    testbench = root.getElementsByTagName("testbench")[0]
    TBNote = testbench.getElementsByTagName("TBNote")[0]
    TBNoteData = TBNote.firstChild.data

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

    # Component Description
    markdown_cell = nbf.v4.new_markdown_cell(f"## Component Description\n\n{description}")
    notebook.cells.append(markdown_cell) 

    # Entity IO
    markdown_cell_contents = f"## Entity I/O\n\n| Name | Mode | Type | Description |\n|:----:|:----:|:----:|:------------|"
    for s in all_ports:
        markdown_cell_contents += f"\n| {s[0]} | {s[1]} | {s[2]} | {s[3]} |"
    markdown_cell = nbf.v4.new_markdown_cell(markdown_cell_contents)
    notebook.cells.append(markdown_cell)

    # Python Set Up Markdown Block
    markdown_cell = nbf.v4.new_markdown_cell(f"## Python Set Up")
    notebook.cells.append(markdown_cell)
    # Python Set Up Code Block
    code_cell_contents = "from pynq import Overlay"
    code_cell_contents += "\nimport pandas as pd"
    code_cell_contents += "\nimport time"
    code_cell_contents += "\n\n# Import Overlay"
    code_cell_contents += f"\n{compName} = Overlay(\"{compName}.bit\")"
    
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
                    split_signals.append([f"{gpio_name}_{pin_counter}_{pin_counter+31}", 32])
                    if gpio_mode == "out":
                        output_split.append(f"{gpio_name}_{pin_counter}_{pin_counter+31}")
                    else:
                        input_split.append(f"{gpio_name}_{pin_counter}_{pin_counter+31}")
                    pin_counter += 32
                elif gpio_width - pin_counter <= 32:
                    split_signals.append([f"{gpio_name}_{pin_counter}_{gpio_width-1}", gpio_width-pin_counter])
                    if gpio_mode == "out":
                        output_split.append(f"{gpio_name}_{pin_counter}_{pin_counter+31}")
                    else:
                        input_split.append(f"{gpio_name}_{pin_counter}_{pin_counter+31}")
                    pin_counter += gpio_width - pin_counter
                    
            if len(output_split) > 1:
                large_output_signals.append(output_split)
            if len(input_split) > 1:
                large_input_signals.append(input_split)
                    
        
    code_cell_contents += "\n# Declare Signal Objects"
    for sig in split_signals:
        code_cell_contents += f"\n{sig[0]} = {compName}.{sig[0]}"


    if clock_enabled:
        code_cell_contents += "\n# Set-Up Clock Function\ndef run_clock_pulse():"
        code_cell_contents += "\n\ttime.sleep(0.0000002)"
        code_cell_contents += "\n\tclk.write(0,1)"
        code_cell_contents += "\n\ttime.sleep(0.0000002)"
        code_cell_contents += "\n\tclk.write(0,0)\n"

    ##### Break here if only dealing with skeleton code.
    # Possible To-do here is a "example" cell showing how to use signals

    if not generic:

        code_cell = nbf.v4.new_code_cell(code_cell_contents)
        notebook.cells.append(code_cell)

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
        markdown_cell = nbf.v4.new_markdown_cell("# Test Execution Set-Up Code")
        notebook.cells.append(markdown_cell) 


        code_cell_contents = "# Test Case Set Up"
        code_cell_contents += f"\n# Number Of Test Cases: {len(test_cases)}"
        code_cell_contents += f"\ntest_results = [None] * {len(test_cases)}"
        
        # The next section of code is difficult to read.
        # We need to loop outputs 3 separate times in the next few lines of code.
        # Therefore, all 3 strings are going to be made together now but injected into JNB
        # At different points over the next 30 lines.

        # 1) Create output signals array
        # 2) Read each output signal signal.read(0)
        # 3) Store results as test_results[test] = [signal1_val, signal2_val, signal3_val]
        sub_signals = signals_line[1:-3]
        sub_modes = mode_line[1:-3]
        sub_radix = radix_line[1:-3]  
        output_radix = []

        string1 = "\noutput_signals = ["
        # string2 = ""
        string3 = "\n\t\ttest_results[test] = ["
        for i in range(len(sub_signals)):
                if sub_modes[i] == "out":
                    string1 += "'"+sub_signals[i] + "', " # signal1, 
                    try:
                        if sub_radix[i][-1] == "h":
                            string3 += f"hex({sub_signals[i]}_val), "
                        elif sub_radix[i][-1] == "b":
                            string3 += f"bin({sub_signals[i]}_val), "
                        if sub_radix[i][-1] == "d":
                            string3 += f"str({sub_signals[i]}_val), "
                    except Exception:
                        pass                    
                    output_radix.append(sub_radix[i])

        string1 = string1[:-2] + "]" # delete the last ", " and add "]" instead
        string3 = string3[:-2] + "]" # delete the last 

        # Loop Outputs
        code_cell_contents += string1
                    
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
                read_sigs_substring = f" | ({sig_array[x]}_val << {32*x-1})" + read_sigs_substring
            read_signals_string += read_sigs_substring[2:]

        # for i in range(len(sub_signals)):
        #     if sub_modes[i] == "out":

        #         # dOut_32_63_val = dOut_32_63.read(0)
        #         # dOut_0_31_val = dOut_0_31.read(0)
        #         # dOut_val = (dOut_32_63_val << 32) | dOut_0_31_val

        #         # String 2 here 

        #         read_signals_string += "\n\t\t" + sub_signals[i] + "_val = " + sub_signals[i] + ".read(0)"    # reading each signal   <- Working perfectly
                    
        
        
        
        code_cell_contents += read_signals_string
                
        code_cell_contents += string3
        
        code_cell_contents += "\n\t\tdf = pd.DataFrame({"
        code_cell_contents += "\n\t\t\t'Signal': output_signals,"
        code_cell_contents += "\n\t\t\t'Expected Result': expected_results[test],"
        code_cell_contents += "\n\t\t\t'Observed Result': test_results[test],"
        code_cell_contents += "\n\t\t\t'Test Passed?': [a == b for a, b in zip(expected_results[test], test_results[test])]"
        code_cell_contents += "\n\t\t})"
        code_cell_contents += "\n\t\treturn df.style.applymap(color_test_passed, subset=['Test Passed?'])"
        code_cell_contents += "\n\telse:"
        code_cell_contents += "\n\t\tprint('Invalid Test Number Provided')"

        code_cell = nbf.v4.new_code_cell(code_cell_contents)
        notebook.cells.append(code_cell)

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
                
                value = filtered_test[val]
                signal_name = signals_line[val+1]

                if radix_form == 'h':
                    # If the signal is short, just story it, if the signal is large then we want to divide it into 32 bit chunks
                    if signal_name in small_input_signals:
                        test_converted_to_decimal_from_radix_dictionary[signal_name] = f"int(\"{value}\", 16)"
                    else:
                        radix_number = 64
                        test_converted_to_decimal_from_radix_dictionary[signal_name] = hex_to_padded_chunks(value, radix_number)
                    

                    # Convert for hexidecimal
                    # decimal_value = int(value, 16)
                    # test_converted_to_decimal_from_radix.append(str(decimal_value))
                    test_converted_to_decimal_from_radix.append(f"int(\"{value}\", 16)")
                elif radix_form == 'b':
                    if signal_name in small_input_signals:
                        test_converted_to_decimal_from_radix_dictionary[signal_name] = f"int(\"{value}\", 2)"
                    # Convert for binary
                    # decimal_value = int(value, 2)
                    # test_converted_to_decimal_from_radix.append(str(decimal_value))
                    test_converted_to_decimal_from_radix.append(f"int(\"{value}\", 2)")
                elif radix_form == "d":
                    if signal_name in small_input_signals:
                        test_converted_to_decimal_from_radix_dictionary[signal_name] = f"{value}"

                    
                    # Convert for binary
                    # decimal_value = int(value, 2)
                    # test_converted_to_decimal_from_radix.append(str(decimal_value))
                    test_converted_to_decimal_from_radix.append(f"{value}")
                else:
                    print(f"Warning: Could not detect radix form for: {radix_val}")
                
            # print(test_converted_to_decimal_from_radix)

            # Create title cell.
            markdown_cell = nbf.v4.new_markdown_cell(f"**Test Case: {test_number}**")
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
                if isinstance(value, list):
                    # Find the array in large_input_signals that has same name [1]
                    for sig in large_input_signals:
                        if sig[0] == key:
                            # Found the signal names.
                            for i in range(0, len(sig)-1):
                                code_cell_contents += f"{sig[i+1]}.write(0, int(\"{value[i]}\", 16))\n"
                    
                    pass # deal with array
                else:
                    code_cell_contents += f"{key}.write(0, {value})\n"



            while delay_total >= 1 and clock_enabled:
                # run clock 
                code_cell_contents += "\nrun_clock_pulse()"
                delay_total = delay_total - 1


            # Break
            code_cell_contents += "\n\n# Recording Outputs"
            code_cell_contents += f"\nsave_and_print_test({test_number})"
            # code_cell_contents += "\ntst_res = []"
            # # Checking Output:
            # for i in range(len(sub_signals)):
            #     if sub_modes[i] == "out":
            #         code_cell_contents += f"\ntst_res.append(True if {sub_signals[i]}.read(0) == {test_converted_to_decimal_from_radix[i]} else False)"

            # code_cell_contents += f"\ntest_results[{test_number}] = all(tst_res)"

            # Code to print summary and present results.
            #code_cell_contents += 


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

    else: 
        code_cell = nbf.v4.new_code_cell(code_cell_contents)
        notebook.cells.append(code_cell)

    output_file = f'{output_filename}\{name}.ipynb'
    # if output_filename is not None:
    #     output_file = output_filename

    with open(output_file, 'w') as f:
        nbf.write(notebook, f)
        
    print(f"Notebook Generated at: {output_file}")


def hex_to_padded_chunks(hex_number, desired_bits):
    # Convert hex to binary and remove the '0b' prefix
    binary_representation = bin(int(hex_number, 16))[2:]
    print(binary_representation)

    # Ensure the binary representation has a length that is a multiple of 32
    binary_representation = binary_representation.zfill(desired_bits)
    print(binary_representation)

    # Calculate the number of chunks needed
    num_chunks = (len(binary_representation) + 31) // 32
    print(num_chunks)

    flipped_binary = binary_representation[::-1]

    # Split the binary representation into 32-bit chunks and pad each chunk
    chunks = [flipped_binary[i*32:(i+1)*32] for i in range(num_chunks)]
    print(chunks)

    flipped_chunks = chunks[::-1]
    print(flipped_chunks)
    
    normalized_chunks = [element[::-1] for element in flipped_chunks]
    print(normalized_chunks)
    # Convert each padded chunk back to hexadecimal
    # hex_chunks = [hex(int(chunk, 2))[2:].zfill(8) for chunk in padded_chunks]

    hex_arrays = [hex(int(binary, 2))[2:].zfill(len(binary) // 4) for binary in normalized_chunks]

    print(hex_arrays)

    return hex_arrays
