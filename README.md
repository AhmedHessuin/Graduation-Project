# Graduaiton-Project
# About Project:
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
  *to train the yolo modules.
* gen_anchors.py
  * generate anchors for the modules based on the labels and the truth box.
* train_knn.py
  * train k nearest neighborhood module for number detection.
  
-------------------------------------------------------- backend files ---------------------------------------------------------------
* predict.py 
  * this file is the core file for prediction, as this call and connect other backend files to predict and draw the predicted anchors on        the image.
  * Runnability: can be run, need image named test.png and will generate verilog code and the predicted image.
* image_operations.py 
  * this file do all operations on image like : draw on the image, add element to draw, remove element from the image, load the original image.
* matching.py
  * this file for connecting the anchors, this file has the algorithm of searching and defining which anchors connected together, it has function to define the states and its condition as a transaction, if the matching passed this file gives permission for Verilog to generate.
* anchor_sub_file.py 
  * this file contain preprocessing on part of the image to detect the numbers.
  * this file detect numbers.
* bbox.py 
  * this file predict and recognize the anchors on the image based on the module.
* xml_creator.py
  * work with tree_build_function.py to create xml files.
* data_class.py
  * this file contain all the data types used on backend files ( except on the bbox.py).
* object_file.py
  * this file contain all the global and shared objects between files, a core file that every file call.
* log_config.py
  * this file contain the log format for the gui.
-----------------------------------------------------------------------------------------------------------------------------------
  
# Project Algorithm Flow:
----------------------------
