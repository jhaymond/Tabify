'''
A collection of utility functions and properties
'''

def read_args(args):
    '''
    
    '''
    arg_dict = {}
    i = 0
    
    while i < len(args):
        if args[i] == '--no-gui':
            arg_dict['no_gui'] = True
        elif args[i] == '-f':
            arg_dict['song_file'] = args[i + 1]
            i += 1
        i += 1
    
    return arg_dict
