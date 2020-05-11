import math
import json
import numpy as np
import cv2

def get_category(response, category='Person'):
    labels = response["Labels"]
    data = {}
    for l in labels:
        name = l['Label']['Name']
        if category in name:
            boxes = l['Label']['Instances']
            if l['Timestamp'] in data:
                data[l['Timestamp']].append(boxes)
            else:
                data[l['Timestamp']] = boxes
                
    return data

def distance(p1, p2=(0,0)):  
    dist = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)  
    return dist  

def create_box(box, video_width, video_height):
    left = video_width * box['BoundingBox']['Left']
    top = video_height * box['BoundingBox']['Top']
    width = video_width * box['BoundingBox']['Width']
    height = video_height * box['BoundingBox']['Height']
    p1 = (int(left),int(top))
    p2 = (int(left + width), int(top + height))
    center = ((np.array(p1) + np.array(p2)) / 2).astype(int)
    center[1] += height/2
    label = {'left': left, 'top': top, 'width': width, 'height':height, 'center': center, 'p1': p1, 'p2': p2}
    
    return label

def compute_boxes(data, video_width, video_height):
    new_data = {}
    for k in data:
        for b in data[k]:
            box = create_box(b, video_width, video_height)
            if k in new_data:
                new_data[k].append(box)
            else:
                new_data[k] = [box]
    
    return new_data

def load_data(path):
    with open(path) as f:
        
        return json.load(f)


def transform_perspective(point, hom):
    point = np.array([point], dtype='float32')
    point = np.array([point])
    point = cv2.perspectiveTransform(point, hom)
    
    return point[0][0]