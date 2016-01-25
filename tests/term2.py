#!/usr/bin/env python3
import random

def terminal_size():
    import fcntl, termios, struct
    h, w, hp, wp = struct.unpack(
        'HHHH',
        fcntl.ioctl(0, termios.TIOCGWINSZ,
            struct.pack('HHHH', 0, 0, 0, 0)
        )
    )
    return h, w

height, width = terminal_size()
print( "terminal height: {}, width: {}".format( height, width ) )

print_height = 0

dictionary = []
# create long dataset
with open("/usr/share/dict/words","r") as f:
    dictionary = f.read().split('\n')[random.randint(100,5000):]

wordnum = 0
def mapwords(l):
    global wordnum
    i = wordnum
    wordnum = wordnum + 1
    return '{}  {}'.format( wordnum, dictionary[i] )

dataset = list(map( mapwords, range(1,201) ))

index = 0
while index < len(dataset):
    line = dataset[index]
    if print_height >= height - 1:
        print_height = 0
        ans = input( "(Enter)Continue/(P)revious/(Q)uit? > " )
        if ans.lower() == 'p':
            index = max( index - 2 * ( height - 1 ), 0 )
            continue
        elif ans.lower() == 'q':
            break

    print( line )
    print_height = print_height + 1
    index = index + 1
