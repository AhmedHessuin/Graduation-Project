# Graduaiton-Project
# About Project:
# input constrains 
  * don't use any tensorflow application when you run the exe, tensorflow runs on one main thread, this will lead to faliure in both programs.
  * image type -> .jpg .png .JPEG 
  * the input images shouldn't be small images like 280 * 280 or something like that, at least 800 * 600.
  * the input images can't be sharpened, this lead to false/no predict, example http://madebyevan.com/fsm/ save images as sharpened image that need to edit with paint.
  * best performance with images 1600 * 1200.
  * input images resized to 1600 * 1200 from small images lead to incorrect predict.
  * no words in the image, it can lead to false predict.
  * if the gui Crash, check the input image and check if the input image justify the opencv imread function or no.
  
  
# training files
* training images and annotations
  * https://drive.google.com/open?id=1NBn4ybLnFkzkD88xYLDjqtTPc4-8mSk4, train images folder 
  * https://drive.google.com/open?id=1frt7EfAvlOONhB8-DsDOBWohsjNW0W7j, train annotations folder
  * https://drive.google.com/open?id=1pL-tGmqbG-LTmumjL9hiej2s04obpi9W, original train images in high resolutions
  * https://drive.google.com/open?id=1WfFPYJm3aJwjzHs17yPwX-4LiHNsOQdH, number train images folder,annotations is built in.
  * for testing the module on the training example, use original train image because of the resolution.
  * common error, if image faild to load or predict using the gui, change it to .jpg or another format
----------------------------

# Project Files:
* transactionToVerilog.py 
  * File Role:Defines a function with the same name that returns the Verilog code as a string as a replacement to xmlToverilog.py 
This python function takes 2 arguments : The module name as a string , and the list of transactions describing the finite state   machine diagram . 
  The function returns a string with the Verilog code corresponding to the finite state machine (with proper indentations).
 
  * Each element in the list of transactions is a dictionary containing 4 elements with the following keys:
    * "src_id" : contains the name of the source state as a string
    * "dst_id" : contains the name of the destination state as a string
    * "input" : contains the input bits of that transaction as a string
    * "output" : contains the output bits needed when that transaction occurs as a string

  * Notes: 
    * The number of bits of the input/output in all transactions must be the same in order for the function to work .

  * Runnability: Not Runnable -to be used in the main code 

* node.py
  * File Role: Defines class 'Node' which defines a state to be used in transactionToVerilog.py for verilog code creation
  * Runnability: Not Runnable - used only in transactionToVerilog.py
* xmlToverilog.py
  * File Role: Generates the Verilog code from detected transactions which are saved in XML format
  * Runnability: can be run from a command line with an optional path argument (--path) determining the XML file path.(if path isn't supplied it is assumed that the XML file is in the working directory with name a.xml)
----------------------------------------------------------- train files -------------------------------------------------------------
* Train.py 
  * File Role: to train the yolo modules.
* gen_anchors.py
  * File Role: generate anchors for the modules based on the labels and the truth box.
* train_knn.py
  * File Role: train k nearest neighborhood module for number detection.
  
-------------------------------------------------------- backend files ---------------------------------------------------------------
* predict.py 
  * File Role: this file is the core file for prediction, as this call and connect other backend files to predict and draw the predicted anchors on the image.
  * Runnability: can be run, need image named test.png and will generate verilog code and the predicted image.
* image_operations.py 
  * File Role: this file do all operations on image like : draw on the image, add element to draw, remove element from the image, load the original image.
* matching.py
  * File Role: this file for connecting the anchors, this file has the algorithm of searching and defining which anchors connected together, it has function to define the states and its condition as a transaction, if the matching passed this file gives permission for Verilog to generate.
  * Runnability: can't run, full of functions only
* anchor_sub_file.py 
  * File Role: this file contain preprocessing on part of the image to detect the numbers.
  * this file detect numbers.
  * Runnability: can't run, full of functions only
* bbox.py 
  * File Role: this file predict and recognize the anchors on the image based on the module.
  * Runnability: can't run, full of functions only
* xml_creator.py
  * File Role: work with tree_build_function.py to create xml files.
  * Runnability: can't run, full of functions only
* data_class.py
  * File Role: this file contain all the data types used on backend files ( except on the bbox.py).
  * Runnability: can't run, full of classes only
* object_file.py
  * File Role: this file contain all the global and shared objects between files, a core file that every file call.
  * Runnability: can't run, full of objects only
* log_config.py
  * File Role: this file contain the log format for the gui.
  * Runnability: can't run, full of functions only
-----------------------------------------------------------------------------------------------------------------------------------
  
# Project Algorithm Flow:

* behavior one, the user use predict.py
  * first step: predict
    * the predict.py will call load weight function, to load the module weights.
    * then call the predict function, after loading the weights, this function predict every label by calling bbox.py file
    * the bbox.py call sub_anchor.py  when it predict state condition or state, to predict and allocate where is the numbers in the state conditions and the states
    * after predicting where is the anchors on the image and the label for every anchor, now call the image_operations.py and draw this anchors
  * second step: connect and get transactions
    * after drawing the anchors, call file matching.py, to connect every anchor with another intersected anchor, py connect anchors function
    * after getting the relations with the anchors, call connect the transactions function.
    * connect transactions function, get every arrow head then get which state it's connected to the arrow head, marking this state as the dst state, search for the arrow connected to this arrow head, getting from this arrow the src state and the state condition
    * the state condition get the predicted numbers inside it, sorting them from left to right and get the state condition input/output
    * the src state and dst state, also get the predicted numbers inside it and mark it as the src,dst state id
    * checking algorithm for errors, if there is no src state or dst state or there is no state condition
    * return error msg to the user if there is an error, or return log msg in the screen of the states transactions and set valid verilog code to be true
  * third step: generate the verilog
    * after checking and setting the valid to be true, go to transactions_to_verilog.py to write on file the relations of the state based on connect transactions algorithm.
  
  
* behavior two, the user use the gui
  
----------------------------
# To Run the project run predict/mainfile.py
----------------------------
# Used libraries:
 * Tensorflow-gpu version 1.14
 * Keras version 2.3.1
 * cuda 10.0
 * cudnn
 * OpenCv
# Project Demo:
 * [Demo Link](https://drive.google.com/open?id=1DU-FfDiuBAhmYHOsoOOwWzaueoBSbYg8)
