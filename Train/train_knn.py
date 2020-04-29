'''
modified file 
'''
__author__ = 'ahmed hessuin'

import sys
import numpy as np
import cv2

def preprocessing_handwritten(im,min_area=20):
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    ret,thresh = cv2.threshold(gray,127,255,cv2.THRESH_BINARY_INV)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    print("o")
    cv2.imshow("thres",thresh)
    cv2.waitKey()
    #==================== sort =================#
    for cnt in contours:
        if cv2.contourArea(cnt)<min_area :
            [x, y, w, h] = cv2.boundingRect(cnt)
            thresh[y:y+h,x:x+w]=[0]
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4))
    thresh=cv2.dilate(thresh,kernel=kernel,iterations=1)
    thresh=cv2.bitwise_not(thresh)
    return thresh




train_list=[1,2,3,4,5,6,7,8,9,-1]



samples = np.empty((0, 900), np.float32)
responses = []
for i in range(12):
    im = cv2.imread('../data/'+str(i)+'.png')
    im3 = im.copy()
    append_value=(i)
    if i==10 or i ==11:
        append_value=-1
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    ret, thresh = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)

    #################      Now finding Contours         ###################

    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    keys = [i for i in range(48, 58)]

    contours = sorted(contours, key=lambda ctr: cv2.boundingRect(ctr)[0])
    for cnt in contours:

        if cv2.contourArea(cnt) > 1:
            [x, y, w, h] = cv2.boundingRect(cnt)

            if h > 10:

                cv2.rectangle(im, (x, y), (x + w, y + h), (0, 0, 255), 2)
                roi = thresh[y:y + h, x:x + w]
                roismall = cv2.resize(roi, (30, 30))
                cv2.imshow("ros",roismall)
                cv2.waitKey()



                print(i)
                responses.append(int(append_value))
                sample = roismall.reshape((1, 900))
                samples = np.append(samples, sample, 0)
    cv2.imshow('norm2', im)
    cv2.waitKey()

responses = np.array(responses, np.float32)
responses = responses.reshape((responses.size, 1))
print ("training complete")

samples = np.float32(samples)
responses = np.float32(responses)


np.savetxt('../data/generalsamples3.data', samples)
np.savetxt('../data/generalresponses3.data', responses)
model = cv2.ml.KNearest_create()

# samples=np.append(samples,samples2)
# responses=np.append(responses,responses2)
model=cv2.ml.KNearest_load("../data/model_3.text")
model.train(samples, cv2.ml.ROW_SAMPLE, responses)

#model.train(samples2, cv2.ml.ROW_SAMPLE, responses2)

cv2.Algorithm.save(model,"model_7.text")
