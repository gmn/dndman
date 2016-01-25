#!/usr/bin/env python3
import json
import os

def list_dir(d):
    files=[]
    def _ld(d,files):
        if os.path.isfile(d):
            files.append(d)
        elif os.path.isdir(d):
            for x in os.listdir(d):
                _ld(os.path.join(d,x), files)
    _ld(d,files)
    return sorted(files)

files = list_dir('.')
for file in files:
    if '.json' not in file:
        continue

    try:
        with open( file, "r" ) as f:
            json.load(f)

        print( "{} passed".format(file) )
    except:
        print( "{} <------------------ BROKEN".format(file) )
        raise


