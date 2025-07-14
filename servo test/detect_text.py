import sys
import cv2
import numpy as np
#import pytesseract

def fourPointsTransform(frame, vertices):
    vertices = np.asarray(vertices)
    outputSize = (100, 32)
    if vertices[0][0] < vertices[2][0] and vertices[0][1] > vertices[2][1]:
        targetVertices = np.array([
            [0, outputSize[1] - 1],
            [0, 0],
            [outputSize[0] - 1, 0],
            [outputSize[0] - 1, outputSize[1] - 1]], dtype="float32")
    else:
        targetVertices = np.array([
            [outputSize[0] - 1, outputSize[1] - 1],
            [0, outputSize[1] - 1],
            [0, 0],
            [outputSize[0] - 1, 0]],dtype="float32")
    #print("verticves=",vertices)
    #print("targetVertices",targetVertices)
    rotationMatrix = cv2.getPerspectiveTransform(vertices, targetVertices)
    result = cv2.warpPerspective(frame, rotationMatrix, outputSize)
    #print("result=",result.shape)
    return result

def decodeText(scores):
    text = ""
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"
    for i in range(scores.shape[0]):
        c = np.argmax(scores[i][0])
        if c != 0:
            text += alphabet[c - 1]
        else:
            text += '-'

    # adjacent same letters as well as background text must be removed to get the final output
    char_list = []
    for i in range(len(text)):
        if text[i] != '-' and (not (i > 0 and text[i] == text[i - 1])):
            char_list.append(text[i])
    return ''.join(char_list)

def display_lines(image, lines):
    line_image = np.zeros_like(image)
    if lines is not None:
        for line in lines:
            if line is not None:
                x1,y1,x2,y2 = line.reshape(4)
                if abs(x2-x1) < abs(y2-y1) :
                    cv2.line(line_image, (x1, y1), (x2, y2), (255,255,0), 1)
                else:
                    cv2.line(line_image, (x1, y1), (x2, y2), (0,255,255), 1)
    return line_image

recognizer = cv2.dnn.readNet('crnn.onnx')
tickmeter = cv2.TickMeter()

img = cv2.imread(str(sys.argv[1]))
gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
blur = cv2.GaussianBlur(gray,(5,5),0)
canny = cv2.Canny(blur,50,150)
cv2.imshow("canny", canny)
cv2.waitKey()
lines = cv2.HoughLinesP(canny, 2, np.pi/180, 100, np.array([]), minLineLength=40, maxLineGap=5)
img2 = display_lines(img, lines)
cv2.imshow("HoughLinesP", img2)
cv2.waitKey()
exit()
# Preprocessing the image starts

# Convert the image to gray scale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Performing OTSU threshold
ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)

# Specify structure shape and kernel size. 
# Kernel size increases or decreases the area 
# of the rectangle to be detected.
# A smaller value like (10, 10) will detect 
# each word instead of a sentence.
#rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))
print("w,h=",gray.shape[0],gray.shape[1])
rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))

# Applying dilation on the threshold image
dilation = cv2.dilate(thresh1, rect_kernel, iterations = 1)
cv2.imshow("dilation", dilation)
cv2.waitKey()

# Finding contours
contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, 
                                                 cv2.CHAIN_APPROX_NONE)

# Creating a copy of image
im2 = img.copy()

# Looping through the identified contours
# Then rectangular part is cropped and passed on
# to pytesseract for extracting text from it
# Extracted text is then written into the text file
for cnt in contours:
    x, y, w, h = cv2.boundingRect(cnt)
    #print(w,h)
    if w < 100 and h < 100:
        # Drawing a rectangle on copied image
        rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Cropping the text block for giving input to OCR
        cropped = im2[y:y + h, x:x + w]
        
        # Apply OCR on the cropped image
        #text = pytesseract.image_to_string(cropped)
        #print("text=",text)
        partcial = cv2.cvtColor(cropped, cv2.COLOR_RGB2GRAY)
        #print(partcial.shape)
        #cv2.imshow("Partcial1", partcial)
        vertices = np.float32([[w,h],[0,h],[0,0]
                               ,[w,0]])
        roi = fourPointsTransform(partcial, vertices)
        cv2.imshow("roi", roi)
        # Create a 4D blob from cropped image
        blob = cv2.dnn.blobFromImage(roi, size=(100, 32), mean=127.5, scalefactor=1 / 127.5)
        print(blob.shape)
        recognizer.setInput(blob)
        # Run the recognition model
        tickmeter.start()
        result = recognizer.forward()
        tickmeter.stop()
        #print(result)
        # decode the result into text
        wordRecognized = decodeText(result)
        print( wordRecognized )
        cv2.waitKey()


cv2.imshow("img2", im2)
cv2.waitKey()
