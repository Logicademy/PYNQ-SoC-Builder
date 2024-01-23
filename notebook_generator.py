import nbformat as nbf
import xml.dom.minidom
import csv
from io import StringIO
import html

# TODO: Generate Generic JNB
def create_generic_jnb(path_to_hdlgen_file, output_filename=None):
    pass


# Function to generate JNB, takes HDLGen file path and notebook name as parameters
def create_jnb(path_to_hdlgen_file, output_filename=None):

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
            print("Line 91 NBG: Invalid Port")


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
    code_cell_contents += f"\n{compName} = Overlay(/path/to/overlay)"
    code_cell_contents += "\n# Inputs:"
    for i in input_ports:
        code_cell_contents += f"\n{i[0]} = {compName}.{i[0]}"
    code_cell_contents += "\n# Outputs:"
    for o in output_ports: 
        code_cell_contents += f"\n{o[0]} = {compName}.{o[0]}"
    code_cell_contents += "\n\n# Test Case Set Up"
    code_cell_contents += f"\n# Number Of Test Cases: {len(test_cases)}"
    code_cell_contents += f"\ntest_results = [None] * {len(test_cases)}"

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

    # Loop to Generate each test case
    test_number = 0
    delay_total = 0 

    for test in test_cases:

        # print(f"Generating for test case {test_number}")
        # print(test)

        test_converted_to_decimal_from_radix = []
        for val in range(1, len(test)-3):
            radix_val = radix_line[val]
            radix_form = radix_val[-1]
            value = test[val]
            if radix_form == 'h':
                # Convert for hexidecimal
                decimal_value = int(value, 16)
                test_converted_to_decimal_from_radix.append(str(decimal_value))
            elif radix_form == 'b':
                # Convert for binary
                decimal_value = int(value, 2)
                test_converted_to_decimal_from_radix.append(str(decimal_value))
            else:
                print(f"Warning: Could not detect radix form properly for: {radix_val}")
            
        # print(test_converted_to_decimal_from_radix)

        # Create title cell.
        markdown_cell = nbf.v4.new_markdown_cell(f"**Test Case: {test_number}**")
        notebook.cells.append(markdown_cell)

        # Code Cell:
        # Generating Inputs:
        code_cell_contents = "# Asserting Inputs\n" 

        
        delay_total += int(test[-3])

        sub_signals = signals_line[1:-3]
        sub_modes = mode_line[1:-3]

        for i in range(len(sub_signals)):
            if sub_modes[i] == "in":
                code_cell_contents += f"{sub_signals[i]}.write(0, {test_converted_to_decimal_from_radix[i]})\n"

        while delay_total >= 1 and clock_enabled:
            # run clock 
            code_cell_contents += "\nRunning Clock Pulse"
            code_cell_contents += "\ntime.sleep(0.05) # Sleep for 50 ms"
            code_cell_contents += "\nclk.write(1,0)"
            code_cell_contents += "\ntime.sleep(0.05) # Sleep for 50 ms"
            code_cell_contents += "\nclk.write(0,0)\n"
            delay_total = delay_total - 1
        
        # Break
        code_cell_contents += "\n# Recording Outputs"
        code_cell_contents += "\ntst_res = []"
        # Checking Output:
        for i in range(len(sub_signals)):
            if sub_modes[i] == "out":
                code_cell_contents += f"\ntst_res.append(True if {sub_signals[i]}.read(0) == {test_converted_to_decimal_from_radix[i]} else False)"

        code_cell_contents += f"\ntest_results[{test_number}] = all(tst_res)"

        test_number += 1    # Increment Test Number after use.
        code_cell = nbf.v4.new_code_cell(code_cell_contents)
        notebook.cells.append(code_cell)


    # Finally, presenting the results in a presentable fashion:
    # Title Markdown Cell
    markdown_cell = nbf.v4.new_markdown_cell("# Test Results")
    notebook.cells.append(markdown_cell)

    code_cell_contents = "import pandas as pd\n"
    code_cell_contents += "\ndf = pd.DataFrame({'Result': test_results})"
    code_cell_contents += "\npd.set_option('display.notebook_repr_html', False)"
    code_cell_contents += "\ndef highlight_cells(val):"
    code_cell_contents += "\n\tif val == True:"
    code_cell_contents += "\n\t\treturn 'background-color: green'"
    code_cell_contents += "\n\telif val == False:"
    code_cell_contents += "\n\t\treturn 'background-color: red'"
    code_cell_contents += "\n\telse:"
    code_cell_contents += "\n\t\treturn 'background-color: darkorange'"
    code_cell_contents += "\nstyled_df = df.style.applymap(highlight_cells, subset=['Result'])"
    code_cell_contents += "\nstyled_df"
    code_cell = nbf.v4.new_code_cell(code_cell_contents)
    notebook.cells.append(code_cell)

    output_file = 'output\{name}.ipynb'
    # if output_filename is not None:
    #     output_file = output_filename

    with open(output_file, 'w') as f:
        nbf.write(notebook, f)
        
    print(f"Notebook Generated at: {output_file}")

# create_jnb("E:\\HDLGEN\\RISCV_RB\\RISCV_RB\\HDLGenPrj\\RISCV_RB.hdlgen")