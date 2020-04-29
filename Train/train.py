#! /usr/bin/env python
# commented by ahmed hessuin / ibrahiem amr
import argparse
import os
import numpy as np
import json
from voc import parse_voc_annotation
from yolo import create_yolov3_model, dummy_loss
from generator import BatchGenerator
from utils.utils import normalize, evaluate, makedirs
from keras.callbacks import EarlyStopping, ReduceLROnPlateau
from keras.optimizers import Adam
from callbacks import CustomModelCheckpoint, CustomTensorBoard
from utils.multi_gpu_model import multi_gpu_model
import tensorflow as tf
import keras
from keras.models import load_model


#====================== creating the training instances ===============================================================#
def create_training_instances(
    train_annot_folder,#this will go to voc
    train_image_folder,#this will go to voc
    train_cache,#this will go to voc
    valid_annot_folder,#this will go to voc
    valid_image_folder,#this will go to voc
    valid_cache,#this will go to voc
    labels,#this is the output of voc
):

    #======================================= the voc call for training data ===========================================#
    # parse annotations of the training set
    train_ints, train_labels = parse_voc_annotation(train_annot_folder, train_image_folder, train_cache, labels)
    #as the voc return total number of insts and the seen labels (see voc comments)
    #==================================================================================================================#

    #======================================= the voc call for the valid data ==========================================#
    # parse annotations of the validation set, if any, otherwise split the training set
    if os.path.exists(valid_annot_folder):#check if there is a path for valid or no ?
        #path exist
        valid_ints, valid_labels = parse_voc_annotation(valid_annot_folder, valid_image_folder, valid_cache, labels)
        #call the voc to get the labels and ints from the data
    else:
        #path doesn't exist
        print("valid_annot_folder not exists. Spliting the trainining set.")# notify that there is no folder for validation
        #=================================== no valid data behavior ===================================================#
        train_valid_split = int(0.8*len(train_ints))#split the data as 80% for training and 20% for validation
        np.random.seed(0)#make it random (random seed mean that the random value will be the same everytime it runs)
        np.random.shuffle(train_ints)#shuffle the data to increase the random and robust the module
        np.random.seed()#ranodm seed again

        valid_ints = train_ints[train_valid_split:]#now get the valid ints from some of the train ints
        train_ints = train_ints[:train_valid_split]#train ints is the remaining data
        #==============================================================================================================#
    #==================================================================================================================#

    #===============================================error handling for config =========================================#
    # compare the seen labels with the given labels in config.json
    #if there is labels
    if len(labels) > 0:
        overlap_labels = set(labels).intersection(set(train_labels.keys()))#get the labels from the config file
            #=====================================================================================#
        print('Seen labels: \t'  + str(train_labels) + '\n')#print the seen labels from the voc
        print('Given labels: \t' + str(labels))#print the given labels from the config
            #=====================================================================================#
        # return None, None, None if some given label is not in the data set
        if len(overlap_labels) < len(labels):#ther eis an error some labels in config not found in voc
            print('Some labels have no annotations! Please revise the list of labels in the config.json.')
            return None, None, None#return none none none stop the training there is an error
    #------------------------------------------------------------------------------------------------------------------#
    else:#there is no labels
        print('No labels are provided. Train on all seen labels.')
        print(train_labels)
        labels = train_labels.keys() #train on the seen labels from the voc
    #==================================================================================================================#
    max_box_per_image = max([len(inst['object']) for inst in (train_ints + valid_ints)])
    #get the max number of boxes we can get from an image
    #==================================================================================================================#
    return train_ints, valid_ints, sorted(labels), max_box_per_image
    #good job we are done now return the train ints and valid ints , sorted labels and max number of boxees we can get
#======================================================================================================================#


#=================================================== call backs =======================================================#
def create_callbacks(saved_weights_name, tensorboard_logs, model_to_save):
    makedirs(tensorboard_logs)
    
    early_stop = EarlyStopping(# early stop
        monitor     = 'loss', #based on loss
        min_delta   = 0.01,   #if improvment less than 0.01 it's not a  real improve
        patience    = 5,      #number of times loss didn't improve to stop (5 times try )
        mode        = 'min',  #based on loss choice we want it min
        verbose     = 1       #print epoch and extra info default is 0
    )
    checkpoint = CustomModelCheckpoint(
        model_to_save   = model_to_save,
        filepath        = saved_weights_name,# + '{epoch:02d}.h5', 
        monitor         = 'loss', 
        verbose         = 1, 
        save_best_only  = True, 
        mode            = 'min', 
        period          = 1
    )
    reduce_on_plateau = ReduceLROnPlateau( # reduce learning rate when loss didn't improve
        monitor  = 'loss',  #based ob loss
        factor   = 0.1,     #factir if reduce
        patience = 2,       # every 2 epochs
        verbose  = 1,       # 0 equal quit , 1 update
        mode     = 'min',   #min mode for loss
        epsilon  = 0.01,    #change in epsilon
        cooldown = 0,       #number of epochs to wait before resuming normal operation after lr has been reduced.
        min_lr   = 0        #lower bound on the learning rate.
    )
    tensorboard = CustomTensorBoard(
        log_dir                = tensorboard_logs,
        write_graph            = True,
        write_images           = True,
    )    
    return [early_stop, checkpoint, reduce_on_plateau, tensorboard]
#======================================================================================================================#

#============================================ create model ============================================================#
def create_model(
    nb_class, #this is the total number of classes (labels)
    anchors,  #this is the anchors , from the config file
    max_box_per_image, #max box per image
    max_grid, batch_size, #max grid, batch size , from the config
    warmup_batches, #warmup  you start with a small learning rate and then gradually increase it by a constant
        # for each epoch till it reaches “k times learning rate”.
    ignore_thresh, #ignore threash the confidence level, if iou is less than this just ignore it and consider it false
    multi_gpu, #multi gpu
    saved_weights_name, #saved weights file name
    lr,#
    grid_scales,#grid scale
    obj_scale, #object scale
    noobj_scale, #no obj scale
    xywh_scale,#xywh scale
    class_scale  #class scale
):
    if multi_gpu > 1: # we have multi gpu use the best gpu, O:^) >:^)
        with tf.device('/cpu:0'):#close the cpu, choose best gpu 3:^)

            #make a template model (training model )and Inference model ( the final model to predict )
            template_model, infer_model = create_yolov3_model(
                nb_class            = nb_class, 
                anchors             = anchors, 
                max_box_per_image   = max_box_per_image, 
                max_grid            = max_grid, 
                batch_size          = batch_size//multi_gpu, 
                warmup_batches      = warmup_batches,
                ignore_thresh       = ignore_thresh,
                grid_scales         = grid_scales,
                obj_scale           = obj_scale,
                noobj_scale         = noobj_scale,
                xywh_scale          = xywh_scale,
                class_scale         = class_scale
            )
    else:#no gpu >:^(   T_T use the cpu
        template_model, infer_model = create_yolov3_model(
            nb_class            = nb_class, 
            anchors             = anchors, 
            max_box_per_image   = max_box_per_image, 
            max_grid            = max_grid, 
            batch_size          = batch_size, 
            warmup_batches      = warmup_batches,
            ignore_thresh       = ignore_thresh,
            grid_scales         = grid_scales,
            obj_scale           = obj_scale,
            noobj_scale         = noobj_scale,
            xywh_scale          = xywh_scale,
            class_scale         = class_scale
        )  
    #=================================================== weights ======================================================#
    # load the pretrained weight if exists, otherwise load the backend weight only
    if os.path.exists(saved_weights_name): #if the weight path exist
        print("\nLoading pretrained weights.\n")#load this weights
        template_model.load_weights(saved_weights_name)#add this weights to the template model (training model)
    else:#the path doesn't exist, first time train for example
        template_model.load_weights("backend.h5", by_name=True)#get the backend weights
    #==================================================================================================================#

    #=============================================== process ==========================================================#
    if multi_gpu > 1:# we have multi gpu O:^)
        train_model = multi_gpu_model(template_model, gpus=multi_gpu)#start train multi gpu template model

    else:#we don't have multi gpu
        train_model = template_model      # the template is the train model
    #==================================================================================================================#

    #=========================================== optmizers ============================================================#
    optimizer = Adam(lr=lr, clipnorm=0.001)#optmizer type and value
    train_model.compile(loss=dummy_loss, optimizer=optimizer)#loss type = dummy loss
    #==================================================================================================================#
    return train_model, infer_model#return the train model and the infer model (note that we didn't do much on infer
#======================================================================================================================#

#======================================================= main =========================================================#
def _main_(args):
    config_path = args.conf # get the path of the config file

    with open(config_path) as config_buffer:    #open the config file
        config = json.loads(config_buffer.read())#load the data from the config

    ###############################
    #   Parse the annotations 
    ###############################
    #======================================== get the information from the config =====================================#
    train_ints, valid_ints, labels, max_box_per_image = create_training_instances(
        config['train']['train_annot_folder'],
        config['train']['train_image_folder'],
        config['train']['cache_name'],
        config['valid']['valid_annot_folder'],
        config['valid']['valid_image_folder'],
        config['valid']['cache_name'],
        config['model']['labels']
    )
    #==================================================================================================================#

    print('\nTraining on: \t' + str(labels) + '\n')

    ###############################
    #   Create the generators 
    ###############################    
    train_generator = BatchGenerator(
        instances           = train_ints, 
        anchors             = config['model']['anchors'],   
        labels              = labels,        
        downsample          = 32, # ratio between network input's size and network output's size, 32 for YOLOv3
        max_box_per_image   = max_box_per_image,
        batch_size          = config['train']['batch_size'],
        min_net_size        = config['model']['min_input_size'],
        max_net_size        = config['model']['max_input_size'],   
        shuffle             = True, 
        jitter              = 0.3, 
        norm                = normalize
    )
    
    valid_generator = BatchGenerator(
        instances           = valid_ints, 
        anchors             = config['model']['anchors'],   
        labels              = labels,        
        downsample          = 32, # ratio between network input's size and network output's size, 32 for YOLOv3
        max_box_per_image   = max_box_per_image,
        batch_size          = config['train']['batch_size'],
        min_net_size        = config['model']['min_input_size'],
        max_net_size        = config['model']['max_input_size'],   
        shuffle             = True, 
        jitter              = 0.0, 
        norm                = normalize
    )
    #==================================================================================================================#
    ###############################
    #   Create the model 
    ###############################
    #
                        #---------------------------------------------------------------#
    if os.path.exists(config['train']['saved_weights_name']): #if the path of saved weights exist
        config['train']['warmup_epochs'] = 0 #warmup epochs=0, if we have already trained weights
                        #---------------------------------------------------------------#
    warmup_batches = config['train']['warmup_epochs'] * (config['train']['train_times']*len(train_generator))
    #get warmup from the config file
                        #---------------------------------------------------------------#

    os.environ['CUDA_VISIBLE_DEVICES'] = config['train']['gpus']
    multi_gpu = len(config['train']['gpus'].split(','))
                        #---------------------------------------------------------------#
    #======================================== train model and infer model =============================================#
    train_model, infer_model = create_model(
        nb_class            = len(labels), 
        anchors             = config['model']['anchors'], 
        max_box_per_image   = max_box_per_image, 
        max_grid            = [config['model']['max_input_size'], config['model']['max_input_size']], 
        batch_size          = config['train']['batch_size'], 
        warmup_batches      = warmup_batches,
        ignore_thresh       = config['train']['ignore_thresh'],
        multi_gpu           = multi_gpu,
        saved_weights_name  = config['train']['saved_weights_name'],
        lr                  = config['train']['learning_rate'],
        grid_scales         = config['train']['grid_scales'],
        obj_scale           = config['train']['obj_scale'],
        noobj_scale         = config['train']['noobj_scale'],
        xywh_scale          = config['train']['xywh_scale'],
        class_scale         = config['train']['class_scale'],
    )
    #==================================================================================================================#
    ###############################
    #   Kick off the training
    ###############################
    callbacks = create_callbacks(config['train']['saved_weights_name'], config['train']['tensorboard_dir'], infer_model)
    #==================================================================================================================#
    train_model.fit_generator(
        generator        = train_generator, 
        steps_per_epoch  = len(train_generator) * config['train']['train_times'], 
        epochs           = config['train']['nb_epochs'] + config['train']['warmup_epochs'], 
        verbose          = 2 if config['train']['debug'] else 1,
        callbacks        = callbacks, 
        workers          = 4,
        max_queue_size   = 8
    )
    #=========================================== the infer model(predict model)========================================#
    # make a GPU version of infer_model for evaluation
    if multi_gpu > 1:
        infer_model = load_model(config['train']['saved_weights_name'])#load the final weights
    #==================================================================================================================#

    #======================================== process on validation set ===============================================#
    ###############################
    #   Run the evaluation
    ###############################   
    # compute mAP for all the classes
    average_precisions = evaluate(infer_model, valid_generator)

    # print the score
    # print the map for every label
    for label, average_precision in average_precisions.items():
        print(labels[label] + ': {:.4f}'.format(average_precision))
    print('mAP: {:.4f}'.format(sum(average_precisions.values()) / len(average_precisions)))
    #==================================================================================================================#
if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='train and evaluate YOLO_v3 model on any dataset')
    argparser.add_argument('-c', '--conf',default='config.json', help='path to configuration file')

    args = argparser.parse_args()
    _main_(args)
    print('no error')