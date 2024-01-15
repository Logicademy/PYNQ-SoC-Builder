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
    
    tsv_data_filtered = []
    for row in tsv_reader:
        if row == []:
            pass
        elif row and row[0] and row[0][0] == '#':
            pass
        else:
            tsv_data_filtered.append(row)
    # Convert CSV reader into a list of lists
    # tsv_data = [row for row in tsv_reader]

    # for row in tsv_data:
    #     print(row)

    for row in tsv_data_filtered:
        print(row)

    signals_line = ""
    mode_line = ""
    radix_line = ""
    test_cases = []

    for row in tsv_data_filtered:
        if row[0] == '#':
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

    signals = []
    for i in range(len(signals_line)):  # range(1, len(signals_line)-3)
        signals.append([signals_line[i], mode_line[i], radix_line[i]])
    
    for s in signals:
        print(s)

create_jnb("E:\\HDLGEN\\RISCV_RB\\RISCV_RB\\HDLGenPrj\\RISCV_RB.hdlgen")