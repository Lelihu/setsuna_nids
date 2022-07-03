import paramiko
import time
import os
from scp import SCPClient

"""

The program aims to connect to a Setsuna-deployed remote server
The location of the Setsuna should be:
    ~/zKN
Or the program cannot run as the locations within the program is hard-coded

You may smodify the path to meet your conditions, but be aware on permission issue

"""

# declare credentials   
host = '192.168.168.254'
username = 'pi'   
password = '00000000'

up = input(">>>-------Setsuna zClient Miracle Box: Upload your raw packet: ")

if not os.path.isfile(up):
    print(">>>-------Setsuna zClient Miracle Box: File " + up + " does not exist.")
    raise Exception()

type = up.split('.')[-1]
if type != "tsv" and type != "pcap" and type != 'pcapng':
    print(">>>-------Setsuna zClient Miracle Box: File " + up + " is not a tsv or pcap file.")
    raise Exception()
    
# connect to server   
con = paramiko.SSHClient()
con.load_system_host_keys()
con.connect(host, username=username, password=password)

with SCPClient(con.get_transport()) as scp:
    scp.put(up, "~/zKN/upload/packet")
    
# execute the script
stdin, stdout, stderr = con.exec_command("ls -al ~/zKN/upload/packet/" + up)

if stderr.read() != b'':
    print("An error occurred")
    raise Exception()
else:
    print(">>>-------Setsuna zClient Miracle Box: File " + up + " upload Success.")

# run the command
# Replace 'sleep 5' with your actual command which will write its output to /tmp/foo.log
# where we can read from later, make sure to also pipe stderr to stdout with 2>&1 otherwise this will hang
#stdin, stdout, stderr = con.exec_command("ls -l")# > /tmp/foo.log 2>&1 & echo $!;")
stdin, stdout, stderr = con.exec_command("python ~/zKN/expm_knCore.py -r hybrid " + 
                                         "-m ~/zKN/Monday_50000_50000.pkl " + 
                                         "-p ~/zKN/upload/packet/" + up + " " + 
                                         " > /tmp/foo.log 2>&1 & echo $!;")

procid = stdout.read().decode().strip()

print(">>>-------Setsuna zClient Miracle Box: Remote server waiting and running for process with process id ", procid)

while True:
        # Use ps to find whether the process exists, returns 2 lines if it does
        stdin, stdout, stderr = con.exec_command("ps -p " + procid)
        if len(stdout.readlines()) < 2:
                break
        time.sleep(1)  # Poll every second

# Read your output (the above sleep command won't have one)
stdin, stdout, stderr = con.exec_command("cat /tmp/foo.log")

print(stdout.read().decode())