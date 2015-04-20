#import built-in modules
import argparse
import glob 
import itertools
import os
import time
import datetime

#load installed or created modules 
from lxml import etree
from nltk.corpus import wordnet as wn
import wn_gloss_corpus_to_naf_utils as utils

'''
goal of this module is to
(1) loop through .xml files of wordnet gloss corpus
(2) convert each file to naf (while also converting sensekeys to ilidefs)

by means of experiment, this script should run with both python2.7 and python3.3
'''

#pos tagset
#they seem to use
#https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
__date__       = "19-04-2015"
__author__     = "Marten Postma"
__license__    = "Apache 2.0"
__version__    = "1.0"
__maintainer__ = "Marten Postma"
__email__      = "martenp@gmail.com"
__status__     = "developement"

#parse arguments
parser = argparse.ArgumentParser(description='''Convert wordnet gloss corpus to NAF. Note: external libraries are needed to run this script.
I used: (1) lxml (lxml.etree version 3.3.5), and (2) nltk (version 3.0.0)''')

parser.add_argument('-i',           dest='input_folder',    help='''download the wordnet gloss corpus from (http://wordnetcode.princeton.edu/glosstag-files/WordNet-3.0-glosstag.zip),
unzip it. and provide the full path to the 'merged' folder (probably UNZIPPED_FOLDER_NAME/glosstag/merged)''',                                              required=True)
parser.add_argument('-o',           dest="output_folder",   help="full path to output folder", required=True)
parser.add_argument('-a',           dest='annotation_tags', help="divided by underscore the annotation tags you want to include: man | auto")
parser.add_argument('-s',           dest='sentence',        help='''synset | example. synset: definition and examples are considered a sentence as a whole. example: every definition and example
is considered a separate sentence.''', required=True)
parser.add_argument("--examples", dest="examples", help="include examples", action="store_true", default=False)

#include example sentences or not
args = parser.parse_args()

args.annotation_tags = args.annotation_tags.split("_")
sense_key_dict = {}

#for wn_gloss_xml in input folder
for wn_gloss_xml in glob.glob("{input_folder}/*.xml".format(input_folder=args.input_folder)):
            
    
    print(wn_gloss_xml,datetime.datetime.now())
                      
    #parse xml file and create output_path (based on setting lemmatised)
    inputdoc = etree.parse(wn_gloss_xml)
    
    #create new xml instance
    outputdoc           = utils.create_output_doc_with_header(utils.xml_string)
    output_doc_text_el  = outputdoc.find("text")
    output_doc_terms_el = outputdoc.find('terms')
    
    #set offset + wf_id start + sent_id start
    t_and_wf_id = 0 # updating is done before processing sentence, hence first will be one
    sent_id     = 0 # updating is done before processing sentence, hence first will be one
    
    #loop synset/gloss 
    for gloss_el in inputdoc.iterfind("synset/gloss[@desc='wsd']"):
        
        #update sent_id
        if args.sentence == "synset": #based on settings of args.sentence
            sent_id += 1 
        
        #loop over both ex and def elements
        sent_el_loop = gloss_el.iterfind("def")
        if args.examples: 
            sent_el_loop = itertools.chain(gloss_el.iterfind("def"),
                                       gloss_el.iterfind("ex"))
            
        for sent_el in sent_el_loop:
            
            #update sent_id
            if args.sentence == "example": #based on setting of args.sentence
                sent_id += 1
                
            #loop over paths "qf/wf" (ex) and "wf" (def and ex)
            for el_path in ['qf/wf','wf']:
                for wf_el in sent_el.iterfind(el_path):
                    sense_key_dict,info = utils.analyse_sensetag_el(wf_el,
                                                                    sense_key_dict)
                    
                    #add dict key values to locals()
                    for key,value in info.items():
                        locals()[key] = value

                    #update t_and_wf_id
                    t_and_wf_id   += 1
                    
                    #add this point, we need
                    #word lemma pos tag t_and_wf_id sent_id [sense_key ilidef]
                    
                    #add wf_el
                    wf_attrib = {"id"  : "w"+str(t_and_wf_id),
                                 'sent': str(sent_id)}
                    new_w_el = etree.SubElement(output_doc_text_el, 
                                                'wf',
                                                attrib=wf_attrib)
                    new_w_el.text = word
                    output_doc_text_el.append(new_w_el)
                    
                    #term_el
                    
                    #set term attributes
                    t_attrib = {'id'         : 't'+str(t_and_wf_id),
                                'lemma'      : lemma,
                                'pos'        : pos}
                    
                    #create new term el
                    new_t_el = etree.SubElement(output_doc_terms_el, 
                                                'term',
                                                attrib=t_attrib)
                    
                    #create new span el and target el
                    span_el = etree.SubElement(new_t_el,
                                               'span')
                    
                    target_el = etree.SubElement(span_el,
                                                 'target',
                                                 attrib={'id': 'w'+str(t_and_wf_id)})
                    
                    #add elements
                    span_el.append(target_el)
                    new_t_el.append(span_el)
                    output_doc_terms_el.append(new_t_el)
                    
                    #if tag in args.annotation_tags
                    if tag in args.annotation_tags:
                        
                        #add ext refs el
                        ext_refs_el = etree.SubElement(new_t_el, "externalReferences")
                        
                        #attributes
                        attrib = {'resource'   : 'WordNet-3.0',
                                  'confidence' : '1.0', #do not know what to do with this if tag is other than manual
                                  'reference'  : "",
                                  'reftype'    : ""}
                        
                        #add sensekey
                        attrib['reftype']   = 'sense'
                        attrib['reference'] = sense_key
                        
                        ext_ref_el = etree.SubElement(new_t_el, 
                                                      "externalRef",
                                                      attrib=attrib)
                        ext_refs_el.append(ext_ref_el)
                        
                        #add ilidef
                        attrib['reftype']   = 'ilidef'
                        attrib['reference'] = ilidef
                        
                        ext_ref_el = etree.SubElement(new_t_el, 
                                                      "externalRef",
                                                      attrib=attrib)
                        ext_refs_el.append(ext_ref_el)
    
                        
                        #add original id
                        attrib['reftype']   = 'original_id'
                        attrib['reference'] = original_id
                        
                        ext_ref_el = etree.SubElement(new_t_el, 
                                                      "externalRef",
                                                      attrib=attrib)
                        ext_refs_el.append(ext_ref_el)
                        
                        new_t_el.append(ext_refs_el)
        
    #write output to file
    output_path = os.path.join(args.output_folder,
                               args.sentence+"."+os.path.basename(wn_gloss_xml)+".naf")
    
    #update timestamp info
    time_stamp = "{date}T{the_time}".format(date    = datetime.date.today(),
                                            the_time= time.strftime("%H:%M:%S"))
    for lp_el in outputdoc.iterfind("nafHeader/linguisticProcessors/lp"):
        lp_el.attrib['endTimestamp'] = time_stamp
    
    #write to file
    with open(output_path,"wb") as outfile:
        outputdoc.getroottree().write(outfile, 
                  xml_declaration=True,
                  encoding='utf-8',
                  pretty_print=True
                  )
    
