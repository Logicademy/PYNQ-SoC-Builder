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
    # Convert CSV reader into a list of lists
    tsv_data = [row for row in tsv_reader]

    for row in tsv_data:
        print(row)   










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


    
    # Convert the test plan into a 2-D array of rows and columns
    lines = TBNoteData.split("\n")
    TBNoteDataArray = []
    for line in lines:
        TBNoteDataArray.append(line.split())
    
    # TB Design Assumptions I am going to make.
    # We can learn the order of the input/output signals but it must be:
    # All inputs, then all outputs
    # We will then read the radix line and understand form for each signal
    # From here, any line beginning with a number will go: Test Number; Delay; Inputs; Outputs; Note;

    inputs = []
    outputs = []
    test_cases = []
    # Populate variables required 
    # Inputs, Outputs, compName, test_cases (in form of 2D array)
    for line in TBNoteDataArray:
        if len(line) == 0:      # Skip blank lines
            continue            
        if line[0] == "Inputs":
            for column in line:
                if column == line[0]:
                    continue
                inputs.append(column)
        elif line[0] == "Outputs":
            for column in line:
                if column == line[0]:
                    continue
                outputs.append(column)
        elif (len(line) > 0):
            if column == line[0]:
                    continue
            test_cases.append(line)


    # genFolder - VHDL Folders
    genFolder = root.getElementsByTagName("genFolder")[0]
    model_folder_path = genFolder.getElementsByTagName("vhdl_folder")[0].firstChild.data
    testbench_folder_path = genFolder.getElementsByTagName("vhdl_folder")[1].firstChild.data
    # ChatGPT_folder = genFolder.getElementsByTagName("vhdl_folder")[2]             # Commented as not needed
    # ChatGPT_Backups_folder = genFolder.getElementsByTagName("vhdl_folder")[3]     # Commented as not needed
    AMDproj_folder_path = genFolder.getElementsByTagName("vhdl_folder")[4].firstChild.data
        
    # print(testbench_cols)

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
    for i in input_ports:
        markdown_cell_contents += f"\n| {i[0]} | {i[1]} | {i[2]} | {i[3]} |"
    for o in output_ports:
        markdown_cell_contents += f"\n| {o[0]} | {o[1]} | {o[2]} | {o[3]} |"
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
    markdown_cell_contents = "|"
    for i in input_ports:
        markdown_cell_contents += f" {i[0]} |"
    for o in output_ports:
        markdown_cell_contents += f" *{o[0]}* |"
    number_of_io = len(input_ports) + len(output_ports)
    markdown_cell_contents += "\n|"
    for _ in range(number_of_io):
        markdown_cell_contents += ":----:|"
        
    for test in test_cases:
        markdown_cell_contents += f"\n| "
        for io in test:
            markdown_cell_contents += f" {io} |"

    markdown_cell = nbf.v4.new_markdown_cell(markdown_cell_contents)
    notebook.cells.append(markdown_cell)

    # Loop to Generate each test case
    test_number = 0
    for test in test_cases:
        # Create title cell.
        markdown_cell = nbf.v4.new_markdown_cell(f"**Test Case: {test_number}**")
        notebook.cells.append(markdown_cell)

        # Code Cell:
        # Generating Inputs:
        code_cell_contents = "# Asserting Inputs\n" 
        for i in range(len(input_ports)):
            code_cell_contents += f"{input_ports[i][0]}.write(0, {test[i]})\n"
        
        # Break
        code_cell_contents += "\n\n# Recording Outputs\n"
        
        # Checking Output:
        for o in range(len(output_ports)):
            code_cell_contents += f"if {output_ports[o][0]}.read(0) == {test[len(input_ports)+o]}:\n\ttest_result[{test_number}] = True\nelse:\n\ttest_result[{test_number}] = False\n"

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

    output_file = 'generated.ipynb'
    if output_filename is not None:
        output_file = output_filename

    with open(output_filename, 'w') as f:
        nbf.write(notebook, f)
        
    print("Notebook Generated")



