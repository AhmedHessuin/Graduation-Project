'''
@author ahmed hessuin
description : this file is for operation on image.
'''
from cv2 import rectangle
from utils import object_file
from cv2 import imwrite
from utils import log_config
from utils import matching
import numpy as np
import cv2
#======================================================================================================================#
def draw_incline_line(image,point1_x,point1_y,point2_x,point2_y):
    tolerance_in_x=40
    point1_x=int(point1_x-tolerance_in_x/2)
    point2_x=int(point2_x-tolerance_in_x/2)
    point3_x=int(point1_x+tolerance_in_x)
    point3_y=int(point1_y)
    point4_x=int(point2_x+tolerance_in_x)
    point4_y=int(point2_y)
    cv2.line(image,pt1=(point1_x,point1_y),pt2=(point3_x,point3_y),thickness=3,color=[27, 189, 255])
    cv2.line(image, pt1=(point2_x, point2_y), pt2=(point4_x, point4_y), thickness=3, color=[27, 189, 255])
    cv2.line(image, pt1=(point1_x, point1_y), pt2=(point2_x, point2_y), thickness=3, color=[27, 189, 255])
    cv2.line(image, pt1=(point3_x, point3_y), pt2=(point4_x, point4_y), thickness=3, color=[27, 189, 255])


#======================================================================================================================#
def get_image():
    '''
    description : get the original image use it before any draw on the image
    :return void
    '''
    object_file.image=object_file.image_copy.copy()
#======================================================================================================================#
def draw_elements():
    '''
    description : draw all elements predicted and added or removed on the image
    by searching in all object dictionary elements and draw them
    :return: void
    '''
    headers_in_reverse = []
    for header in object_file.all_objects_as_dic:
        headers_in_reverse.insert(0, header)

    for header in headers_in_reverse:# for every header(key) in the dictionary
        #for element in range(len(object_file.all_objects_as_dic[header])):# for every element  in this list
        draw_on_image(object_file.image, object_file.all_objects_as_dic[header])# draw this element on the image
#======================================================================================================================#
def draw_on_image(image,boxes):
    '''
    description: take and image and boxes list, then draw rectangle on the image based on
    the xmin, xmax, ymin ,ymax and color the rectangle depend on the label

    :param image: an image , np array
    :param boxes: an input list of boxes ,type Data, defined in data_class.py
    :return: void
    '''
    color=[1,2,3]
    #============ set color for every label ===========#
    for box in boxes:
        thickness=2 #default value
        if (box.get_label()) == ("state"):
            color = [217, 89, 80]
        elif (box.get_label()) == ("/"):
            color = [0, 255, 0]
            thickness = 1
        elif (box.get_label()) == ("loop back arrow"):
            color = [255, 0, 255]
        elif (box.get_label()) == ("state condition"):
            color = [50, 0, 255]
        elif (box.get_label()) == ("arrow head"):
            color = [249, 223, 64]
        elif (box.get_label()) == ("straight arrow") or (box.get_label()) == ("curved arrow"):
            color = [27, 189, 255]
        elif (box.get_label()) == ("incline arrow"):
            color=[27, 189, 255]

        else:
            color = [166, 73, 36]  # this is for text and numbers
            thickness = 1


        #===============================================#
        if box.get_label()==("incline arrow"):

            draw_incline_line(image=image,point1_x=box.get_xmin(),point1_y=box.get_ymin(),
                              point2_x=box.get_xmax(),point2_y=box.get_ymax())
        else:
            rectangle(img=image, pt1=(box.get_xmin(), box.get_ymin()), pt2=(box.get_xmax(), box.get_ymax()), color=color, thickness=thickness)  # rectangle format
            if box.get_name()=="0" or box.get_name()=="1" or box.get_name()=="2" or box.get_name()=="3" or \
                    box.get_name() == "4" or box.get_name()=="5" or  box.get_name()=="6" or  box.get_name()=="7" or \
                    box.get_name() == "8" or box.get_name()=="9" or box.get_name()[0]=="g": #box.get_name()[0]=="g":  this condition for generated ids
                text_color=color
                cv2.putText(image,box.get_name(),(box.get_xmin(),box.get_ymax())
                            ,cv2.FONT_HERSHEY_SIMPLEX,1,text_color,2,cv2.LINE_4)

    #========================================#
#======================================================================================================================#
def get_element_with_x_and_y(x_input,y_input):
    '''
    description : return any element has (x_input,y_input) inside of it, if there are many objects
    share this x and y, remove the smallest area.

    :param x_input: x dimension of a point
    :param y_input: y dimension of a point
    :return: string of the element name or "didn't find anything", header,type(string), element,type(Data)
    '''

    element_name=""
    area=1920000 # a very large area as initialization value
    remove_header="" # header of the removed element
    remove_element=None # index of the removed element
    for header in object_file.all_objects_as_dic.keys():
        for element in object_file.all_objects_as_dic[header]:
            if element.get_xmin() < int(x_input) and \
             element.get_xmax()>int(x_input) and\
             element.get_ymin()<int(y_input) and\
             element.get_ymax()>int(y_input) and header != "incline arrow":
                element_width=element.get_xmax()-element.get_xmin()
                element_height=element.get_ymax()-element.get_ymin()
                element_area=element_width*element_height
                if element_area < area:  # mark this element
                    element_name = element.get_name()  # get the name
                    area = element_area  # update the area
                    remove_header = header  # mark the header
                    remove_element = element  # mark the element
            if header=="incline arrow":
                dumb_element=object_file.DC.Data("state condition",x_input,y_input,x_input+10,y_input+10,"90")
                element_area=matching.area_of_intersection_with_incline_arrow(dumb_element,element)
                if element_area==0:
                    continue
                if element_area < area:  # mark this element
                    element_name = element.get_name()  # get the name
                    area = element_area  # update the area
                    remove_header = header  # mark the header
                    remove_element = element  # mark the element




    if remove_element==None:
        return "didn't find anything to remove",remove_header,remove_element

    return element_name,remove_header,remove_element
    #--------------------------------------------#
#======================================================================================================================#
def remove_element(remove_header,remove_element):
    '''
    description : remove element from a given header, taking it's header name and the element type

    :param remove_header : the name of the dictionary key, string
    :param remove_element: the element to remove from the dictionary
    :return: text " removed "+ the element that was removed
    '''

    element_name=remove_element.get_name()
    object_file.all_objects_as_dic[remove_header].remove(remove_element)  # remove this anchor from my anchor dictionary

    update_image()

    return log_config.start_of_log()+"removed " + element_name+log_config.end_of_log()
    #--------------------------------------------#
#======================================================================================================================#
def add_element(x_min,y_min,x_max,y_max,name,accuracy="100%"):
    '''
    description : add element of label(name), defined by 2 points
    draw the rectangle on the image based on p1 and p2
    add this element to xml file

    :param x_min: point 1 xmin
    :param y_min: point 1 ymin
    :param x_max: point 2 xmax
    :param y_max: point 2 ymax
    :param name: label name
    :param accuracy: accuracy optional
    :return: text "added +" the name of the label
    '''
    # adding this anchor
    if str(name)=="incline arrow":
        if x_min>x_max:
            x_min,x_max=x_max,x_min
            y_min,y_max=y_max,y_min


    object_file.all_objects_as_dic[str(name)].append(object_file.DC.Data(str(name),str(x_min),str(y_min),str(x_max),str(y_max),str(accuracy),object_file.object_id))
    #update the object id
    object_file.object_id=object_file.object_id+1
    update_image()
    return log_config.start_of_log()+"added "+ name+log_config.end_of_log()
#======================================================================================================================#
def undo_element():
    '''
    under development
    :return:text " undo completed "
    '''
    if len(object_file.undo_all_objects)>0:
        object_file.all_objects.append(object_file.undo_all_objects.pop())

    get_image()
    draw_elements()
    return ("undo completed")
#======================================================================================================================#
def export_image():
    '''
    description : write on the hard disk the output image based on the
    output path

    :return: void
    '''
    imwrite(object_file.output_path, np.uint8(object_file.image))
#======================================================================================================================#
def set_output_path(new_output_path):
    '''
    description: set the output path of the exported image

    :param new_output_path: set the output path of the output image
    :return: void
    '''
    object_file.output_path=new_output_path
#======================================================================================================================#
def update_image():
    '''
    description : update the image by redrawing
    :return: void
    '''
    get_image()
    draw_elements()
#======================================================================================================================#
def set_anchors_to_display_image_1600_1200():
    '''
    description : for better display change the image size to be 1600x1200 thus, change also all
    anchors value to the new image size
    :return: void
    '''

    train_size=800
    height,width,depth=object_file.image.shape
    height_ratio=height/train_size
    width_ratio=width/train_size
    for key in object_file.all_objects_as_dic.keys():
        if key=="arrow head" or key=="straight arrow"or key=="incline arrow":
            #the arrow head use 1600 1200 image not 800*800
            continue
        for anchor in object_file.all_objects_as_dic[key]:
            anchor.xmin=int(int(anchor.xmin)*width_ratio )
            anchor.xmax=int(int(anchor.xmax)*width_ratio )
            anchor.ymin=int(int(anchor.ymin)*height_ratio)
            anchor.ymax=int(int(anchor.ymax)*height_ratio)


def set_anchor_to_original_image(xmin,ymin,xmax,ymax):
    '''
    description : change the anchor dimension to the original image this is helpful in
    anchor sub file to get the state condition from the original image with high pixel value
    :param xmin: anchor x min , int
    :param ymin: anchor y min , int
    :param xmax: anchor x max , int
    :param ymax: anchor y max , int
    :return: new x min , y min , x max and y max based on the original image
    '''
    height,width,depth=object_file.original_image.shape
    train_image_x=1600
    train_image_y=1200
    height_ratio = height / train_image_y
    width_ratio = width / train_image_x

    xmin_new=int(xmin*width_ratio)
    xmax_new=int(xmax*width_ratio)
    ymin_new=int(ymin*height_ratio)
    ymax_new=int(ymax*height_ratio)
    return xmin_new,ymin_new,xmax_new,ymax_new

