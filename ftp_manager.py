import pysftp

# Using the IP address directly or simply "pynq" both work.
host_name = "192.168.0.53"
other_host_name = "pynq"
user_name = "xilinx"
pass_word = "xilinx"

# NOTE: This two cnopts lines are probably big security problems if used in production
#       according to pysftp documentation.
cnopts = pysftp.CnOpts()
cnopts.hostkeys = None

# No need to set the port as 22 as this is default.
with pysftp.Connection(host=other_host_name, username=user_name, password=pass_word, cnopts=cnopts) as sftp:

    print("Connection Estabilished Successfully\n")
    print(sftp.pwd)