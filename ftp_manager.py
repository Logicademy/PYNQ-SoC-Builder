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
# with pysftp.Connection(host=other_host_name, username=user_name, password=pass_word, cnopts=cnopts) as sftp:
#     print("Connection Estabilished Successfully\n")
#     print(sftp.pwd)

def pwd():
    with pysftp.Connection(host=host_name, username=user_name, password=pass_word, cnopts=cnopts) as sftp:
        print("Connection Estabilished Successfully\n")
        result = sftp.pwd
        print(result)
        return result
    
def upload_file(local_path, remote_path):
    with pysftp.Connection(host=host_name, username=user_name, password=pass_word, cnopts=cnopts) as sftp:
        print("Connection Estabilished Successfully\n")
        sftp.put(local_path, remote_path)
    
def download_file(remote_path, local_path):
    with pysftp.Connection(host=host_name, username=user_name, password=pass_word, cnopts=cnopts) as sftp:
        print("Connection Estabilished Successfully\n")
        sftp.get(remote_path, local_path)



    # with sftp.cd('/allcode'):           # temporarily chdir to allcode
    #     sftp.put('/pycode/filename')  	# upload file to allcode/pycode on remote
    #     sftp.get('remote_file')         # get a remote file