import numpy as np
from scipy.cluster.hierarchy import linkage, to_tree

class corClust:
    def __init__(self, n):
        #parameter:
        self.n = n
        #varaibles
        self.c = np.zeros(n)        # linear num of features
        self.c_r = np.zeros(n)      # linear sum of feature residules
        self.c_rs = np.zeros(n)     # linear sum of feature residules
        self.C = np.zeros((n,n))    # partial correlation matrix
        self.N = 0                  # number of updates performed

    # x: a numpy vector of length n
    def update(self, x):
        self.N += 1
        self.c += x
        c_rt = x - self.c/self.N
        self.c_r += c_rt
        self.c_rs += c_rt**2
        self.C += np.outer(c_rt,c_rt)

    # creates the current correlation distance matrix between the features
    def corrDist(self):
        c_rs_sqrt = np.sqrt(self.c_rs)
        C_rs_sqrt = np.outer(c_rs_sqrt,c_rs_sqrt)
        C_rs_sqrt[C_rs_sqrt==0] = 1e-100        # this protects against dive by zero erros (occurs when a feature is a constant)
        D = 1-self.C/C_rs_sqrt                  # the correlation distance matrix
        D[D<0] = 0                              # small negatives may appear due to the incremental fashion in which we update the mean. Therefore, we 'fix' them
        return D

    # clusters the features together, having no more than maxClust features per cluster
    def cluster(self,maxClust):
        D = self.corrDist()
        Z = linkage(D[np.triu_indices(self.n, 1)])    # create a linkage matrix based on the distance matrix
        if maxClust < 1:
            maxClust = 1
        if maxClust > self.n:
            maxClust = self.n
        map = self.__breakClust__(to_tree(Z),maxClust)
        return map

    # a recursive helper function which breaks down the dendrogram branches until all clusters have no more than maxClust elements
    def __breakClust__(self,dendro,maxClust):
        if dendro.count <= maxClust:        # base case: we found a minimal cluster, so mark it
            return [dendro.pre_order()]     # return the origional ids of the features in this cluster
        return self.__breakClust__(dendro.get_left(),maxClust) + self.__breakClust__(dendro.get_right(),maxClust)
