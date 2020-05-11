import cv2
import json 
import argparse

# Handle parameters
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
args = vars(ap.parse_args())

# Callback that saves points
points = []
def mouse_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONUP:
        points.append([x,y])
        cv2.circle(frame, (x, y), 5, (255,255,0), -1)
        cv2.imshow('frame', frame)
        
# Load video
cap = cv2.VideoCapture(args['video'])
cv2.namedWindow("frame")
cv2.setMouseCallback('frame', mouse_click)

success, frame = cap.read()
text = 'Create points clockwise from top left corner, s to save q to quit'
while(success):
    cv2.imshow('frame', frame)
    cv2.putText(frame, text, (0,50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,0), 2)

    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('q'):
        break
    if key == ord('s'):
        coord = {'camera': points,
            'plane': [[0,0], [700,0], [700, 700], [0,700]]}
        with open('coordinates.json', 'w') as f:
            json.dump(coord, f)
        break

cap.release()
cv2.destroyAllWindows()