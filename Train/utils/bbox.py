#commented by ahmed hessuin / ibrahiem amr
import numpy as np
import os
import cv2
from .colors import get_color
import xml.etree.cElementTree as ET
class BoundBox:
    #the bound box class
    def __init__(self, xmin, ymin, xmax, ymax, c = None, classes = None):
        self.xmin = xmin#xmin
        self.ymin = ymin#ymin
        self.xmax = xmax#xmax
        self.ymax = ymax#ymax
        
        self.c       = c#defult = none
        self.classes = classes#classes

        self.label = -1#label =-1
        self.score = -1#label =-1

    def get_label(self):
        if self.label == -1:#if there is no label
            self.label = np.argmax(self.classes)#get argmax of classes
        
        return self.label#return the label
    
    def get_score(self):
        if self.score == -1:#if the score =-1
            self.score = self.classes[self.get_label()]#get the classes[label]
            
        return self.score      #return the score

#============================================== interval overlap ======================================================#
def _interval_overlap(interval_a, interval_b):
    x1, x2 = interval_a # we have interval a
    x3, x4 = interval_b # we have interval b


    #interval a = x
    #interval b = o


    #  x3         x4         x1               x2   --------> case 1

    #  x3         [x1         x4]               x2 --------> case 2
    #  x3         [x1         x2]               x4 --------> case 2

    #  x1          x2        x3               x4   --------> case 3

    #  x1         [x3        x2]               x4  --------> case 4
    #  x1         [x3        x4]               x2  --------> case 4
    #


    #to make sure if we have overlap or no
    if x3 < x1: # case 1 , case 2
        if x4 < x1:#case 1
            return 0 #case 1 no overlap
        else:
            return min(x2,x4) - x1 #case 2 get the overlap [   ]
    else:# case 3 , case 4
        if x2 < x3:#case 3
             return 0#no overlap
        else:#case 4
            return min(x2,x4) - x3 #overlap [       ]
#======================================================================================================================#


#===========================================intersection over union ===================================================#
def bbox_iou(box1, box2):
    intersect_w = _interval_overlap([box1.xmin, box1.xmax], [box2.xmin, box2.xmax])#get the intersected W
    intersect_h = _interval_overlap([box1.ymin, box1.ymax], [box2.ymin, box2.ymax])#get the intersected H
                    #--------------------------------------------------------------#
    intersect = intersect_w * intersect_h# intersected area
                    #--------------------------------------------------------------#
    w1, h1 = box1.xmax-box1.xmin, box1.ymax-box1.ymin # w1 , h1
    w2, h2 = box2.xmax-box2.xmin, box2.ymax-box2.ymin # w2 , h2
    
    union = w1*h1 + w2*h2 - intersect # the total area common (union)
    if intersect==0:#if intersected ==0 is a special condtion we made to solve issue in the code done by ahmed hessuin
        return 0#retun 0
    return float(intersect) / union # return the intersected area over the union area
#======================================================================================================================#



#============================================== draw boxes ============================================================#
def draw_boxes(image, boxes, labels, obj_thresh, quiet=True):
    # draw the box with cv2 function rectangle
    for box in boxes:
        label_str = ''
        label = -1
        for i in range(len(labels)):
            if box.classes[i] > obj_thresh:
                if label_str != '': label_str += ', '
                label_str += (labels[i] + ' ' + str(round(box.get_score()*100, 2)) + '%')
                label = i
            if not quiet: print(label_str)
                
        if label >= 0:
            text_size = cv2.getTextSize(label_str, cv2.FONT_HERSHEY_SIMPLEX, 1.1e-3 * image.shape[0], 5)
            width, height = text_size[0][0], text_size[0][1]
            region = np.array([[box.xmin-3,        box.ymin], 
                               [box.xmin-3,        box.ymin-height-26], 
                               [box.xmin+width+13, box.ymin-height-26], 
                               [box.xmin+width+13, box.ymin]], dtype='int32')  
            print('x min = ',box.xmin,',x max = ',box.xmax,',y min = ',box.ymin,'y max = ',box.ymax,'class = ',label_str)
            cv2.rectangle(img=image, pt1=(box.xmin,box.ymin), pt2=(box.xmax,box.ymax), color=get_color(label), thickness=2)#rectangle format

            cv2.putText(img=image, 
                        text=label_str,
                        org=(box.xmin+13, box.ymin - 13), 
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX, 
                        fontScale=1e-3 * image.shape[0], 
                        color=(0,0,0), 
                        thickness=1)# text format
        
    return image          