import sys
import cv2
import numpy as np

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


recognizer = cv2.dnn.readNet('crnn.onnx')
tickmeter = cv2.TickMeter()

img = cv2.imread(str(sys.argv[1]))
gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

textSpotter = cv2.text.TextDetectorCNN_create("textbox.prototxt", "TextBoxes_icdar13.caffemodel")
rects, outProbs = textSpotter.detect(img)
print(rects, outProbs)
vis = img.copy()
thres = 0.1
for r in range(np.shape(rects)[0]):
    if outProbs[r] > thres:
        rect = rects[r]
        cv2.rectangle(vis, (rect[0],rect[1]), (rect[0] + rect[2], rect[1] + rect[3]), (255, 0, 0), 2)
        partcial = img[rect[1]:rect[1]+rect[3], rect[0]:rect[0]+rect[2]]
        partcial = cv2.cvtColor(partcial, cv2.COLOR_RGB2GRAY)
        print(partcial.shape)
        #cv2.imshow("Partcial1", partcial)
        vertices = np.float32([[rect[2],rect[3]],[0,rect[3]],[0,0]
                               ,[rect[2],0]])
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
        
cv2.imshow("Text detection result", vis)
cv2.waitKey()
