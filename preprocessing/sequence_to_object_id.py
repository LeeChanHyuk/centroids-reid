import os
from pickle import NONE
import shutil

base_path = '/home/chanhyuk/git/centroids-reid/data/MCMOT/rearanged/test'
save_path = '/home/chanhyuk/git/centroids-reid/data/MCMOT/rearanged/test2'
folder_list = os.listdir(base_path)
folder_list.sort()

# 0000_c1s1_000001_00
id_list = []
for folder in folder_list:
    id_dict = dict()
    for file in os.listdir(os.path.join(base_path, folder)):
        id, cam, frame, det = file.split('_')
        if id_dict.get(id) == None:
            id_dict[id] = 0
        else:
            id_dict[id] += 1
    id_list.append(len(id_dict))
print(folder_list)
for folder_index, folder in enumerate(folder_list):
    if not os.path.exists(os.path.join(save_path, folder)):
        os.mkdir(os.path.join(save_path, folder))
    for file in os.listdir(os.path.join(base_path, folder)):
        id, cam, frame, det = file.split('_')
        if folder_index>0:
            offset = 0
            for i in range(folder_index):
                offset += id_list[i]
            new_id = int(id) + int(offset)
        else:
            new_id = int(id)
        new_id = str(new_id).zfill(6)
        shutil.copy2(
            os.path.join(base_path, folder, file),
            os.path.join(save_path, folder,
            new_id+'_'+cam+'_'+frame+'_'+det
            )
        )
print(id_list)
