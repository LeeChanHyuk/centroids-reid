import os
import shutil

load_path = '/home/chanhyuk/git/centroids-reid/data/MCMOT/rearanged/test2'
save_path = '/home/chanhyuk/git/centroids-reid/data/market1501'

for index, folder in enumerate(os.listdir(load_path)):
    if index < 8:
        for file in os.listdir(os.path.join(load_path, folder)):
            shutil.copy2(
                os.path.join(load_path, folder, file),
                os.path.join(save_path, 'bounding_box_train', file)
            )
    else:
        for file in os.listdir(os.path.join(load_path, folder)):
            shutil.copy2(
                os.path.join(load_path, folder, file),
                os.path.join(save_path, 'bounding_box_test', file)
            )
            shutil.copy2(
                os.path.join(load_path, folder, file),
                os.path.join(save_path, 'query', file)
            )