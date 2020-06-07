'''
@author ahmed hessuin
this file for detecting the arrows
'''
import cv2
import numpy as np
from utils import object_file


# ======================================================================================================================#
def interval_overlap(first_element_coordinate_min, first_element_coordinate_max,
                     second_element_coordinate_min, second_element_coordinate_max):
    '''
   description : this check if there is an intersection between 2 intervals as x1,x2 is the first interval and x3,x4 is
   the second interval
   :param first_element_coordinate_min: the first interval min value, type(int)
   :param first_element_coordinate_max: the first interval max value, type(int)
   :param second_element_coordinate_min: the second interval min value, type(int)
   :param second_element_coordinate_max: the second interval max value, type(int)
   :return: 1 if there is an intersection, 0 if there is no intersection ,type(int)
   '''
    x1 = first_element_coordinate_min
    x2 = first_element_coordinate_max  # we have interval a
    x3 = second_element_coordinate_min
    x4 = second_element_coordinate_max  # we have interval b

    # first interval     [        ]
    # second interval    (        )

    # [x3         x4]       (x1               x2)   --------> case 1

    # [x3         (x1         x4]             x2)   --------> case 2
    # [x3         (x1         x2)             x4]   --------> case 2

    # (x1          x2)      [x3                x4]  --------> case 3

    # (x1         [x3        x2)               x4]  --------> case 4
    # (x1         [x3        x4]               x2)  --------> case 4
    #

    # to make sure if we have overlap or no
    if x3 < x1:  # case 1 , case 2
        if x4 < x1:  # case 1
            return 0  # case 1 no overlap
        else:
            return min(x2, x4) - x1  # case 2 get the overlap [   ]
    else:  # case 3 , case 4
        if x2 < x3:  # case 3
            return 0  # no overlap
        else:  # case 4
            return min(x2, x4) - x3  # overlap [       ]
# ======================================================================================================================#
def get_line_type(width, height):
    '''
   description : getting the line type based on it's width and height
   :param width: width of the arrow , int
   :param height: height of the arrow, int
   :return: the type of this arrow, h-> horz, v-> vert , i-> incline
   '''
    threshold_value_for_horz_line = 25
    threshold_value_for_vert_line = 25

    if width > height and height < threshold_value_for_horz_line:
        return 'h'
    elif height > width and width < threshold_value_for_vert_line:
        return 'v'
    else:
        return 'i'
# ======================================================================================================================#
def get_line_type_for_line_array(x_min, y_min, x_max, y_max):
    '''
   description : this function get the type of the arrow based on it's 4 points
   :param x_min: arrow x min, int
   :param y_min: arrow y min, int
   :param x_max: arrow x max, int
   :param y_max: arrow y max, int
   :return:the type of the arrow, v-> vert, h-> horz, i-> incline
   '''
    if y_min > y_max:
        dumy = y_min
        y_min = y_max
        y_max = dumy

    if x_min > x_max:
        dumy = x_min
        x_min = x_max
        x_max = dumy

    if x_max - x_min > 25 and y_max - y_min < 25:
        return ("h")
    elif x_max - x_min < 25 and y_max - y_min > 25:
        return ("v")
    else:
        return ("i")
# ======================================================================================================================#
def line_detector(img):
    '''
   description : the main function of this file, detect the lines on given image and add it to the object file
   all object as dic
   :param img: input image , np.array
   :return: void
   '''
    ########################## variable section ##########################
    horz_copy = img.copy()  #
    vert_copy = img.copy()  #
    incline_copy = img.copy()  #
    green = [0, 255, 0]  #
    blue = [255, 0, 0]  #
    lower_blue = np.array([110, 50, 50])  #
    upper_blue = np.array([130, 255, 255])  #
    lower_green = np.array([36, 25, 25])  #
    upper_green = np.array([70, 255, 255])  #
    min_len = 80  #
    thrshold = 100  #
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  #
    edges = cv2.bitwise_not(gray)  # no canny , to get thick lines          #
    ######################################################################

    ############################################## predict straight and incline lines ######################
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=thrshold, maxLineGap=5, minLineLength=min_len)  #
    line_array = []  #
    for line in lines:  #
        x1, y1, x2, y2 = line[0]  #
        line_array.append([x1, y1, x2, y2])  #
    ########################################################################################################

    ########## get type of each line and mark it on the image##########
    for line in line_array:  #
        x1, y1, x2, y2 = line  #
        type_dump = get_line_type_for_line_array(x1, y1, x2, y2)  #
        if type_dump == "i":  #
            cv2.line(incline_copy, (x1, y1), (x2, y2), green, 3)  #
        else:  #
            if type_dump == 'h':  #
                cv2.line(horz_copy, (x1, y1), (x2, y2), blue, 3)  #
            if type_dump == 'v':  #
                cv2.line(vert_copy, (x1, y1), (x2, y2), blue, 3)  #
    ###################################################################

    ######### get the lines only from the image ##########################
    hsv_vert = cv2.cvtColor(vert_copy, cv2.COLOR_BGR2HSV)                #
    hsv_horz = cv2.cvtColor(horz_copy, cv2.COLOR_BGR2HSV)                #
    hsv_incline = cv2.cvtColor(incline_copy, cv2.COLOR_BGR2HSV)          #
    mask_incline = cv2.inRange(hsv_incline, lower_green, upper_green)    #
    mask_vert = cv2.inRange(hsv_vert, lower_blue, upper_blue)            #
    mask_horz = cv2.inRange(hsv_horz, lower_blue, upper_blue)            #
    ######################################################################


    # get contours of  H lines
    contours, hierarchy = cv2.findContours(mask_horz, cv2.RETR_EXTERNAL,
                                           cv2.CHAIN_APPROX_NONE)  # find the contours  of every object not inside another object
    cnt_area_threshold = 20  # to remove noise
    for cnt in contours:  # for every contour
        [x, y, w, h] = cv2.boundingRect(cnt)  # get the contour width and heightmmmm
        area = w * h
        if area < cnt_area_threshold:
            continue
        type = get_line_type(w, h)
        width_tolerance = 10
        height_tolerance = 10
        extra_tolerance_for_horz = 5
        if type == 'h':
            x = x - (width_tolerance + extra_tolerance_for_horz)
            w = w + (width_tolerance + extra_tolerance_for_horz) * 2  # *2 because the negative tolerance in x
            y = y - height_tolerance
            h = h + height_tolerance * 2  # *2 because the negative tolerance in y
        object_file.all_objects_as_dic['straight arrow'].append(
            object_file.DC.Data('straight arrow',
                                x, y,
                                x + w, y + h,
                                str("0.9"), object_file.object_id))  # insert the anchor in the dictionary
        object_file.object_id = object_file.object_id + 1
    # ============================================================================================================#

    # get contours of the V lines
    contours, hierarchy = cv2.findContours(mask_vert, cv2.RETR_EXTERNAL,
                                           cv2.CHAIN_APPROX_NONE)  # find the contours  of every object not inside another object

    cnt_area_threshold = 20
    for cnt in contours:  # for every contour
        [x, y, w, h] = cv2.boundingRect(cnt)  # get the contour width and heightmmmm
        area = w * h
        if area < cnt_area_threshold:
            continue
        type = get_line_type(w, h)
        width_tolerance = 10
        height_tolerance = 10
        extra_tolerance_for_horz = 5
        if type == 'v':
            x = x - width_tolerance
            w = w + width_tolerance * 2  # *2 because the negative tolerance in x
            y = y - height_tolerance
            h = h + height_tolerance * 2  # *2 because the negative tolerance in y
        object_file.all_objects_as_dic['straight arrow'].append(
            object_file.DC.Data('straight arrow',
                                x, y,
                                x + w, y + h,
                                str("0.9"), object_file.object_id))  # insert the anchor in the dictionary
        object_file.object_id = object_file.object_id + 1
    # =========================================================================================================#

    # get contours for incline and cross lines
    contours, hierarchy = cv2.findContours(mask_incline, cv2.RETR_EXTERNAL,
                                           cv2.CHAIN_APPROX_NONE)  # find the contours  of every object not inside another object
    # ---------------------------#
    for cnt in contours:  # for every contour
        [x, y, w, h] = cv2.boundingRect(cnt)  # get the contour width and heightmmmm
        area = w * h
        incline_arrow_ratio_theshold = 0.5
        if area < cnt_area_threshold:
            continue

        if h < incline_arrow_ratio_theshold * w or w < incline_arrow_ratio_theshold * h:
            # this is for noise on curved arrow
            continue

        object_file.all_objects_as_dic['incline arrow'].append(
            object_file.DC.Data('incline arrow',
                                x, y,
                                x + w, y + h,
                                str("0.9"), object_file.object_id))  # insert the anchor in the dictionary
        object_file.object_id = object_file.object_id + 1
# ======================================================================================================================#
