world = {
    "exchange_rate" : {
        "cp" : {
            "cp" : 1,
            "sp" : 0.1,
            "ep" : 0.01,
            "gp" : 0.005,
            "pp" : 0.001
        },
        "sp" : {
            "cp" : 10,
            "sp" : 1,
            "ep" : 0.1,
            "gp" : 0.05,
            "pp" : 0.01
        },
        "ep" : {
            "cp" : 100,
            "sp" : 10,
            "ep" : 1,
            "gp" : 0.5,
            "pp" : 0.1
        },
        "gp" : {
            "cp" : 200,
            "sp" : 20,
            "ep" : 2,
            "gp" : 1,
            "pp" : 0.2
        },
        "pp" : {
            "cp" : 1000,
            "sp" : 100,
            "ep" : 10,
            "gp" : 5,
            "pp" : 1
        }
    }
}

def exchange( it, quantity, ot ):
    io = world['exchange_rate'][it][ot]
    return io * quantity

# display the value of a mixed group of coins in terms of one type of coin
def frac_coin( money, kind='gp' ):
    tot = 0
    for t in ('cp','sp','gp','ep','pp'):
        if t in money:
            tot = tot + exchange( t, money[t], kind )
    return tot

def consolidate_coin_value(o):
    """turn all money into cp,
        then build the cp up into the minimum number of large value coins"""
    pass

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
    print( mine, ' ', cost )
    print( me, ' ', yu )

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

    print( str(change) )
    return change

cp_vals = [{v:frac_coin({v:1}, 'cp')} for v in ('pp','ep','gp','sp','cp')]
import json
print( json.dumps(cp_vals,indent=2) )
change = make_change( {'sp':20, 'gp':20, 'pp':1}, {'cp':900, 'gp':1} )
print( frac_coin( change, 'cp' ) )
