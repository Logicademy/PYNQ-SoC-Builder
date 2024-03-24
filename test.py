import os

source = r"C:\repo\HDLGen-ChatGPT-Latest\User_Projects\ToLuke\FIFOs\FIFO4x64Top"

# Split the path into directory and filename
head, tail1 = os.path.split(source)
head, tail2 = os.path.split(head)
result = os.path.join(tail2, tail1)
print(result)
