VERSION = (1, 0, 0, 'final', 20100908)
#          0  1  2  3        4

def get_version():
    version = '%s.%s.%s' % (VERSION[0], VERSION[1], VERSION[2]) 
    
    if VERSION[3] != 'final':
        version = '%s %s' % (version, VERSION[4])

    return version

