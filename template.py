import ipywidgets as widgets
from IPython.display import SVG, display
from ipywidgets import GridspecLayout
from ipywidgets import Button, Layout, jslink, IntText, IntSlider

file_path = 'RISCV_ALU.svg'
svg_content=""

# Read the SVG content from the file
with open(file_path, 'r') as file:
    svg_content = file.read()

# Create Input Widgets
selALUOp_tbox = widgets.Text(
    value='',
    placeholder='0x0',
    description='selALUOp:',
    disabled=False   
)
A_tbox = widgets.Text(
    value='',
    placeholder='0x00000000',
    description='A:',
    disabled=False   
)
B_tbox = widgets.Text(
    value='',
    placeholder='0x00000000',
    description='B:',
    disabled=False   
)

# Create Output Widgets
ALUOut_tbox = widgets.Text(
    value='',
    placeholder='',
    description='ALUOut:',
    disabled=True   
)
branch_tbox = widgets.Text(
    value='',
    placeholder='',
    description='branch:',
    disabled=True   
)

# Set Signals Handler
def on_button_click(arg):
    print(arg)
    print("Set Signals")

# Set Signals Button
display_button = Button(description="Set Signals", button_style="info", layout=Layout(width='auto', margin='auto'))
display_button.on_click(on_button_click)

# Format SVG Data
svg_content = svg_content.split("<?xml", 1)[-1]
svg_with_tags = f'<svg>{svg_content}</svg>'

# Create Widget Object for SVG
output_svg = Output()
with output_svg:
    display(SVG(data=svg_with_tags))

# Define Grid Layout
grid = GridspecLayout(4, 3) 

# Set the Grid Widgets
# Image (Centre, Full Height)
grid[:, 1] = output_svg

# Input Widgets
grid[0, 0] = selALUOp_tbox
grid[1, 0] = A_tbox
grid[2, 0] = B_tbox
grid[3,0] = display_button

# Output Widgets
grid[0, 2] = ALUOut_tbox
grid[1, 2] = branch_tbox

# Display Grid
display(grid)