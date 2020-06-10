#! /usr/bin/env python
'''
@author ahmed hessuin
description : predict file core file for prediction on the given image
'''
#commented by ibrahiem amr / ahmed hessuin
import numpy as np
import cv2
from utils.utils import get_yolo_boxes
from utils.bbox import config_boxes
from keras.models import load_model as load_model_1
from keras.models import load_model as load_model_2
from keras.models import load_model as load_model_3
from utils import log_config
from utils   import  matching
import transactionToVerilog
from keras.models import load_model as load_model_4
from keras.models import load_model as load_model_5
from utils import image_operations
from utils import object_file
from  utils import  xml_creator
import image_preprocess
import line_detector
from utils import matching
#============================= warning remover =========================================#
import warnings
from tensorflow.python.util import deprecation
deprecation._PRINT_DEPRECATION_WARNINGS = False

import tensorflow as tf
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

warnings.filterwarnings('ignore')
tf.get_logger().setLevel('INFO')

try:
    from tensorflow.python.util import module_wrapper as deprecation
except ImportError:
    from tensorflow.python.util import deprecation_wrapper as deprecation
deprecation._PER_MODULE_WARNING_LIMIT = 0
#======================================================================================================================#
def set_inputpath_and_image(image,input_path):
    '''
    description : set the input path in object file and the image in object file for future use
    :param image: input image, np array
    :param input_path: input path, text (str)
    :return: void
    '''
    object_file.image = image.copy()  # set the image
    object_file.image_copy= image.copy()
    object_file.input_path=input_path # set the image path
#======================================================================================================================#
def reset_object_file():
    '''
    description : this function for predict function to reset the object parameter for multi input image
    :return: void
    '''
    object_file.all_objects_as_dic={"/": [], "0": [], "1": [], "2": [], "3": [], "4": [], "5": [], "6": [], "7": [], "8": [], "9": [],"arrow head": [], "state condition": [], "loop back arrow": [], "state": [], "straight arrow": [],"incline arrow":[],"curved arrow":[]}
    object_file.object_id = 0
#======================================================================================================================#
def first_step_config():
    '''
    description : first step configuration , loading the infer models
    :return: void
    '''
    ###############################
    #   Load the model
    ###############################
    os.environ['CUDA_VISIBLE_DEVICES'] = "0" # use the gpu bus

    # ============================== use infer model ===========================#

    ###################################load infer model ##############################
    object_file.model_1 = load_model_1("weights/all_in_one.h5")                      #
    object_file.model_2 = load_model_1("weights/state_condition_and_slash.h5")       #
    object_file.model_3 = load_model_3("weights/arrow_head.h5")                      #
    object_file.model_4 = load_model_4("weights/arrows.h5")                          #
    ##################################################################################
#======================================================================================================================#
def clean_straight_arrow_with_other_arrows_or_state():
    '''
    description: clean the image from  noisy straight arrows, like predicted arrows on the arc of circle
    :return: void
    '''
    threshold=60/100
    nothing_to_remove=True
    while(nothing_to_remove==True):
        nothing_to_remove=False
        for element in object_file.all_objects_as_dic["straight arrow"]:
            element_area=matching.get_anchor_area(element)
            threshold_area=threshold*element_area

            for second_element in object_file.all_objects_as_dic["curved arrow"]:
                if matching.area_of_intersection(element,second_element)>threshold_area:
                    try:
                        object_file.all_objects_as_dic["straight arrow"].remove(element)
                        nothing_to_remove = True
                    except:
                        continue
            for second_element in object_file.all_objects_as_dic["loop back arrow"]:
                if matching.area_of_intersection(element, second_element) > threshold_area:
                    try:
                        nothing_to_remove = True
                        object_file.all_objects_as_dic["straight arrow"].remove(element)
                    except:
                        continue
            for second_element in object_file.all_objects_as_dic["state"]:
                if matching.area_of_intersection(element, second_element) > threshold_area:
                    try:
                        object_file.all_objects_as_dic["straight arrow"].remove(element)
                        nothing_to_remove = True
                    except:
                        continue

def clean_incline_arrow_with_state():
    threshold = 90 / 100
    nothing_to_remove = True
    while (nothing_to_remove == True):
        nothing_to_remove = False
        for element in object_file.all_objects_as_dic["incline arrow"]:
            element_area = matching.get_anchor_area(element)
            threshold_area = threshold * element_area


            for second_element in object_file.all_objects_as_dic["state"]:
                if matching.area_of_intersection(element, second_element) > threshold_area:
                    try:
                        object_file.all_objects_as_dic["incline arrow"].remove(element)
                        nothing_to_remove = True
                    except:
                        continue


#======================================================================================================================#
#==================================================== main ============================================================#
def _main_(input_path_x,infer_model,infer_model_2,infer_model_3,infer_model_4,infer_model_5):
    '''
    description : main function for predict the anchors on the image using the infer models and anchors of yolo v3 for this labels


    :param input_path_x:the input path of the image , text (str)
    :param infer_model: infer model 1, .h5
    :param infer_model_2:infer model 2, .h5
    :param infer_model_3:infer model 3, .h5
    :param infer_model_4:infer model 4, .h5
    :return:void
    '''
    input_path   = input_path_x # get the input path from the args
    ###############################
    #   Set some parameter
    ###############################
    net_h, net_w = 416, 416 # a multiple of 32, the smaller the faster 416, 416
    obj_thresh, nms_thresh = 0.90, .3  #obj_thresh = .5 mean if less than 50% sure ignore it, nms_thresh =.3 means if 30 % IOU for 2 boxes; merge them


    #===========================================================================#
    ###############################
    #   Predict bounding boxes
    ###############################
    #============================================ for video ===========================================================#

    #==================================================================================================================#
    #============================================ for image ===========================================================#
    if True: # do detection on an image or a set of images
        image_paths = []
        #==================================== image path ==============================================================#
        if os.path.isdir(input_path):
            for inp_file in os.listdir(input_path): # get the input image
                image_paths += [input_path + inp_file] # get the input image
        else:
            image_paths += [input_path] # relative address

        image_paths = [inp_file for inp_file in image_paths if (inp_file[-4:] in ['.jpg', '.png', 'JPEG'])]#image format
        #==============================================================================================================#


        ############################# anchors intialiazation ############################################
        model_1_anchors = [13, 17, 17, 14, 17, 19, 22, 28, 27, 12, 27, 18, 28, 37, 35, 52, 48, 74]      #
        model_2_anchors=[4,13, 5,14, 6,12, 6,16, 20,25, 22,21, 27,15, 31,25, 35,17]                     #
        model_3_anchors=[55,69, 75,234, 133,240, 136,129, 142,363, 203,290, 228,184, 285,359, 341,260]  #
        model_4_anchors=[55,69, 75,234, 133,240, 136,129, 142,363, 203,290, 228,184, 285,359, 341,260]  #
        #################################################################################################

        ################################## labels intialiazation ######################################
        model_1_label = ["loop back arrow", "state", "state condition"]                               #
        model_2_label = ["/"]                                                                         #
        model_3_label=["arrow head"]                                                                  #
        model_4_label=["curved arrow"]                                                                #
        ###############################################################################################

        ############################################ the main loop ################################################################

        for image_path in image_paths:
            ########################################## image preprocess #############################
            image = cv2.imread(image_path)# load the image path                                     #
            #image=image_preprocess.resize_image_less_than_600_800(image)                            #
            object_file.original_image=cv2.imread(image_path) # set the original image              #
            image=image_preprocess.start_pre(image,condition=object_file.hand_written)              #                    #
            line_detector.line_detector(image)                                                      #
            #########################################################################################

            ########################################## predict the bounding boxes ##################################################
            boxes = get_yolo_boxes(infer_model, [image], net_h, net_w, model_1_anchors, obj_thresh, nms_thresh)[0]                 #
            boxes_2=get_yolo_boxes(infer_model_2, [image], net_h, net_w, model_2_anchors, obj_thresh, nms_thresh)[0]               #
            boxes_3 =get_yolo_boxes(infer_model_3, [image], net_h, net_w, model_3_anchors, obj_thresh, nms_thresh)[0] #
            boxes_4 =get_yolo_boxes(infer_model_4, [image], net_h, net_w, model_4_anchors, obj_thresh, nms_thresh)[0]              #                                                                                                                 #
            ########################################################################################################################                                                                                                                     #




            ######################## draw boxes after predict ########
            config_boxes(image, boxes, model_1_label, obj_thresh)    #
            config_boxes(image, boxes_2, model_2_label, obj_thresh)  #
            config_boxes(image, boxes_3, model_3_label, obj_thresh)  #
            config_boxes(image, boxes_4, model_4_label, obj_thresh)  #
            ##########################################################

            ######################### set the exported path ######################
            set_inputpath_and_image(image,image_path)                    #
            ######################################################################
#======================================================================================================================#
def predict_main(input_path):
    '''
    description : this function is main function, the GUI call it and it's predict the anchors and draw on the image
    :param input_path: the image input path, text(str)
    :return: string "predict"
    '''
    image_path = input_path
    _main_(image_path,object_file.model_1,object_file.model_2,object_file.model_3,object_file.model_4,object_file.model_5) # call the main
    #=====================================================================#
    #image_operations.set_anchors_to_display_image_1600_1200()
    clean_straight_arrow_with_other_arrows_or_state()
    clean_incline_arrow_with_state()
    image_operations.update_image()
    #---------------------------------------------------------------------#
    return log_config.start_of_log()+"predict done"+log_config.end_of_log()
#======================================================================================================================#
if __name__ == '__main__':
    reset_object_file()
    first_step_config()

    print(log_config.start_of_log(),log_config.start_up_log())
    print(predict_main("Slide5.png"))
    xml_creator.xml_output_path("test.xml")
    image_operations.set_output_path("predicted.png")
    image_operations.export_image()
    matching.connect_anchors()
    passed, text, img =matching.connect_transactions()
    print(text)
    transactionToVerilog.transactionToVerilog("Moudel_0",object_file.transaction)
    enter=input("Enter any button to close")
