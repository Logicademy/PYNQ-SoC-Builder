import nbformat as nbf
import xml.dom.minidom
import csv
from io import StringIO
import html

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

    # Separating signals into input and outputs
    input_ports = []
    output_ports = []
    for port in all_ports:
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

    print("Signals: ", signals_line)
    print("Mode: ", mode_line)
    print("Radix: ", radix_line)

    signals_tb = []
    for i in range(len(signals_line)):  # range(1, len(signals_line)-3)
        signals_tb.append([signals_line[i], mode_line[i], radix_line[i]])
    
    print("Test Cases")
    for t in test_cases:
        print(t)

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
    code_cell_contents += f"test_results = [None] * {len(test_cases)}"

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

    output_file = 'generated.ipynb'
    # if output_filename is not None:
    #     output_file = output_filename

    with open(output_file, 'w') as f:
        nbf.write(notebook, f)
        
    print("Notebook Generated")


create_jnb("E:\\HDLGEN\\RISCV_RB\\RISCV_RB\\HDLGenPrj\\RISCV_RB.hdlgen")