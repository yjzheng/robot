import cv2

#_frame_width = int(1024)
#_frame_height = int(768)
cap = cv2.VideoCapture(0)
#ret = cap.set(cv2.CAP_PROP_FRAME_WIDTH,_frame_width)
#ret = cap.set(cv2.CAP_PROP_FRAME_HEIGHT,_frame_height)

#fourcc = cv2.VideoWriter_fourcc(*'XVID')
#out = cv2.VideoWriter('output.avi', fourcc, 20.0, (_frame_width,  _frame_height))

def zoom_at(img, zoom, coord=None):
    """
    Simple image zooming without boundary checking.
    Centered at "coord", if given, else the image center.

    img: numpy.ndarray of shape (h,w,:)
    zoom: float
    coord: (float, float)
    """
    # Translate to zoomed coordinates
    h, w, _ = [ zoom * i for i in img.shape ]
    #print(img.shape)
    #print(h,w)
    
    if coord is None: cx, cy = w/2, h/2
    else: cx, cy = [ zoom*c for c in coord ]
    
    img = cv2.resize( img, (0, 0), fx=zoom, fy=zoom)
    img = img[ int(round(cy - h/zoom * .5)) : int(round(cy + h/zoom * .5)),
               int(round(cx - w/zoom * .5)) : int(round(cx + w/zoom * .5)),
               : ]
    
    return img

frame_width =  int(cap.get( cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
zoom_scale = 1.0
guide_line_begin = int(frame_width / 2)
guide_line_end = int(frame_width / 2)
try:
   while True:
      _, frame = cap.read()
      #out.write( frame)
      #cv2.imshow('view', frame)

      zoom = zoom_at(frame, zoom_scale)
      cv2.line(zoom,(guide_line_begin,0),(guide_line_end,zoom.shape[0]),(255,255,0),2)
      cv2.imshow("zoom",zoom)
      k = cv2.waitKey(1) & 0xFF
      #print("k=", k)
      char = chr(k)
      if k == 27:
         break
      elif char == '+':
         zoom_scale += 0.5
      elif char == '-':
         if(zoom_scale > 1.0):
            zoom_scale -= 0.5
      elif char == '1':
         guide_line_begin -= 1
      elif char == '2':
         guide_line_begin += 1
      elif char == 'q':
         guide_line_end -= 1
      elif char == 'w':
         guide_line_end += 1
      elif char == 'a':
         guide_line_begin -= 10
      elif char == 's':
         guide_line_begin += 10
      elif char == 'z':
         guide_line_end -= 10
      elif char == 'x':
         guide_line_end += 10
except KeyboardInterrupt:
   print('KeyboardInterrupt')

#out.release()
cap.release()
cv2.destroyAllWindows()
