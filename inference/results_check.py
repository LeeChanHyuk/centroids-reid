import os
import numpy as np

path = '/home/chanhyuk/git/centroids-reid/data/market1501/similarity'
file = 'results.npy'

data = np.load(os.path.join(path, file), allow_pickle=True)
print(data[0])
print(data[1])