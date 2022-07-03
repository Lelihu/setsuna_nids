import argparse
import numpy as np
import os

import zKITNET
from zGearbox import runFE as rfe

'''
The program aims to perform feature extration on single raw
 pcap/pcapng (raw) in a specific location. A raw produces a feature
 file .npy and a parsed file .tsv for further usage.
    
'''

if __name__ == "__main__":
    parse = argparse.ArgumentParser()
    
    parse.add_argument('-p', '--PacketFile', type = str,
                        help = "The location of raw packet. " + 
                        "Only accept file in PCAP/PCAPNG/TSV. " +
                        "Applicable for HYBRID mode only.")
    
    arg = parse.parse_args()

try:
    # Check user input (input of none)
    if not all([arg.PacketFile]):
        raise RuntimeError("[!] Setsuna>_ Missing arguements")
        
    # Check user input (file extension)
    if not arg.PacketFile.endswith('pcap') and not arg.PacketFile.endswith('pcapng'):
        raise RuntimeError(">>>-------Setsuna FE>_ Not packet file")
    
    print(">>>-------Setsuna FE>_ Loading...")
    pcapf = arg.PacketFile    
    featf = os.path.splitext(arg.PacketFile)[0] + ".npy"
    feature = rfe(zKITNET.init_FE(pcapf, np.inf))
    np.save(featf, feature)
    print(">>>-------Setsuna sFE>_ Feature vector saved into " + featf)

except RuntimeError as err:
    print(err)