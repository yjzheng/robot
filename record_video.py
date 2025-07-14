#record_video.py
import cv2

_frame_width = int(640)
_frame_height = int(480)
cap = cv2.VideoCapture(0)
ret = cap.set(cv2.CAP_PROP_FRAME_WIDTH,_frame_width)
ret = cap.set(cv2.CAP_PROP_FRAME_HEIGHT,_frame_height)

fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output002.avi', fourcc, 20.0, (_frame_width,  _frame_height))
print("Begin recoreding")
try:
   while True:
       _, frame = cap.read()
       out.write( frame)
       #cv2.imshow('test', frame)
       k = cv2.waitKey(1) & 0xFF
       if k == 27:
           break

except KeyboardInterrupt:
   print('KeyboardInterrupt')

out.release()
cap.release()
#cv2.destroyAllWindows()
