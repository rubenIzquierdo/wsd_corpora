#import built-in modules
import socket

#import installed or created modules
from nltk.corpus import wordnet as wn
from lxml import etree
import datetime
import time


def analyse_sensetag_el(wf_el, sense_key_dict):
    '''
    given a wf_el (with or without the id child element)
    b'<wf id="a00001740_wf10" lemma="authority%1" pos="NN" tag="man">\n     
        <id id="a00001740_id.6" lemma="authority" sk="authority%1:07:00::"/>authority
    </wf>\n 
    this method returns a dict with 
    word, lemma, pos, original_id, annotation tag, sense_key, ilidef
    
    @type  wf_el: lxml.etree._Element
    @param wf_el: wf_el element in the wordnet gloss corpus
    
    @type  sense_key_dict: dict
    @param sense_key_dict: mapping from sense_key to ilidef (is updated
    to make sure that same sense_key is not converted more than once)
    
    @rtype: dict
    @return: mapping containing word, lemma, 
    pos, original_id, annotation tag, sense_key, ilidef
    
    '''
    #set sensekey and ilidef to default value
    sense_key = ""
    ilidef    = ""
    
    #try to get word (can be None if sent_el has a child element id)
    word = wf_el.text
    
    #try to get lemma
    if 'lemma' in wf_el.attrib:
        lemma = wf_el.get("lemma").split("%")[0]
    else:
        lemma = wf_el.text
    
    #obtain original_id and pos
    original_id = wf_el.get('id')
    pos         = wf_el.get('pos')
    
    #if type == 'punc' set to 'SYM'
    if wf_el.get('type') == 'punc':
        pos = "SYM"
    
    #for the examples, we do not know the pos = unkown
    if pos == None:
        pos = "unknown"
     
    #obtain tag and check if sent_el has a child element id   
    tag   = wf_el.get('tag')
    id_el = wf_el.find('id')
    
    #if there is a child element, get senses
    if id_el is not None:
        lemma     = id_el.get('lemma')
        word      = id_el.tail
        sense_key = id_el.get('sk')
        if sense_key in sense_key_dict:
            ilidef = sense_key_dict[sense_key]
        else:
            ilidef    = sense_key_to_ilidef(sense_key)
            sense_key_dict[sense_key] = ilidef
            
    return sense_key_dict,{'word'        : word,
                           'lemma'       : lemma,
                           'original_id' : original_id,
                           'pos'         : pos,
                           'sense_key'   : sense_key,
                           'ilidef'      : ilidef,
                           'tag'         : tag}
    

    
def sense_key_to_ilidef(sense_key):
    '''
    given a sensekey (assuming wordnet 3.0), this method returns
    the ili identifier if possible, else empty string
    
    >>> sense_key_to_ilidef('accessible%3:00:00::')
    'ili-30-00019131-a'
    
    >>> sense_key_to_ilidef('sdfoijsdfoijs%3:00:00::')
    ''
    
    >>> sense_key_to_ilidef('sdfiosdjfosjfoj')
    ''

    @type  sensekey: str
    @param sensekey: sensekey (for example 'accessible%3:00:00::')

    @rtype: str
    @return: ilidef if found, else empty string
    '''
    #obtain lemma and synset
    try:
        lemma  = wn.lemma_from_key(sense_key)
    except: #I know it's bad practice to do except: without specification, but are so many different errors possible here
        return ""
    
    #obtain synset and wn version
    synset  = lemma.synset()
    version = '30'
    
    #pos (tagset is n v r a)
    pos     = synset.pos()
    if pos == "s":
        pos = "r"
      
    #create proper offset (.offset remove the trailing zeros)  
    offset        = str(synset.offset())
    length_offset = len(offset)
    zeros         = (8-length_offset)*'0'
    
    ilidef = "ili-{version}-{zeros}{offset}-{pos}".format(**locals())
    return ilidef


def create_output_doc_with_header(xml_string):
    '''
    create new naf file using lxml
    
    @rtype: lxml.etree._Element
    @return: empty naf file with correct header information
    '''
    hostname = socket.gethostname()
    time_stamp = "{date}T{the_time}".format(date    = datetime.date.today(),
                                            the_time= time.strftime("%H:%M:%S"))
    xml_string = xml_string.format(**locals())
    
    doc = etree.fromstring(xml_string,
                           etree.XMLParser(remove_blank_text=True)
                           )
    return doc

xml_string = '''\
<?xml version='1.0'?>
<NAF xml:lang="en" version="1.0">
    <nafHeader>
        <linguisticProcessors layer="text">
            <lp name="Princeton WordNet Gloss Corpus" version="1.0" timestamp="2012" beginTimestamp="{time_stamp}" endTimestamp="" hostname="{hostname}"/>
        </linguisticProcessors>
        <linguisticProcessors layer="terms">
            <lp name="Princeton WordNet Gloss Corpus" version="1.0" timestamp="2012" beginTimestamp="{time_stamp}" endTimestamp="" hostname="{hostname}"/>
        </linguisticProcessors>
        <linguisticProcessors layer="wsd">
            <lp name="Princeton WordNet Gloss Corpus" version="1.0" timestamp="2012" beginTimestamp="{time_stamp}" endTimestamp="" hostname="{hostname}"/>
        </linguisticProcessors>
    </nafHeader>
    <text></text>
    <terms></terms>
</NAF>
'''
