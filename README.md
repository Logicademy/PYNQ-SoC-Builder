# Automated PYNQ Overlay Generation

## Overview 

PYNQ Automate is a CLI tool for generating PYNQ Overlays in Vivado automatically.

## Usage:

```
python pynq_automate.py [command] --hdlgen [path to .hdlgen file]
```

## Available Commands

- generate_tcl
- run_vivado
- copy

## Installation

Clone this repo to any directory

Open CMD or Anaconda terminal and go to the cloned repo directory

Install the required libraries

```pip install -r requirements.txt```


## Overview of System to date

![Project Architecture](docs/Automation_Architecture.png)

## Examples

### Generating Tcl Script

```
python pynq_automate.py generate_tcl --hdlgen C:\projects\My_Project\HDLGenPrj\My_Project.hdlgen
```

### Running Vivado

```
python pynq_automate.py run_vivado --hdlgen C:\projects\My_Project\HDLGenPrj\My_Project.hdlgen
```

### Copying Output

```
python pynq_automate.py copy --hdlgen C:\projects\My_Project\HDLGenPrj\My_Project.hdlgen
```

If --dest flag is not specified, output files are copied to *current_directory\output*

```
python pynq_automate.py copy --hdlgen C:\projects\My_Project\HDLGenPrj\My_Project.hdlgen --dest C:\projects\output_files
```
