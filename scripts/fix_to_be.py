#!/usr/bin/env python

from KafNafParserPy import KafNafParser
import sys

if __name__ == '__main__':
    naf_obj = KafNafParser(sys.stdin)

    candidates = set(['is','are','were','was',"'s"])
    for term in naf_obj.get_terms():
        if term.get_lemma() == 'i':
            token_id = term.get_span().get_span_ids()[0]
            token = naf_obj.get_token(token_id).get_text()
            if token in candidates:
                term.set_lemma('be')
                term.set_pos('VBZ')

    naf_obj.dump()