from math import ldexp
import os
import json
import cv2

# PATH
FOLDER_PATH = os.path.join((os.path.dirname(os.path.realpath(__file__))), "MCMOT")
TRAIN_FOLDER_PATH = os.path.join(FOLDER_PATH, 'image')
TRAIN_SAVE_FOLDER_PATH = os.path.join(FOLDER_PATH, 'image2')
LABEL_FOLDER_PATH = os.path.join(FOLDER_PATH, "label")

# LIST
#train_image_list = os.listdir(TRAIN_FOLDER_PATH)
label_list = os.listdir(LABEL_FOLDER_PATH)
#train_image_list.sort()
label_list.sort()
#assert(len(train_image_list) == len(label_list))

training_data = []
# Market1501 dataset format = (path, PID, CAM ID, idx(of paths))
for label_folder in label_list:
    for index, json_file in enumerate(os.listdir(os.path.join(LABEL_FOLDER_PATH, label_folder))):
        with open(os.path.join(LABEL_FOLDER_PATH, label_folder, json_file), 'r') as file:
            data = json.load(file)
            filename = os.path.join(TRAIN_FOLDER_PATH, label_folder, data['filename'])
            if 'left' in filename:
                cam = 0
            elif 'center' in filename:
                cam = 1
            else:
                cam = 2
            for object in (data['objects']):
                dictionary = object
                dictionary['filename'] = filename
                dictionary['cam'] = cam
                training_data.append(dictionary)
                x_list, y_list = list(), list()
                for geometry in dictionary['geometry']:
                    if dictionary['geometry'][geometry] is not None:
                        for position in dictionary['geometry'][geometry]:
                                x_list.append(position[0])
                                y_list.append(position[1])
                max_x, min_x = max(x_list), min(x_list)
                max_y, min_y = max(y_list), min(y_list)
                dictionary['geometry'] = [min_x, min_y, max_x, max_y]
                dictionary['idx'] = index
# filename + geometry로 image 만들어낼 수 있고, pid, cam_id, 
print('done')
