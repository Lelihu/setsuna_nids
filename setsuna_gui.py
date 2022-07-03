import numpy as np
import pickle as pkl
import os.path as path
from time import time
from string import Template as tlp
from gooey import Gooey, GooeyParser

# KitNET module
import zKITNET as core
from zGearbox import runFE, runKN, plotRMSE, banner_gui


@Gooey(program_name = "Setsuna GUI", default_size=(800, 600), \
       tabbed_groups=True, navigation='Tabbed', disable_stop_button=True)
def main():
    parse = GooeyParser(description="A Framework For KitNET")
    
    config = parse.add_argument_group('Kit-NET Parameter', gooey_options={ 'show_border': True })
        
    config.add_argument('RunMode', choices = ['train', 'exec', 'hybrid'],
                        help = "The KitNET mode in TRAIN, EXEC, and HYBRID.")

    config.add_argument('AutoencoderSize', type=int, default=10,
                       help = "The maximum size for autoencoders in the ensemble layer.\n" + 
                               "Default is 10.")
    
    config.add_argument('FeatureMappingGrace', type=int, default=5000,
                       help = "The number of instances taken to learn the feature mapping.\n" + 
                               "Default is 5000.")
    
    config.add_argument('AnormalyDetectorGrace', type=int, default=10000,
                       help = "The number of instances used to train the anomaly detector.\n" +
                               "Default is 10000.")
    
    config.add_argument('FeatureFile', type=str, widget='FileChooser', gooey_options={ 'full_width': True }, default="N/A",
                        help = "The location of feature vectors in .NPY format." + 
                        "Applicable for TRAIN or EXEC mode. N/A for HYBRID mode.")
    
    config.add_argument('ModelFile', type=str, widget='FileChooser', gooey_options={ 'full_width': True }, default="N/A",
                        help = "The location of the trained model in .PKL format. " + 
                        "Applicable for EXEC and HYBRID mode. N/A for TRAIN mode.")
   
    config.add_argument('PacketFile', type=str, widget='FileChooser', gooey_options={ 'full_width': True }, default="N/A",
                        help = "The location of raw packet. " + 
                        "Only accept file in PCAP/PCAPNG/TSV. " +
                        "Applicable for HYBRID mode. N/A for TRAIN or EXEC mode.")
    
    arg = parse.parse_args()
    start = time()
    
    pr0 = tlp('[*] Setsuna Frame-work>_ Under $s0 mode!\n' + \
              '[*] Setsuna $s0 mode>_ Packet file: $s1\n' + \
              '[*] Setsuna $s0 mode>_ Feature file: $s2\n' + \
              '[*] Setsuna $s0 mode>_ Model file: $s3\n' + \
              '[*] Setsuna $s0 mode>_ Max autoencoder: $s4\n' + \
              '[*] Setsuna $s0 mode>_ No. of feature mapping learner: $s5\n' + \
              '[*] Setsuna $s0 mode>_ No. of Anomaly Detector: $s6')

    pr2 = tlp('[*] Setsuna $s0 mode>_ Time elapsed (mins) $s1\n' + \
              '[*] Setsuna $s0 mode>_ The Anomaly Detector threshold $s2\n' + \
              '[*] Setsuna $s0 mode>_ The RMSE over anomaly detector threshold $s3\n' + \
              '[*] Setsuna $s0 mode>_ The legnth of RMSE total number $s4\n' + \
              '[*] Setsuna $s0 mode>_ The RMSE mean $s5')
        
    try:
        
        if not arg.RunMode:
            raise RuntimeError("[!] Setsuna>_ No arguements")
        
        if arg.RunMode not in ['train', 'exec', 'hybrid']:
            raise RuntimeError("[!] Setsuna>_ Invalid options")
        
        if arg.RunMode == "train":
            
            # Check user input (input of none or zero)
            if not all([arg.AutoencoderSize, arg.FeatureMappingGrace, arg.AnormalyDetectorGrace]):
                raise RuntimeError("[!] Setsuna>_ Missing arguements or has a zero for KN")
            
            AutoencoderSize, FeatureMappingGrace, AnormalyDetectorGrace = arg.AutoencoderSize, arg.FeatureMappingGrace, arg.AnormalyDetectorGrace

            # Check user input (file extension)
            if not all([arg.FeatureFile]):#, arg.ModelFile]):
                raise RuntimeError("[!] Setsuna>_ Missing arguement for feature file or model file.")
            
            if not path.isfile(arg.FeatureFile):
                raise RuntimeError("[!] Setsuna>_ Feature file not found")
            
            # Check user input (file extension)
            if not arg.FeatureFile.endswith(".npy"):
                raise RuntimeError("[!] Setsuna>_ Invaild input for feature")
           
            # if not arg.ModelFile.endswith(".pkl"):
            #     raise RuntimeError("[!] Setsuna>_ Invaild input for model")
            
            RunMode, FeatureFile, ModelFile = str.upper(arg.RunMode), arg.FeatureFile, arg.FeatureFile + "test.pkl"
            
            print(pr0.substitute(s0=RunMode, s1='N/A', s2=FeatureFile, s3=ModelFile, \
                                 s4=AutoencoderSize, s5=FeatureMappingGrace, s6=AnormalyDetectorGrace))
    
            feature = np.load(FeatureFile, mmap_mode='r')
            feature = feature[:FeatureMappingGrace + AnormalyDetectorGrace]
            featurez = feature.shape[1]
            tkn = core.init_KN_0(ModelFile, featurez, AutoencoderSize, FeatureMappingGrace, AnormalyDetectorGrace)
            rmse = runKN(tkn, feature)
            adth = max(rmse[FeatureMappingGrace:])
            with open(ModelFile, "ab") as f:
                pkl.dump(adth, f)
            
            print("[*] Setsuna " + RunMode + " mode>_ Time elapsed (mins) " + str((time() - start)/60) + 
                  "\n[*] Setsuna " + RunMode + " mode>_ The anomaly detector threshold "+ str(adth) + 
                  "\n[*] Setsuna " + RunMode + " mode>_ The feature model is saved into " + str(ModelFile) +
                  "\n[*] Setsuna " + RunMode + " mode>_ Process completed")       
        
        if arg.RunMode == "exec":
                
            # Check user input (input of none)
            if not all([arg.FeatureFile, arg.ModelFile]):
                raise RuntimeError("[!] Setsuna>_ Missing arguements for exec")
                
            if not path.isfile(arg.FeatureFile):
                raise RuntimeError("[!] Setsuna>_ Feature file not found")
            
            if not path.isfile(arg.ModelFile):
                raise RuntimeError("[!] Setsuna>_ Model file not found")
            
            # Check user input (file extension)
            if not arg.FeatureFile.endswith(".npy"):
                raise RuntimeError("[!] Setsuna>_ Not feature file")
                
            if not arg.ModelFile.endswith(".pkl"):
                raise RuntimeError("[!] Setsuna>_ Not model file")
                
            RunMode, FeatureFile, ModelFile, AutoencoderSize = str.upper(arg.RunMode), arg.FeatureFile, arg.ModelFile, arg.AutoencoderSize
            
            graph = path.splitext(FeatureFile)[0] + ".png"
            
            print(pr0.substitute(s0=RunMode, s1='N/A', s2=FeatureFile, s3=ModelFile, \
                                 s4=AutoencoderSize, s5="Default", s6="Default"))
            
            feature = np.load(FeatureFile, mmap_mode='r')
            rmse = np.array(runKN(core.init_KN_1(ModelFile, feature.shape[1], AutoencoderSize), feature))
            
            with open(ModelFile, "rb") as f:
                _ = pkl.load(f)
                _ = pkl.load(f)
                _ = pkl.load(f)
                adth = pkl.load(f)
            rangeRmse = np.arange(0, len(rmse), 1)
            
            print(pr2.substitute(s0=RunMode, s1=(time() - start)/60, \
                                 s2=adth, s3=rmse[rmse > adth].shape, \
                                 s4=len(rmse), s5=np.mean(rmse)))
            
            plotRMSE(RunMode, rmse, rangeRmse, adth, FeatureFile, graph)
        
        if arg.RunMode == "hybrid":
            
            # Check user input (input of none)
            if not all([arg.PacketFile, arg.ModelFile]):
                raise RuntimeError("[!] Setsuna>_ Missing arguements for hybrid")
            
            # Check user input (file extension)
            if not arg.PacketFile.endswith('pcap') and not arg.PacketFile.endswith('pcapng'):
                raise RuntimeError("[!] Setsuna>_ Not packet file")
            
            if not arg.ModelFile.endswith(".pkl"):
                raise RuntimeError("[!] Setsuna>_ Not model file")
            
            RunMode, PacketFile, ModelFile, AutoencoderSize = str.upper(arg.RunMode), arg.PacketFile, arg.ModelFile, arg.AutoencoderSize
                        
            print(pr0.substitute(s0=RunMode, s1=PacketFile, s2='N/A', s3=ModelFile, \
                                 s4=AutoencoderSize, s5="Default", s6="Default"))
            
            graph = path.splitext(PacketFile)[0] + ".png"

            FE = core.init_FE(PacketFile, np.inf)
            exfeature = runFE(FE)
            rmse = np.array(runKN(core.init_KN_1(ModelFile, np.array(exfeature).shape[1], AutoencoderSize), exfeature))
            
            with open(ModelFile, "rb") as f:
                _ = pkl.load(f)
                _ = pkl.load(f)
                _ = pkl.load(f)
                adth = pkl.load(f)
            rangeRmse = np.arange(0, len(rmse), 1)
            
            print(pr2.substitute(s0=RunMode, s1=(time() - start)/60, \
                                 s2=adth, s3=rmse[rmse > adth].shape, \
                                     s4=len(rmse), s5=np.mean(rmse)))
            
            plotRMSE(RunMode, rmse, rangeRmse, adth, PacketFile, graph)
            
    except RuntimeError as err:
        print(err)
        
if __name__ == '__main__':
    main()
    banner_gui()
    print("[*] Setsuna GUI is running (Press Ctrl-C to close program)\n")