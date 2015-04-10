#import built-in modules
import argparse
import glob
from collections import defaultdict
import cPickle
import os

#import external modules
import utils
from lxml import etree

'''
goal of this module is to
(1) loop through semcor
(2) count for every lemma+ "___" + pos the sense distribution
(3) save this information into pickle, which has the following format:
    lemma.pos:
        -> mfs:   list of one or more senses with the highest freq in SemCor
        -> senses dictionary mapping from reference to count
'''

__author__     = "Marten Postma"
__license__    = "Apache 2.0"
__version__    = "1.0"
__maintainer__ = "Marten Postma"
__email__      = "martenp@gmail.com"
__status__     = "production"

#parse arguments
parser = argparse.ArgumentParser(description='Load sense freq dict from SemCor')

parser.add_argument('-i',   dest='input_folder',   help='folder with naf files (to semcor 1.6 or semcor 3.0)',  required=True)
parser.add_argument('-w',   dest='resource',       help='WordNet-eng16 | WordNet-eng30',                        required=True)
parser.add_argument('-r',   dest='reftype',        help="lexical_key | synset",                                 required=True)
parser.add_argument('-o',   dest="output_folder",  help="basename will be resource_reftype",                    required=True)
parser.add_argument(        dest="ili", type=bool, help="if 'ili' is added at the end of the call, the synset references will be converted to ili definitions")

args = parser.parse_args()


#set data
sense_freq = defaultdict(dict)

#set string to external references elements in naf
path_to_ext_ref_els = "/".join(["terms",
                                "term",
                                "externalReferences",
                                "externalRef"
                                ])

#loop through naf files
for naf_file in utils.path_generator(args.input_folder,".naf"):
    
    #parse naf file
    doc = etree.parse(naf_file)
    
    #loop through it
    for ext_ref_el in doc.iterfind(path_to_ext_ref_els):
        
        #check parameters settings
        attrib = ext_ref_el.attrib
        if all([attrib['resource'] == args.resource,
                attrib['reftype']  == args.reftype
                ]):
            #obtain reference
            reference = attrib['reference']
            
            #convert it if needed by args.ili
            if args.ili:
                reference = reference.replace("eng","ili-")

            #obtain pos,lemma
            pos       = reference[-1]
            lemma     = ext_ref_el.getparent().getparent().get("lemma")
            lemma_pos = "%s___%s" % (lemma,pos)
            
            #add to dict
            if lemma_pos not in sense_freq:
                sense_freq[lemma_pos]["senses"] = defaultdict(int)
            sense_freq[lemma_pos]["senses"][reference] += 1

#calculate mfs
for lemma_pos,info in sense_freq.iteritems():
    
    mfs = utils.mfs(info['senses'])
    
    sense_freq[lemma_pos]['mfs'] = mfs
    
    
#write output

if args.ili:
    args.reftype = "ili"
    
output_path = os.path.join(args.output_folder,
                           args.resource+"_"+args.reftype)
with open(output_path,"w") as outfile:
    cPickle.dump(sense_freq, outfile, protocol=0)
    
print
print "the sense freqency dict for:"
print "resource: %s" % args.resource
print "reftype:  %s" % args.reftype
print
print "can be found here:"
print output_path
print
print 'the cPickle object has the following structure:'
print '''
'lemma___pos':
        -> 'mfs':    : list of one or more senses with the highest freq in SemCor version
        -> 'senses'  : dictionary mapping from reference (str) to count (int)
'''