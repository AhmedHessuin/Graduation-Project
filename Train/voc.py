#commented by ibrahiem amr / ahmed hessuin
import numpy as np
import os
import xml.etree.ElementTree as ET
import pickle

def parse_voc_annotation(ann_dir, img_dir, cache_name, labels=[]):
    #voc function to read the input labels from the xml files
    if os.path.exists(cache_name): # check if the cache path exist
        with open(cache_name, 'rb') as handle:#open the files as read
            cache = pickle.load(handle)#get the cache file
        all_insts, seen_labels = cache['all_insts'], cache['seen_labels'] #get the number of all seen labels from the cache (.pkl)
    else:#there is no cache this is first time to train on this data
        all_insts = []#empty list for all insts
        seen_labels = {}#empty list of all labels
        
        for ann in sorted(os.listdir(ann_dir)):#for every annotation file (.xml) in the annotation folder path
            img = {'object':[]}#image opj

            try:#try for handling errors
                tree = ET.parse(ann_dir + ann)#the path exist or no
            except Exception as e:#error
                print(e)#print error
                print('Ignore this bad annotation: ' + ann_dir + ann)#print that we are going to ignore this bad anno(dosen't exist)
                continue#and continue for the next anno
            
            for elem in tree.iter():#we are fine we got the right anno, we are gonna search in tags
                if 'filename' in elem.tag:#file name tag refer to the image this anno is made for
                    img['filename'] = img_dir + elem.text#get the image from the image directory adding the file name
                if 'width' in elem.tag:#width of the image
                    img['width'] = int(elem.text)#get the width
                if 'height' in elem.tag:#height of the img
                    img['height'] = int(elem.text)#get the hight
                if 'object' in elem.tag or 'part' in elem.tag:#the object (the class label )
                    obj = {}#each object get his empty list
                    
                    for attr in list(elem):#itrate on the object tags
                        if 'name' in attr.tag:#object name (the class name )
                            obj['name'] = attr.text#get the name

                            if obj['name'] in seen_labels:#did we see this class before ?
                                seen_labels[obj['name']] += 1#add the seen labels number of this class by one
                            else:#we didn't see it, it's our first time
                                seen_labels[obj['name']] = 1#add this class in seen labels
                            
                            if len(labels) > 0 and obj['name'] not in labels:#check for illogical error, there is labels but no name !!!
                                break
                            else:
                                img['object'] += [obj]#for this image add this object (class)
                                
                        if 'bndbox' in attr.tag:#we are still in the object tags , the boundary box
                            for dim in list(attr):#for every dim in attr
                                if 'xmin' in dim.tag:#is there a xmin?
                                    obj['xmin'] = int(round(float(dim.text)))#get the xmin for this object boundary box
                                if 'ymin' in dim.tag:#is there a y min ?
                                    obj['ymin'] = int(round(float(dim.text)))#get the ymin for this object boundary box
                                if 'xmax' in dim.tag:#is there a xmax ?
                                    obj['xmax'] = int(round(float(dim.text)))#get the xmax for this object boundary box
                                if 'ymax' in dim.tag:#is there a ymax?
                                    obj['ymax'] = int(round(float(dim.text)))#get the ymax for this object boundary box

            if len(img['object']) > 0:#after we finished reading every tags (every existing object)
                all_insts += [img]#for global all_inst, add this file data to it.

        cache = {'all_insts': all_insts, 'seen_labels': seen_labels}#now we are gonna create a cache
        with open(cache_name, 'wb') as handle:#create the cache file name( from the config file )
            pickle.dump(cache, handle, protocol=pickle.HIGHEST_PROTOCOL)    #create the cache
                        
    return all_insts, seen_labels#return all inst and all seen labels