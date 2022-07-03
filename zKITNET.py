import numpy as np
import pickle
from zFE import FE
import KitNET.dA as AE
import KitNET.corClust as CC

######################################################################
########## START:    USED FOR INITIATE FE ONLY
class init_FE:
    def __init__(self, file_path, limit):
        self.FE = FE(file_path, limit)
        self.AnomDetector = self.initKN(self.FE.get_num_features())
    
    def initKN(self, n, feature_map = None):
        self.n = n
        self.v = feature_map
        if self.v is None:
            print("[!] Kit-NET TO-FEXT>_ Under operation with "
                  "Feature-Mapper-train-mode, Anomaly-Detector-off-mode")
        self.FM = CC.corClust(self.n)

    def proc_next_packet(self):
        STOP_FLAG = 999999999.
        count = self.FE.get_next_vector()
        if len(count) == 0:
            return [STOP_FLAG, STOP_FLAG]
        return count
    
########## END
######################################################################

######################################################################
########## START:    USED FOR INITIATE KITNET ONLY
class init_KN_0:
    def __init__(self, model_save_path, n, max_autoencoder_size, FM_grace_period, AD_grace_period, learning_rate=0.1, hidden_ratio=0.75):
        self.AnomDetector = KitNET_train(model_save_path, n, max_autoencoder_size, FM_grace_period, AD_grace_period, learning_rate, hidden_ratio)
    
    def proc_next_packet(self, x):
        return self.AnomDetector.process(x)

class init_KN_1:
    def __init__(self, model_save_path, featurez, max_autoencoder_size, learning_rate=0.1, hidden_ratio=0.75):
        self.AnomDetector = KitNET_execu(model_save_path, featurez, max_autoencoder_size, learning_rate, hidden_ratio)
    
    def proc_next_packet(self, x):     
        return self.AnomDetector.execute(x)

########## END
######################################################################

######################################################################
########## START:    USED FOR TRAINING ONLY
class KitNET_train:
    def __init__(self, model_save_path, n, max_autoencoder_size=10, FM_grace_period=5000, AD_grace_period=50000, learning_rate=0.1, hidden_ratio=0.75, feature_map = None):
        self.f = open(model_save_path, "wb")
        #self.f = open(model_save_path, "ab+")
        self.AD_grace_period = AD_grace_period
        self.FM_grace_period = FM_grace_period
        self.m = 10 if max_autoencoder_size <= 0 else max_autoencoder_size
        self.lr = learning_rate
        self.hr = hidden_ratio
        self.n = n
        self.n_trained = 0      # the number of training instances so far
        self.n_executed = 0     # the number of executed instances so far
        self.v = feature_map
        if self.v is None:
            print("[!] Kit-NET TRAIN mode>_ Current state is: "
                  "Feature-Mapper: train-mode, Anomaly-Detector: off-mode")
        else:
            self.__createAD__()
            print("[!] Kit-NET TRAIN mode>_ Current state is: "
                  "Feature-Mapper: execute-mode, Anomaly-Detector: train-mode")
        # Incremental feature cluatering for the feature mapping process
        self.FM = CC.corClust(self.n)
        self.ensembleLayer = []
        self.outputLayer = None

    def process(self, x):
        # If both the FM and the AD are in execute-mode
        if self.n_trained >= self.FM_grace_period + self.AD_grace_period:
            return 0.0
        else:
            return self.train(x)

    def train(self, x):
        # For the FM in train-mode and feature mapping is None
        if self.n_trained <= self.FM_grace_period and self.v is None:
            self.FM.update(x)
            # See if the feature mapping should be instantiated
            if self.n_trained == self.FM_grace_period:
                self.v = self.FM.cluster(self.m)
                pickle.dump(self.v, self.f)
                print("[!] Kit-NET TRAIN mode>_ Instantiated mapping(v) has been saved in file")
                self.__createAD__()
                print("[!] Kit-NET TRAIN mode>_ The feature-mapper found a mapping -> " + \
                      str(self.n) + " features to " + str(len(self.v)) + " autoencoders")
                print("[!] Kit-NET TRAIN mode>_ Under operation with "
                      "feature-mapper in execute-mode, anomaly-detector in train-mode")
            train_rmse = 0.
        else:
            # Train
            S_l1 = np.zeros(len(self.ensembleLayer))
            for a in range(len(self.ensembleLayer)):
                xi = x[self.v[a]]
                S_l1[a] = self.ensembleLayer[a].train(xi)
            train_rmse = self.outputLayer.train(S_l1)
            if self.n_trained == self.AD_grace_period+self.FM_grace_period-1:
                pickle.dump(self.ensembleLayer, self.f)
                print("[!] Kit-NET TRAIN mode>_ Ensemble layer has been saved in file")
                pickle.dump(self.outputLayer, self.f)
                print("[!] Kit-NET TRAIN mode>_ Output layer has been saved in file")
                print("[!] Kit-NET TRAIN mode>_ Can operate with "
                      "feature-mapper in execute-mode, anomaly-detector in execute-mode")
                self.f.close()
        self.n_trained += 1
        return train_rmse

    def __createAD__(self):
        for map in self.v:
            params = AE.dA_params(n_visible=len(map), n_hidden=0, lr=self.lr, corruption_level=0, gracePeriod=0, hiddenRatio=self.hr)
            self.ensembleLayer.append(AE.dA(params))

        params = AE.dA_params(len(self.v), n_hidden=0, lr=self.lr, corruption_level=0, gracePeriod=0, hiddenRatio=self.hr)
        self.outputLayer = AE.dA(params)

########## END
######################################################################


######################################################################
########## START:    USED FOR EXECUTE ONLY
class KitNET_execu:
    def __init__(self, model_save_path, n, max_autoencoder_size=10, learning_rate=0.1, hidden_ratio=0.75):
        f = open(model_save_path, "rb")
        print("[!] Kit-NET EXEC mode>_ Execution in progress...")
        self.m = 10 if max_autoencoder_size <= 0 else max_autoencoder_size
        self.lr = learning_rate
        self.hr = hidden_ratio
        self.n = n
        self.n_executed = 0
        self.v = pickle.load(f)
        print("[!] Kit-NET EXEC mode>_ Mapping(v) has been loaded from file...")
        self.FM = CC.corClust(self.n)
        self.ensembleLayer = []
        self.outputLayer = None
        self.ensembleLayer = pickle.load(f)
        print("[!] Kit-NET EXEC mode>_ Ensemble layer has been loaded from file...")
        self.outputLayer = pickle.load(f)
        print("[!] Kit-NET EXEC mode>_ Output layer has been loaded from file...")
        f.close()

    def execute(self, x):
        if self.v is None:
            print( "[!] Kit-NET EXEC mode Error>_ No feature mapping. " + \
                  "Try to run TRAIN mode to get the feature map.")
            exit()
        else:
            self.n_executed += 1
            S_l1 = np.zeros(len(self.ensembleLayer))
            for a in range(len(self.ensembleLayer)):
                xi = x[self.v[a]]
                S_l1[a] = self.ensembleLayer[a].execute(xi,1)
            return self.outputLayer.execute(S_l1,2)
        
########## END:    USED FOR EXECUTE ONLY 
######################################################################x