#!/usr/bin/env python

import argparse
import os

from KafNafParserPy import KafNafParser, CexternalReference

ADJ = 'adj'
ADV = 'adv'
NOUN = 'noun'
VERB = 'verb'
os.environ['LC_ALL'] = 'en_US.UTF-8' 
__this_dir__ =  os.path.dirname(os.path.realpath(__file__))
__mappings_path__ = __this_dir__+'/resources/mappings-upc'

    
def load_mapping(from_version, to_version):
    map_from_to = {}
    for pos in [ADJ,ADV,NOUN,VERB]:
        map_from_to[pos] = {}
        map_file = __mappings_path__+'/mapping-'+from_version+'-'+to_version+'/wn'+from_version+'-'+to_version+'.'+pos
        fd = open(map_file,'r')
        for line in fd:
            fields = line.strip().split()
            # In some cases there is more than one possible target synset: 00005388 00525453 0.421 01863970 0.579 
            # So we need to load all of them and select the one with highest probabily
            possible_synsets_conf = []
            
            #This is just to parse 00005388 00525453 0.421 01863970 0.579 
            for n in range((len(fields)-1)/2):
                possible_synsets_conf.append((fields[2*n+1],float(fields[2*n+2])))
            synset_from = fields[0]
            synset_to = sorted(possible_synsets_conf,key = lambda t: -t[1])[0][0]
            map_from_to[pos][synset_from] = synset_to
        fd.close()
    return map_from_to
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Maps synset from one WN version to another', version='1.0')
    parser.add_argument('-if',dest='input_file', help='Input KAF/NAF file', required=True)
    parser.add_argument('-iv', dest='input_version', help='Input WN version of the synsets', required=True)
    parser.add_argument('-ir', dest='input_res_label', help='Input resource label for synset references', required=True)
    parser.add_argument('-of',dest='output_file', help='Output KAF/NAF file', required=True)
    parser.add_argument('-ov', dest='output_version', help='Output WN version of the synsets', required=True)
    parser.add_argument('-or', dest='output_res_label', help='Output resource label for synset references', required=True)
    
    args = parser.parse_args()
    
    mapping = load_mapping(args.input_version, args.output_version)
    
    
    obj = KafNafParser(args.input_file)
    for term in obj.get_terms():
        source_synset = None
        for ext_ref in term.get_external_references():
            if ext_ref.get_resource() == args.input_res_label and ext_ref.get_reftype() == 'synset':
                source_synset = ext_ref.get_reference()
                break
        if source_synset is not None:
            fields = source_synset.split('-')
            this_synset = fields[1]
            short_pos = fields[2]
            if   short_pos == 'a': this_pos=ADJ
            elif short_pos == 'n': this_pos=NOUN
            elif short_pos == 'r': this_pos=ADV
            elif short_pos == 'v': this_pos=VERB
            else: this_pos = None
            
            if this_pos is not None:
                target_synset = mapping[this_pos].get(this_synset)
                if target_synset is not None:
                    full_reference = 'eng%s-%s-%s'  % (args.output_version,target_synset,short_pos)
                    new_ref = CexternalReference()
                    new_ref.set_reference(full_reference)
                    new_ref.set_confidence('1.0')
                    new_ref.set_reftype('synset')
                    new_ref.set_resource(args.output_res_label)
                    term.add_external_reference(new_ref)
    
    obj.dump(args.output_file)