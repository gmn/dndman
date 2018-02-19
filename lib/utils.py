""" METHODS & CLASSES
    * helpers that are generic to the application """

import json
import random
import os
import time
import datetime

#
# classes
#
class Logger:
    def __init__(self,path):
        self.path = path
        self.fh = open( self.path, 'a' )
    def log( self, msg ):
        if not msg or len(msg) < 2:
            return
        if msg[-1] != '\n':
            msg = '{}\n'.format(msg)
        self.fh.write( msg )
    def __del__(self):
        self.fh.close()

class Money:
    def __init__(self, obj=False):
        if obj:
            self.money = obj
        else:
            self.money = {}

    def me_and_you(self, rhs):
        me = frac_coin(self.money)
        if type(rhs) is Money:
            rhs = rhs.money
        yu = frac_coin(rhs)
        return me, yu

    def __lt__(self, rhs):
        me, yu = self.me_and_you( rhs )
        return me < yu

    def __gt__(self, rhs):
        me, yu = self.me_and_you( rhs )
        return me > yu

    def __eq__(self, rhs):
        me, yu = self.me_and_you( rhs )
        return me == yu

    def __le__(self, rhs):
        me, yu = self.me_and_you( rhs )
        return me <= yu

    def __ge__(self, rhs):
        me, yu = self.me_and_you( rhs )
        return me >= yu

    # a - b
    def __sub__(self, rhs):
        # break money into change?
        pass

class RandomDiceRoller:
    def dn(s, n):
        return random.randint(1,n)
    def d4(s):
        return s.dn(4)
    def d6(s):
        return s.dn(6)
    def d8(s):
        return s.dn(8)
    def d10(s):
        return s.dn(10)
    def d12(s):
        return s.dn(12)
    def d20(s):
        return s.dn(20)
    def d100(s):
        return s.dn(100)

    def xdx( self, idi, separate=False ):
        """ takes a string in the format <int>d<int>, eg. 3d6, 6d4 """
        nums = idi.split('d')
        if not nums[0]:
            nums[0] = 1

        t = []
        d = int(nums[1])
        for _ in range( int(nums[0]) ):
            t.append( self.dn( d ) )

        return t if separate else sum(t)

    def roll( self, inp, separate=False ):
        """ computes string of N rolls of xdx joined by '+'. Can also do XDX + CONST """
        drop_lowest = False
        if 'drop lowest' in inp:
            drop_lowest = True
            inp = inp.replace('drop lowest','')

        rolls = inp.replace(' ','').split('+')
        dice_totals = []
        for roll in rolls:
            val = self.xdx( roll, separate=True ) if 'd' in roll else int(roll)
            if type(val) is int:
                dice_totals.append(val)
            else:
                dice_totals.extend(val)
        if drop_lowest:
            dice_totals.remove( min(dice_totals) )
        return dice_totals if separate else sum(dice_totals)

    def mult( self, inp ): # Expects the strict form: "XdX x INTEGER"
        try:
            rolls = inp.replace(' ','').split('x')
            return self.xdx( rolls[0] ) * int( rolls[1] )
        except:
            print( 'dice.mult() Expects the strict form: "XdX x INTEGER"' )
            raise

class RandomTable:
    def __init__( self, table=False ):
        self.table = table
        self.roller = RandomDiceRoller()
    def roll( self, inp=False, sep=False ):
        die_roll = inp if inp is not False else self.roller.roll( self.table['roll'] )
        lrow = self.table['table'][-1]
        for row in reversed(self.table['table']):
            if row['roll'] < die_roll:
                return (lrow['val'], die_roll) if sep else lrow['val']
            lrow = row
        return (lrow['val'], die_roll) if sep else lrow['val']


#
# methods
#
def arraystr(L):
    s = ''
    if not L:
        return s
    for l in L:
        s = '{}"{}", '.format( s, l )
    s = s.rstrip()
    if s and s[-1] == ',':
        s = s[:-1]
    return s


def terminal_size():
    def unix_termsize():
        import fcntl, termios, struct
        h, w, hp, wp = struct.unpack(
            'HHHH',
            fcntl.ioctl(0, termios.TIOCGWINSZ,
                struct.pack('HHHH', 0, 0, 0, 0)
            )
        )
        return h, w
    if os.name == 'nt':
        from lib.terminalsize import get_terminal_size
        return get_terminal_size()
    else:
        return unix_termsize()

def timestamp():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

def Message( s ):
    s = s.rstrip().lstrip()
    fmt = {'ts': timestamp(), 'msg': s}
    global messages
    messages.append( fmt )
    print( '\n -> {}\n'.format(s) )
    log( json.dumps(fmt, sort_keys=True) )
    time.sleep( msg_time )

def vowel( l ):
    l = l.replace(' ','').lower()
    return l == 'a' or l == 'e' or l == 'i' or l == 'o' or l == 'u'

def article(word, capital=True): # returns the word with the appropriate leading article
    a = 'A' if capital else 'a'
    if not word:
        return a
    return (a + 'n ' if vowel(word[0]) else a + ' ') + word

# variable!
DEBUG = False

def dprint( s ):
    if DEBUG is True:
        print( 'DEBUG: {}'.format(s) )

#
# money helper methods
#
def currency_base( it, quantity, ot ):
    io = world['exchange_rate'][it][ot]
    return io * int(quantity)

def frac_coin( money, kind='gp' ):
    tot = 0
    for t in ('cp','sp','gp','ep','pp'):
        if t in money:
            tot = tot + currency_base( t, money[t], kind )
    return tot

def make_change( mine, cost ):
    """ - cost names a cost in an arbitrary coin value.
        - mine names the coins I have.
        - returns False if I don't have enough
        X otherwise, spends the minimum number of coins I have,
            and tries to spend the lower denominations first,
            returning the change left.
        - wasn't able to do the method where I expend the least amount
            of coins from my person. Instead, I convert everything to cp,
            which is the finest granlarity and not fractional, then do the
            difference, then build my change up out of that out of a fresh pile
            of coins
    """
    me = frac_coin( mine, 'cp' )
    yu = frac_coin( cost, 'cp' )

    if me < yu:
        return False

    cp_change = me - yu
    change = {}

    # from largest to smallest
    cp_vals = [{'n':v,'v':frac_coin({v:1}, 'cp')} for v in ('pp','ep','gp','sp','cp')]
    for cp_value in cp_vals:
        debit = cp_change // cp_value['v']
        if debit > 0:
            change[ cp_value['n'] ] = debit
            cp_change = cp_change - cp_value['v'] * debit

    return change

def money_toString( o ):
    s = '('
    for t in ('cp','sp','gp','ep','pp'):
        if o.get(t):
            s += '{}: {}, '.format(t,o[t])
    s = s.rstrip()
    if s[-1] == ',':
        s = s[:-1]
    s = s + ') = {}gp'
    return s.format(frac_coin(o))

#
def number_end( num ):
    if num > 10 and num < 20:
        return str(num) + 'th'
    s = str(num)
    o = str(num)[-1]
    if o == '1':
        return s + 'st'
    elif o == '2':
        return s + 'nd'
    elif o == '3':
        return s + 'rd'
    else:
        return s + 'th'

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

def char_for_name( name ):
    for r in roster:
        if r.data['name'] == name:
            return r
    return False

def fmt_item( item ):
    name = [k for k in item.keys()][0]

    s = '"{}", '.format( name )

    for k, v in item[name].items():
        s = s + '{} {}, '.format( k, v )

    return s.rstrip()[:-1]


def getint( text ):
    if text[-1] != ' ':
        text = '{} '.format( text )
    val = input( text )
    try:
        i = int( val.lstrip().rstrip() )
        return i
    except:
        return False

def yn( text, default_action='n' ):
    suffixen = {'y':'[Y/n]','n':'[y/N]'}
    val = input( '{} {}: '.format(text,suffixen[default_action]) )
    if default_action.lower() == 'y':
        return not(val.upper() == 'N')
    else:
        return val.upper() == 'Y'

def ynq( text, default_action='n' ):
    suffix = '[';
    for letter in ('y','n','q'):
        if letter.upper() == default_action.upper():
            suffix += letter.upper() + '/'
        else:
            suffix += letter.lower() + '/'
    suffix = suffix[:-1] + ']'

    val = input( '{} {}: '.format(text, suffix) )

    if not val or len(val) == 0:
        return {'y':True,'n':False,'q':None}.get(default_action.lower(),False)

    if val.upper() == 'Q':
        return None
    return val.upper() == 'Y'

def fmt_attrib( attribs ):
    s = ''
    for a in attribs_ordered:
        s += '{}: {}, '.format( a, attribs[a] )
    return s.rstrip()[:-1]

def text_question( prompt, default='leave blank to skip' ):
    while True:
        if default:
            inp = input( '{} ({})> '.format(prompt,default) )
        else:
            inp = input( '{}> '.format(prompt) )
        inp = inp.rstrip().lstrip()
        if len(inp) == 0:
            ans = yn( 'Leave blank?', 'y' )
            if ans:
                return False
        ans = ynq( 'You wrote: "{}". Keep?'.format(inp), 'y' )
        if inp:
            return inp

def SubMenu( options, header='', prompt='select>', random_noprompt=False, return_obj=False, custom=False, default=False, exit=True, quit=True, padding=False ):
    """ takes a list,
        X prints a header
        X prints an arbitary length list of options
        X handles console window height run-overs
        X adds on: e) exit menu, q) quit to main, c) custom input
        X print a 'prompt> '
        X gets input, checks for int or option, loops until exit-condition is met, returns a string
        - prints summary of currently selected items
        - enums, so the caller knows if it is supposed to return
        X handles different behaviors, so that all the character class
            eventualities are handled
        - takes 'random=1', so that prompt is skipped and random number
            is selected
        X can be reused in CREATOR, EDITOR, AUTO-GENERATOR
    """

    prompt = prompt.rstrip()
    if default:
        prompt = prompt.replace('>', ' (default: {})>'.format(default) )
    if prompt[-1] != ' ':
        prompt = '{} '.format(prompt)

    padding_rows = padding if padding else 6

    while True:
        if header:
            print( header )

        # prepare for paged print
        term_row_printing = 0
        index_into_dataset = 0
        term_height, _ = terminal_size()

        while index_into_dataset <= len(options):

            if index_into_dataset < len(options):
                option = options[index_into_dataset]

            # terminal screen is full, or at end of list
            if term_row_printing >= ( term_height - padding_rows ) or index_into_dataset >= len(options):
                term_row_printing = 0

                if index_into_dataset < len(options) - 1:
                    print('-------MORE-------')
                else:
                    print('')

                # print the menu and prompt
                if len(options) >= (term_height - padding_rows):
                    print( ' p) show previous screen' )
                if exit:
                    print( ' e) exit to previous menu' )
                if quit:
                    print( ' q) quit to the previous menu' )
                if custom:
                    print( ' c) enter custom type' )

                if index_into_dataset < len(options) - 1:
                    print( '*Enter) Next page' )

                ans = input( prompt ).rstrip().lstrip()
                if ans.lower() == 'p':
                    index_into_dataset = max( index_into_dataset - 2 * ( term_height - padding_rows ), 0 )
                    continue
                elif ans == "":
                    if index_into_dataset == len(options):
                        break
                    else:
                        continue
                else:
                    break

            if type(option) is type({}):
                option = fmt_item( option )
            print( ' {}: "{}"'.format(index_into_dataset, option) )

            term_row_printing = term_row_printing + 1
            index_into_dataset = index_into_dataset + 1


        if custom and ans == 'c':
            while True:
                txt = input( 'enter custom> ' )
                if txt:
                    if txt == 'e':
                        return False
                    elif txt == 'q':
                        return None
                    return txt

        if ans == 'e':
            return False
        elif ans == 'q':
            return None
        else:
            if not ans and default:
                return default
            try:
                iv = int(ans)
            except:
                print( 'invalid selection' )
                time.sleep( sleep_time )
                continue
            if iv < 0 and iv >= len(options):
                print( 'invalid selection' )
                time.sleep( sleep_time )
                continue
            return options[ iv ]

