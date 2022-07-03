import matplotlib.pyplot as plt
import os.path as path
import numpy as np

def checkFile(fileList, mode):
    if not fileList:
        raise RuntimeError ("[-] Setsuna KN-Gearbox>_ File not found")
    for f in fileList:
        if mode in ["tsvIn", "npyIn"]:
            if f.endswith("_merged.tsv") or f.endswith("_merged.npy"):
                raise RuntimeError("[-] Setsuna KN-Gearbox>_ Merged file is found so exit the program")

def runFE(feature):
    print("[-] Setsuna KN-Gearbox>_ Passing data in FE mode")
    STOP_FLAG = 999999999.
    RMSEs = []
    i = 0
    while True:
        i+=1
        rmse = feature.proc_next_packet()
        if i % 2500 == 0:
            print("[-] Setsuna KN-Gearbox>_ Proceed", i, "packets.")
        if rmse[0] == STOP_FLAG:
            break
        RMSEs.append(rmse)
    print("[-] Setsuna KN-Gearbox>_ Complete and Output Features")
    return RMSEs

def runKN(K, feature):
    print("[-] Setsuna KN-Gearbox>_ Passing data in KN mode")
    RMSEs = []
    for i, j in enumerate(feature):
        rmse = K.proc_next_packet(j)
        if i % 2500 == 0:
            print("[-] Setsuna KN-Gearbox>_ Proceed", i, "packets")
        if rmse == -1:
            break
        RMSEs.append(rmse)
    print("[-] Setsuna KN-Gearbox>_ Finish")
    return RMSEs

def plotRMSE (runMode, rmse, rangeRmse, adth, filePath, rmseFig):
    # plt.figure(figsize=(16, 5.5))
    # plt.plot(rangeRmse, rmse, c='orange', lw=0.2, label="Packets", )
    # plt.bar(rangeRmse, rmse, alpha=0.2, align='center', width=(rangeRmse[1]-rangeRmse[0])*0.8)
    # plt.scatter(rangeRmse, rmse, s=0.2,)
    # plt.plot(rangeRmse, [adth]*len(rmse), c='black', lw=2, label="Abnormal Threshold", )
    plt.figure(figsize=(16, 5.5))
    plt.plot(rangeRmse, rmse, c='orange', lw=0.2, label="Packets", )
    plt.plot(rangeRmse, [adth]*len(rmse), c='black', lw=2, label="Abnormal Threshold", )
    plt.title("Abnormal RMSE scores plot")
    plt.xlabel("Packets elapsed")
    plt.ylabel("RMSE scores")
    plt.legend()
    plt.tight_layout()
    plt.savefig(rmseFig, dpi=350)
    print("[*] Setsuna " + runMode + " mode>_ The RMSE figure saved is saved into " + rmseFig +
          "\n[*] Setsuna " + runMode + " mode>_ Complete")
    plt.show()

def plotRMSE_web (runMode, rmse, rangeRmse, adth, filePath, rmseFig):
    plt.figure(figsize=(16, 5.5))
    plt.plot(rangeRmse, rmse, c='orange', lw=0.2, label="Packets", )
    plt.plot(rangeRmse, [adth]*len(rmse), c='black', lw=2, label="Abnormal Threshold", )
    fileName = path.split(filePath)[1]
    plt.title("Abnormal RMSE scores plot " + fileName)
    plt.xlabel("Packets elapsed")
    plt.ylabel("RMSE scores")
    plt.legend()
    #plt.tight_layout()
    plt.savefig(rmseFig, dpi=350)
    print("[*] Setsuna " + runMode + " mode>_ The RMSE figure saved is saved into " + rmseFig +
          "\n[*] Setsuna " + runMode + " mode>_ Complete")
    # plt.show()

def banner():
    print("""
                                        
███████╗███████╗████████╗███████╗██╗   ██╗███╗   ██╗ █████╗ 
██╔════╝██╔════╝╚══██╔══╝██╔════╝██║   ██║████╗  ██║██╔══██╗
███████╗█████╗     ██║   ███████╗██║   ██║██╔██╗ ██║███████║
╚════██║██╔══╝     ██║   ╚════██║██║   ██║██║╚██╗██║██╔══██║
███████║███████╗   ██║   ███████║╚██████╔╝██║ ╚████║██║  ██║
╚══════╝╚══════╝   ╚═╝   ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝
""")

def banner_gui():
    print("""
  ______                                     _______      _ 
 / _____)        _                          / _____)     (_)
( (____  _____ _| |_  ___ _   _ ____  _____| |   ___ _   _ _ 
 \____ \| ___ (_   _)/___| | | |  _ \(____ | | (_  | | | | |
 _____) | ____| | |_|___ | |_| | | | / ___ | |___) | |_| | |
(______/|_____)  \__(___/|____/|_| |_\_____|\_____/|____/|_|
""")

def banner_tool():
    print("""
   ____    __                   ______          _____          
  / __/__ / /______ _____  ___ /_  __/__  ___  / / _ )___ __ __
 _\ \/ -_) __(_-< // / _ \/ _ `// / / _ \/ _ \/ / _  / _ \\ \ /
/___/\__/\__/___|_,_/_//_/\_,_//_/  \___/\___/_/____/\___/_\_\ 
""")

def banner_web():
    print("""
  ___      _                   __      __   _     ___      _ 
 / __| ___| |_ ____  _ _ _  __ \ \    / /__| |__ / __|_  _(_)
 \__ \/ -_)  _(_-< || | ' \/ _` \ \/\/ / -_) '_ \ (_ | || | |
 |___/\___|\__/__/\_,_|_||_\__,_|\_/\_/\___|_.__/\___|\_,_|_|
""")