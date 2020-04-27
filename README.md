# Graduaiton-Project
# About Project:
----------------------------

# Project Files:
* file name
* file name
* .
* .
*transactionToVerilog.py 
  *File Role:Defines a function with the same name that returns the Verilog code as a string as a replacement to xmlToverilog.py 
This python function takes 2 arguments : The module name as a string , and the list of transactions describing the finite state   machine diagram . 
  The function returns a string with the Verilog code corresponding to the finite state machine (with proper indentations).
 

 Each element in the list of transactions is a dictionary containing 4 elements with the following keys:
  "src_id" : contains the name of the source state as a string
  "dst_id" : contains the name of the destination state as a string
  "input" : contains the input bits of that transaction as a string
  "output" : contains the output bits needed when that transaction occurs as a string

 Notes: 
 - The number of bits of the input/output in all transactions must be the same in order for the function to work .

  *Runnability: Not Runnable -to be used in the main code 

* node.py
  * File Role: Defines class 'Node' which defines a state to be used in transactionToVerilog.py for verilog code creation
  * Runnability: Not Runnable - used only in transactionToVerilog.py
* xmlToverilog.py
  * File Role: Generates the Verilog code from detected transactions which are saved in XML format
  * Runnability: can be run from a comand line with an optional path argument (--path) determining the XML file path.(if path isn't supplied it is assumed that the XML file is in the working directory with name a.xml)
  
# Project Algorithm Flow:
----------------------------
