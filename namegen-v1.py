"""
    RANDOM NAME GENERATOR

    What would this program look like if you were to give
    it to Jim Wampler or somebody to use?

    - it would have a wxWidgets/Gtk+ GUI
        - It would have a few checkboxes: #syllables, #names, trailing-vowel?
            #num-consonants per cluster: 1-10
        - the name would be in a textbox that has a button besides it
            called "copy to clipboard"
        - previous names would print out in an output window
            and be archived in a log-file
    - it would be available in Win/Mac/Linux zipped folder
    - it would run right out of the folder, no installer
    - keep all the pieces of code modular, so can be used across different
        projects, generators, ADD/DCCRPG/MCC, etc.
    - post in DCC forums that you've made this tool, how it works and where
        it can be downloaded
    - keep all on github in case someone wants to submit patches to improve it

TODO
    - list of consonant pairs that shouldn't be next to each-other, eg 'tn'

"""

from random import randint

consonants = { chr(L) for L in range( ord('A'), ord('Z')+1 ) }
vowels = {'A','E','I','O','U','Y'}
consonants ^= vowels
consonants = sorted(consonants)
vowels = sorted(vowels)

"""
    format CCC V CCC --

    - name begins with either consonant or vowel
    - name ends with either consonant or vowel
    - consonant sections can have between 1-3(4) consonants in them
    - consonants can repeat, so "Ulhh" is fine.

    - longest possible name configureation: is:
    - name can have at most 4 vowel+consonant sections: C V-C V-C V-C V-C V
"""

def rand_vowel():
    def s_vow():
        i=randint(0,len(vowels)-1)
        return vowels[i]
    if randint(1,7) == 1:
        return s_vow() + s_vow()
    else:
        return s_vow()

def rand_single_con():
    i=randint(0,len(consonants)-1)
    return consonants[i]

def make_con():
    N = 2 if randint(1,3) == 1 else 1
    return ''.join( [ rand_single_con() for _ in range(N) ] )

def make_pair():
    """ Vowel + Consonant Pair """
    s = [ rand_vowel() ]
    s.append( make_con() )
    print( ''.join(s) ) #DEBUG
    return ''.join(s)

def generate_name():
    # Beginning Consonant -- 50%
    C = randint(0,1)
    NAME=[ rand_single_con() if C==1 else '' ]

    # Num V-C Sections, weighted-low
    R = randint(1,32)
    if R <= 15:         # 14/32 (44%)   2 syllables
        sections = 2
    elif R <= 24:       # 9/32  (31%)   1 sylable
        sections = 1
    elif R <= 30:       # 6/32  (19%)
        sections = 3
    else:               # 2/32  (6%)
        sections = 4
    NAME.extend( [make_pair() for _ in range(sections)] )

    # Ending vowel -- 33.3%
    if randint(1,3) == 1:
        NAME.append( rand_vowel() )

    return ''.join( NAME ).capitalize()

if __name__ == '__main__':
    name = generate_name()
    print( 'Created name: "{}"'.format( name ) )
