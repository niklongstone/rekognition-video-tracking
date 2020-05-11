import numpy as np
import cv2
import json 
import argparse
import math
import helper.helper as h

# Handle parameters
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-d", "--data", help="path to the json data file with bounding boxes")
ap.add_argument("-f", "--frame", help="playback framerate", default=50, type=int)
ap.add_argument("-c", "--coord", help="JSON file to map camera coordinates", default=None)
ap.add_argument("-t", "--threshold", help="distance threshold in pixel ", default=150, type=float)

args = vars(ap.parse_args())
    
if args['coord']:
    coord =  h.load_data(args['coord'])
    hom, status = cv2.findHomography(np.array(coord['camera']), np.array(coord['plane']))

# Load video
cap = cv2.VideoCapture(args['video'])
video_width  = cap.get(cv2.CAP_PROP_FRAME_WIDTH)  # float
video_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT) # float
# Load data
data = h.load_data(args['data'])
data = h.get_category(data, 'Person')
data = h.compute_boxes(data, video_width, video_height)

# Sort data based on distance from 0,0
for k in data:
    data[k].sort(key = lambda p: math.sqrt((p['center'][0])**2 + (p['center'][1])**2))

# Define colours
RED = (0,0,255)
GREEN = (0,255,0)

# Mark closest points with RED color
MAX_DISTANCE = args['threshold']
for k in data:
    for i in range(0, len(data[k])):
        curr = data[k][i]
        curr['color'] = GREEN
        for j in range(0, len(data[k])):
            next = data[k][j]
            if args['coord']: 
                # distance on a 3D plane
                curr_center = h.transform_perspective(curr['center'], hom)
                next_center = h.transform_perspective(next['center'], hom)
                distance = h.distance(curr_center, next_center)
            else:          
                # distance on a 2D plane    
                distance = h.distance(curr['center'], next['center'])
                
            if (distance <= MAX_DISTANCE and distance > 0):
                curr['color'] = RED

PLAYBACK_FRAME_RATE = args['frame']

# Play video
while(cap.isOpened()):
    ret, frame = cap.read()
    if ret == True:
        fps = int(cap.get(cv2.CAP_PROP_POS_MSEC))
        key = min(data.keys(), key = lambda key: abs(int(key)-fps))
        res = data[key] 

        for box in res:
            #cv2.circle(frame, tuple(box['center']), 2, box['color'], -1)
            cv2.rectangle(frame, box['p1'], box['p2'], box['color'], 2, 1)

        cv2.imshow('frame', frame)
        if cv2.waitKey(PLAYBACK_FRAME_RATE) & 0xFF == ord('q'):
            break
    else: 
        break

cap.release()
cv2.destroyAllWindows()