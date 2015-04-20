import os

def path_generator(base_dir,extention):
    '''
    given a base directory containing possible subdirectories
    this method returns a generator with all paths with a certain extention.
    
    @type  base_dir: str
    @param base_dir: full path to directory
    
    @type  extention: str
    @param extention: wanted extention, for example '.bz2'
    
    @rtype:  generator
    @return: generator all paths with param extention
    ''' 
    for (dirpath, dirnames, filenames) in os.walk(base_dir):
        for filename in filenames:
            if filename.endswith(extention): 
                yield os.sep.join([dirpath, filename])
                
                
def mfs(d):
    '''
    return mfs of lemma, multiple if same count

    >>> mfs({'ili-30-01835663-a': 2, 'ili-30-01822563-a': 1})
    ['ili-30-01835663-a']
    
    >>> mfs({'ili-30-01835663-a': 2, 'ili-30-01822563-a': 2})
    ['ili-30-01835663-a', 'ili-30-01822563-a']
    
    })
    
    @type  d: dict
    @param d: mapping from reference (str) to count (int)
    
    @rtype: list
    @return: list of mfs
    '''
    max = 0
    mfs = []
    
    for reference,count in d.iteritems():
        
        if count > max:
            mfs = [reference]
            max = count
        
        elif count == max:
            mfs.append(reference)
    
    return mfs