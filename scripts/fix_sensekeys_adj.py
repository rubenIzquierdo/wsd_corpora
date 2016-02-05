#!/usr/bin/env python

from KafNafParserPy import KafNafParser
import sys

if __name__ == '__main__':
    
    #Load Wordnet
    synset_for_skey = {}
    path_to_index_sense = '/home/izquierdo/wordnets/wordnet-3.0/dict/index.sense'
    fd = open(path_to_index_sense)
    for line in fd:
        fields = line.split()
        synset_for_skey[fields[0]] = fields[1]
    fd.close()
    
    
    naf_obj = KafNafParser(sys.stdin)
    
    for term in naf_obj.get_terms():
        this_skey = None
        this_synset = None
        ref_skey = ref_synset = None
        for ext_ref in term.get_external_references():
            if ext_ref.get_reftype() == 'sense':
                this_skey = ext_ref.get_reference()
                ref_skey = ext_ref
            if ext_ref.get_reftype() == 'ilidef':
                this_synset = ext_ref.get_reference()
                ref_synset = ext_ref
        
        if this_synset == '':
            print>>sys.stderr,term.get_id()
            if '%3:' in this_skey:
                this_skey = this_skey.replace('%3:','%5:')
            elif '%5:' in this_skey:
                this_skey = this_skey.replace('%5:','%3:')
            
            this_synset = synset_for_skey.get(this_skey)
            if this_synset is not None:
                ref_skey.set_reference(this_skey)
                ref_synset.set_reference('ili-30-%s-a' % this_synset)
        
    naf_obj.dump()