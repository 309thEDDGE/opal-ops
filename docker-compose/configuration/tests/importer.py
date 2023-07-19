import os
import importlib
import sys


# function to dynamically load module
def dynamic_module_import(module_name):
   
    fp = os.path.dirname(os.path.realpath(__file__))

    fp = fp.replace('tests', 'generate_files')
    sys.path.append( fp)

    return importlib.import_module(name=module_name)
