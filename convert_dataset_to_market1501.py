from genericpath import isdir
from math import ldexp
import os
import json
import cv2
from tqdm import tqdm

# PATH
FOLDER_PATH = os.path.join((os.path.dirname(os.path.realpath(__file__))), "data/MCMOT")
TRAIN_FOLDER_PATH = os.path.join(FOLDER_PATH, 'original/train/images')
TRAIN_SAVE_FOLDER_PATH = os.path.join(FOLDER_PATH, 'rearanged/train')
LABEL_FOLDER_PATH = os.path.join(FOLDER_PATH, "original/train/labels")

# LIST
#train_image_list = os.listdir(TRAIN_FOLDER_PATH)
label_list = os.listdir(LABEL_FOLDER_PATH)
#train_image_list.sort()
label_list.sort()
#assert(len(train_image_list) == len(label_list))

training_data = []
# Market1501 dataset format = (path, PID, CAM ID, idx(of paths))
total = 0
for label_index, label_folder in enumerate(label_list):
    num_total_objects = 0
    label_file_list = os.listdir(os.path.join(LABEL_FOLDER_PATH, label_folder))
    label_file_list.sort()
    left_order, middle_order, right_order = 0, 0, 0
    order = 0
    id_dict = dict()
    id_order = 0
    for index, json_file in enumerate(tqdm(label_file_list)):
        with open(os.path.join(LABEL_FOLDER_PATH, label_folder, json_file), 'r') as file:
            data = json.load(file)
            filename = os.path.join(TRAIN_FOLDER_PATH, label_folder, data['filename'])
            if 'left' in filename:
                cam = 1
                left_order += 1
                order = left_order
            elif 'center' in filename:
                cam = 2
                middle_order += 1
                order = middle_order
            else:
                cam = 3
                right_order += 1
                order = right_order
            for object in (data['objects']):
                num_total_objects += 1
                total += 1
                dictionary = object
                dictionary['filename'] = filename
                dictionary['cam'] = cam
                if id_dict.get(dictionary['id']) == None:
                    id_dict[dictionary['id']] = id_order
                    id_order += 1
                    dictionary['id'] = id_dict[dictionary['id']]
                else:
                    dictionary['id'] = id_dict[dictionary['id']]
                training_data.append(dictionary)
                x_list, y_list = list(), list()
                for geometry in dictionary['geometry']:
                    if dictionary['geometry'][geometry] is not None:
                        for position in dictionary['geometry'][geometry]:
                                x_list.append(position[0])
                                y_list.append(position[1])
                max_x, min_x = max(x_list), min(x_list)
                max_y, min_y = max(y_list), min(y_list)

                img = cv2.imread(filename=filename)
                img_crop = img[int(max(min_y, 0)): int(min(max_y, img.shape[0])), int(max(min_x, 0)): int(min(max_x, img.shape[1]))]
                if img_crop.shape[0] > 1 and img_crop.shape[1] > 1:
                    cv2.imshow('img', img_crop)
                    cv2.waitKey(1)
                    if not os.path.isdir(os.path.join(TRAIN_SAVE_FOLDER_PATH, label_folder)):
                        os.mkdir(os.path.join(TRAIN_SAVE_FOLDER_PATH, label_folder))
                    if img_crop.shape[0]>0 and img_crop.shape[1]>0:
                        if os.path.exists(os.path.join(TRAIN_SAVE_FOLDER_PATH, label_folder,
                        str(dictionary['id']).zfill(4)+'_'
                        +'c'+str(cam)
                        +'s'+str(label_index)+'_'
                        +str(order).zfill(6)+'_'
                        +'00.jpg')):
                            pre_img = cv2.imread(os.path.join(TRAIN_SAVE_FOLDER_PATH, label_folder,
                                                str(dictionary['id']).zfill(4)+'_'
                                                +'c'+str(cam)
                                                +'s'+str(label_index)+'_'
                                                +str(order).zfill(6)+'_'
                                                +'00.jpg'))
                            height, width = pre_img.shape[0], pre_img.shape[1]
                            if ((max_x - min_x) * (max_y - min_y)) > (height * width):
                                cv2.imwrite(os.path.join(TRAIN_SAVE_FOLDER_PATH, label_folder,
                                str(dictionary['id']).zfill(4)+'_'
                                +'c'+str(cam)
                                +'s'+str(label_index)+'_'
                                +str(order).zfill(6)+'_'
                                +'00.jpg'), img_crop)
                        else:
                            cv2.imwrite(os.path.join(TRAIN_SAVE_FOLDER_PATH, label_folder,
                            str(dictionary['id']).zfill(4)+'_'
                            +'c'+str(cam)
                            +'s'+str(label_index)+'_'
                            +str(order).zfill(6)+'_'
                            +'00.jpg'), img_crop)
    print(num_total_objects)
# filename + geometry로 image 만들어낼 수 있고, pid, cam_id, 
print('done')
print(total)
