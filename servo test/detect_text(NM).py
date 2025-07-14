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

erc1 = cv2.text.loadClassifierNM1('./trained_classifierNM1.xml')
er1 = cv2.text.createERFilterNM1(erc1)

erc2 = cv2.text.loadClassifierNM2('./trained_classifierNM2.xml')
er2 = cv2.text.createERFilterNM2(erc2)

regions = cv2.text.detectRegions(gray,er1,er2)
print(len(regions))
rects = [cv2.boundingRect(p.reshape(-1, 1, 2)) for p in regions]
for rect in rects:
    if 15 < rect[2] < 100 and 15 < rect[3] < 40:
        print( rect)
        #cv2.rectangle(img, rect[0:2], (rect[0]+rect[2],rect[1]+rect[3]), (0, 0, 0), 2)
        partcial = img[rect[1]:rect[1]+rect[3], rect[0]:rect[0]+rect[2]]
        cv2.imshow("partcial", partcial)
        cv2.waitKey()
for rect in rects:
    cv2.rectangle(img, rect[0:2], (rect[0]+rect[2],rect[1]+rect[3]), (255, 255, 255), 1)
cv2.imshow("Text detection result", img)
cv2.waitKey()

