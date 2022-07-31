from distutils import filelist
import os
import json

path = '/home/chanhyuk/git/centroids-reid/data/market1501/bounding_box_train'
dictionary = dict()
file_list = os.listdir(path)
for file in file_list:
    id, cam, frame, det = file.split('_')
    if dictionary.get(id) == None:
        dictionary[id] = 0
    else:
        dictionary[id] += 1
for key in dictionary.keys():
    if dictionary[key] < 3:
        for file in file_list:
            if key == file.split('_')[0]:
                os.remove(os.path.join(path, file))

print(dictionary)
