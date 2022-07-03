import argparse
import os
import glob
import time
import pandas as pd
import numpy as np

import zKITNET
from zGearbox import runFE as zGRun
from zGearbox import checkFile as zGCheck
from zGearbox import banner_tool as banner

'''
    Setsuna zJOIN: A toolbox specificly build for Kitsune

'''

if __name__ == "__main__":
    banner()
    parser = argparse.ArgumentParser()
    parser.add_argument('--pcapIn', type=str,
                        help="Get features from the location of PCAP/PCAPNG/TSV")
    
    parser.add_argument('--tsvIn', type=str,
                        help="Get features from the location of TSVs")
    
    parser.add_argument('--npyIn', type=str,
                        help="Concat features from the location of NPYs")
    
    arg = parser.parse_args()
    
    try:
        if not arg.tsvIn and not arg.npyIn and not arg.pcapIn:
            raise RuntimeError("[!] Setsuna zTOOL>_ No argument. "
                               "Use -h for details")
        
        if all([arg.tsvIn, arg.npyIn]) or all([arg.tsvIn, arg.pcapIn]) or all([arg.npyIn, arg.pcapIn]):
            raise RuntimeError("[!] Setsuna zTOOL>_ Too many arguments. "
                               "Use -h for details")
                
        tsvIn, npyIn, pcapIn = arg.tsvIn, arg.npyIn, arg.pcapIn
        start = time.time()
        
        if pcapIn:
            runMode = 'pcapIn'
            i = 0
            LISTFILES = glob.glob(os.path.join(pcapIn, "*"))
            zGCheck(LISTFILES, runMode)
            for f in LISTFILES:
                fileType = f.split('.')[-1]
                if fileType not in ['tsv', 'pcapng', 'pcap']:
                    continue
                else:
                    i = 1
                    featureFile = os.path.splitext(f)[0] + ".npy"
                    result = zGRun(zKITNET.init_FE(f, np.inf))
                    np.save(featureFile, result)
                    print("[-] Setsuna zTOOL>_ Finish and saved in " + featureFile)    
            if i != 1:
                print("[-] Setsuna zTOOL>_ No file proceed")

        if tsvIn:
            runMode = 'tsvIn'
            
            print("[-] Setsuna zTOOL>_ Loading TSVs...")
            LISTFILES = glob.glob(os.path.join(tsvIn, "*.tsv"))
            zGCheck(LISTFILES, runMode)
            loadedData = (pd.read_csv(f) for f in LISTFILES)
            
            print("[-] Setsuna zTOOL>_ Joining TSVs...")
            concateData = pd.concat(loadedData, ignore_index=True)
            mergeData = str(LISTFILES[0]) + "_merged.tsv"
            concateData.to_csv(mergeData, index=False)
            
            print("[-] Setsuna zTOOL>_ Finish and saved in " + mergeData)

        if npyIn:
            runMode = 'npyIn'
            
            print("[-] Setsuna zTOOL>_ Loading NPYs...")
            LISTFILES = glob.glob(os.path.join(npyIn, "*.npy"))
            zGCheck(LISTFILES, runMode)
            
            print("[-] Setsuna zTOOL>_ Joining NPYs...")
            mergeData = str(LISTFILES[0]) + "_merged.npy"
            loadedFeature = []
            for f in LISTFILES:
                loadedData = np.load(f, mmap_mode='r')
                loadedFeature.append(loadedData)
            np.save(mergeData, np.concatenate(loadedFeature))
            
            print("[-] Setsuna zTOOL>_ Finish and saved in " + mergeData)
            
    except RuntimeError as err:
        print(err)
