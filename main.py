#!/usr/bin/env python3
import json
import random
import os
import time
import sys
import datetime

from utils import *

messages = []

# directories
if os.name == 'nt':
    datadir = os.environ['LOCALAPPDATA' if os.name == 'nt' else 'HOME'] + '\\dnd'
else:
    datadir = os.environ['LOCALAPPDATA' if os.name == 'nt' else 'HOME'] + '/.dnd'

logfile_path = datadir + '/dndman.log'

roster = []
DEBUG = True
config = {}
sleep_time = 0.45
msg_time = 0.6

defconfig = """{{
    "rolls" : [
        "3d6",
        "1d12 + 6",
        "2d6 + 6",
        "4d6 drop lowest"
    ],
    "default_attrib_roll_method" : 0,
    "sleep_time": {},
    "msg_time" : {}
}}
""".format(sleep_time, msg_time)

# data sheets to load
equipment = {}
character = {}
world = {}
tables = {}

main_menu_string = """First Edition Dungeons & Dragons Character Management Tool.
Options are:
 (L) List Characters
 (C) Create a New Character
 (E) Edit a Character
 (G) Generate Character Randomly
 (D) Delete a Character
 (R) Roll Methods
 (Q) Quit
Your Selection> """





def create_character():
    """This is the primary interface that allows a player to roll, generate, or manually enter in a character"""
    char = CharacterSheet()
    attribs = char.data['attribs']
    d = char.data
    dice = RandomDiceRoller()

    # NAME
    while True:
        ans = input( "What is your character's NAME? " )
        if not ans:
            print( "--can't be empty string--" )
            continue
        elif ans == 'q':
            return False
        existingChar = char_for_name( ans )
        if existingChar is not False:
            hmm = yn( '"{}" exists already. Overwrite?'.format(ans) )
            if not hmm:
                continue
        hmm = ynq( 'Character\'s Name is: "{}", keep? '.format(ans), 'y' )
        if hmm is None:
            return False
        elif hmm:
            break
    char.data['name'] = ans
    Message( 'Name: "{}"'.format(d['name']) )

    # ATTRIBUTES
    while True:
        auto_roll = ynq( 'Would you like your ATTRIBUTES to be rolled for you?', 'y' )
        if auto_roll is None:
            return False

        elif auto_roll:
            roll_method = config['rolls'][ config['default_attrib_roll_method'] ]
            print( 'Using dice method: "{}"'.format( roll_method ) )
            for a in attribs_ordered:
                attribs[a] = dice.roll( roll_method )
            print( 'rolled: {}'.format( fmt_attrib( attribs ) ) )
            if yn( 'keep?', 'y' ):
                break
        else:
            print( "Enter Attributes Manually:" )
            for a in attribs_ordered:
                while True:
                    atr = getint( "-Enter {} ? ".format(a.upper()) )
                    if not atr:
                        print( "Bad value. Use integer only." )
                        continue
                    attribs[a] = atr
                    break
            if yn( 'entered: {}, keep? '.format( fmt_attrib( attribs ) ), 'y' ):
                break
    Message( 'Character has attributes: {}'.format( fmt_attrib( attribs ) ) )

    # RACE
    while True:
        ans = SubMenu( sorted( character['races'].keys() ), "Select a RACE: ", custom=True, exit=False, default='Human' )
        if ans is None:
            return False
        if ans:
            keep = ynq( 'selected: "{}", keep?'.format( ans ), 'y' )
            if keep is None:
                return False
            elif keep:
                break
    d['race'] = ans
    Message( 'Race is: "{}"'.format( d['race'] ) )

    # SEX
    while True:
        ans = SubMenu( ['Male', 'Female'], 'What SEX is "{}"?'.format(d['name']), custom=True, exit=False, default='Male' )
        if ans is None:
            return False
        if ans:
            keep = ynq( 'selected: "{}", keep?'.format( ans ), 'y' )
            if keep is None:
                return False
            elif keep:
                break
    d['sex'] = ans
    Message( 'got sex: "{}"'.format( d['sex'] ) )

    # ALIGNMENT
    while True:
        ans = SubMenu( character['alignments'], 'What ALIGNMENT is "{}"? '.format(d['name']), custom=True, exit=False, default='Neutral Good' )
        if ans is None:
            return False
        if ans:
            keep = ynq( 'selected: "{}", keep?'.format( ans ), 'y' )
            if keep is None:
                return False
            elif keep:
                break
    d['alignment'] = ans
    Message( 'got alignment: "{}"'.format( d['alignment'] ) )

    # CLASS
    while True:
        ans = SubMenu( sorted( list( character['classes'].keys() ) ), 'Select a CLASS', custom=True, exit=False, default='Fighter' )
        if ans is None:
            return False
        if ans:
            keep = ynq( 'selected: "{}", keep?'.format( ans ), 'y' )
            if keep is None:
                return False
            elif keep:
                break
    d['class'] = ans
    Message( 'got class: "{}"'.format( d['class'] ) )

    # LEVEL
    while True:
        ans = getint( 'What LEVEL is "{}" (default: 1)> '.format(d['name']) )
        if ans is False:
            ans = 1
        keep = ynq( 'selected: "{} Level", keep?'.format( number_end(ans) ), 'y' )
        if keep is None:
            return False
        elif keep:
            break
    d['level'] = ans
    Message( '{} is "{} level"'.format( d['name'], number_end( d['level'] ) ) )

    # HIT_DICE (manual only for custom class)
    if d['class'] in character['classes']:
        d['HD'] = character['classes'][ d['class'] ]['HD']
        d['SHD'] = character['classes'][ d['class'] ]['SHD']
    else:
        d['HD'] = d['SHD'] = input( 'enter hit-dice for custom class (eg. d6, 1d8, d10)> ' )

    # HIT_POINTS (roll hit dice)
    while True:
        done = False
        print( '{} uses hit-dice "{}" with starting hit-die "{}"'.format( article(d['class']), d['HD'], d['SHD'] ) )
        autoroll_hp = ynq( 'Would you like your HIT POINTS to be rolled for you?', 'y' )
        if autoroll_hp is None:
            return False
        if autoroll_hp:
            while True:
                hp = []
                hp.extend( dice.roll( d['SHD'], separate=True ) )
                i = 2
                while i <= d['level']:
                    hp.append( dice.roll( d['HD'] ) )
                    i = i + 1
                print( '{} level rolled: '.format(number_end(d['level'])), end='' )
                for h in hp[:-1]:
                    print( str(h) + ' +', end=' ' )
                print( '{} = {}'.format( str(hp[-1]), sum(hp) ) )
                ans = yn( 'keep?', 'y' )
                if ans:
                    d['hp'] = sum(hp)
                    done = True
                    break
                else:
                    break # n or q exit to higher loop
            if done:
                break
        else:
            hp = getint( 'enter hitpoints > ' )
            if not hp:
                print( ' *not integer' )
                continue
            ans = yn( 'got: {}, keep?'.format(hp), 'y' )
            if ans:
                d['hp'] = hp
                break
    Message( 'The {} has {} hit points'.format( d['class'], d['hp'] ) )

    # AGE
    # use Dwarf for non-standard character race
    while True:
        done = False
        ans = ynq( 'Would you like {}\'s AGE rolled for you?'.format(d['name']), 'y' )
        if ans is None:
            return False
        if not ans:
            age = getint( 'Enter {}\'s age in years? '.format(d['name']) )
            if not age:
                continue
            keep = ynq( 'got {} years of age, keep?'.format(age), 'y' )
            if keep is None:
                return False
            elif keep:
                d['age'] = age
                break
        else:
            race = d['race'] if d['race'] in character['races'] else 'Dwarf'
            # use Cleric as default for non-book classes
            className = d['class'] if d['class'] in character['classes'] else 'Cleric'
            if race != 'Human':
                # demi-humans only have tables by super-class
                className = character['subclass-membership'][ className ]
            dieroll = character['starting-age'][race][className]
            while True:
                years = dice.roll( dieroll )
                ans = ynq( '{} rolls "{}" for {} years starting age, keep?'.format( article(d['race']), dieroll, years ), 'y' )
                if ans is None:
                    break # quit upwards to higher loop
                if ans:
                    d['age'] = years
                    done = True
                    break
            if done:
                break
    Message( '{} is {} years old'.format( d['name'], d['age'] ) )

    # STARTING MONEY
    if d['class'] in character['classes']:
        starting_money = character['classes'][ d['class'] ]['starting_money']
    else:
        starting_money = '1d10 x 10'
    while True:
        ans = ynq( 'Would you like {}\'s STARTING MONEY rolled for you?'.format(d['name']), 'y' )
        if ans is None:
            return False
        if ans:
            print( '{} starts with "{}" gp'.format( d['class'], starting_money ) )
            gp = dice.mult( starting_money )
            ans = yn( 'Rolled {} gp, keep? '.format( gp ), 'y' )
            if ans:
                d['money'] = {'cp':0,'sp':0,'gp':gp,'ep':0,'pp':0}
                break
        else:
            gp = getint( 'How many gold pieces? ' )
            if not gp:
                continue
            keep = yn( 'got {} gp, keep?'.format(gp), 'y' )
            if keep:
                d['money'] = {'cp':0,'sp':0,'gp':gp,'ep':0,'pp':0}
                break
    Message( '{} got {} gp'.format( d['name'], gp ) )


    # WEAPON PROFICIENCIES
    prof = character['classes'].get( d['class'], {'wp': {"inw":2,"npp":-3,"ppl":4}} )['wp']
    total = prof['inw'] + d['level'] // prof['ppl']
    print( 'Character of class {} gets {} WEAPON PROFICIENCIES at 1st level, and one more every {} levels (as per PHB p.37). Thus a {} level {} gets {} proficiencies total'.format( d['class'], prof['inw'], prof['ppl'], number_end(d['level']), d['class'], total ) )
    time.sleep( sleep_time * 2 )

    msg_string = 'Select a Weapon-Proficiency (quit when done)'
    while True:
        weapon = SubMenu( [k for k in sorted(equipment['Arms'].keys())], msg_string , custom=True, exit=False, padding=11 )
        if not weapon:
            break
        if len(msg_string) == 44:
            msg_string = '{}\nGot so far: '.format(msg_string)
        msg_string = '{} "{}",'.format(msg_string, weapon)
        d['proficiencies'].append( weapon )
        print( 'Adding {}'.format(weapon) )
        time.sleep( sleep_time )

    d['proficiencies'] = list(set(d['proficiencies']))
    if d['proficiencies']:
        Message( '{} is proficient in: {}'.format( d['name'], arraystr( d['proficiencies'] ) ) )
    else:
        Message( '{} has no weapon proficiencies'.format( d['name'] ) )

    # KNOWN SPELLS
    #   - print the 1e suggested # of spells known for class & level
    #   - optionally write in 1 or more spells, ask: {name, level}
    #   - select spells known from nested lists
    #       - magic user | illusionist | druid | Cleric
    #           - Level
    #               - Spell
    #   - randomly compute the known spells for class & level

    # STEPS
    # *determine if the class gets spells
    spell_classes = character['classes'].get( d['class'], {} ).get( 'spells', {} )
    for class_name, level_spells in spell_classes.items():
        spells_can_memorize = level_spells[ d['level'] - 1 ]
        print( 'At {} Level, {} gets:'.format( number_end(d['level']), article(d['class'],0) ) )
        for lvl_m1, number in enumerate( spells_can_memorize ):
            level = lvl_m1 + 1
            print( ' - {} {} level {} spells'.format( number, number_end(level), class_name ) )

    # *if so, determine # known
    # *if mu, give "read magic" as 1st

    # SELECT DIETY
    # - text entry
    while True:
        diety = input( 'What is their DIETY? (Default: None)> ' )
        if not diety:
            ans = ynq( 'skip diety?', 'y' )
            if ans is None:
                return False
            if ans:
                break
        ans = ynq( 'Diety is "{}". Keep? '.format( diety ), 'y' )
        if ans is None:
            return False
        if ans:
            char.data['diety'] = diety
            break
    Message( '{} worships {} '.format( d['name'], d.get('diety','nobody') ) )


    # HEIGHT
    while True:
        # FEET
        feet = getint( 'What is their HEIGHT?\n-Feet (default: 5\')> ' )
        if feet is False:
            feet = 5

        # INCHES
        inch = getint( '-Inches (default: 10")> ' )
        if inch is False:
            inch = 10

        ans = ynq( 'Height is {}\' {}". Is this correct? '.format(feet,inch), 'y' )
        if ans is None:
            return False
        if ans:
            d['height'] = {'feet':feet, 'inches':inch}
            break
    Message( '{} is {} '.format( d['name'], d['height'] ) )


    # WEIGHT
    while True:
        # LBS
        lbs = getint( 'What is their WEIGHT?\n-Lbs (default: 120)> ' )
        if lbs is False:
            lbs = 120
        ans = ynq( 'Weight is {} lbs. Is this correct? '.format(lbs), 'y' )
        if ans is None:
            return False
        if ans:
            d['weight'] = lbs
            break
    Message( '{} is {} lbs'.format( d['name'], d['weight'] ) )


    # KNOWN LANGUAGES
    # - print how many the character can know based on INT score (PHB)
    # - present a list, with writein (custom) option
    print( 'Determining KNOWN LANGUAGES' )
    if d['race'] in character['races']:
        xtra = character['races'][ d['race'] ]['lang']
        d['languages'].append( xtra )
    d['languages'] = list(set(d['languages']))
    Message( "Character knows {} to start".format(arraystr(d['languages'])) )

    INT = d['attribs']['int']
    if INT >= 1 and INT <= 18:
        additional_languages = character['additional_languages'][ INT - 1 ]
    else:
        additional_languages = 0
    if additional_languages > 0:
        languages_table = RandomTable( tables[ "random_language" ] )
        while True:
            print( 'Character with {} Intelligence gets {} additional languages'.format(INT, additional_languages) )
            rolled_for_you = ynq( 'Would you like languages rolled for you?', 'y' )
            if rolled_for_you is None:
                return False

            langs = []

            # rolled
            if rolled_for_you:
                while True:
                    newlan = languages_table.roll()
                    while newlan in d['languages']:
                        newlan = languages_table.roll()
                    langs.append( newlan )
                    langs = list(set(langs))
                    if len(langs) >= additional_languages:
                        break
                ans = ynq( 'Got: {}, keep?'.format(arraystr(langs)), 'y' )
                if ans is None:
                    break
                if ans:
                    d['languages'].extend(langs)
                    break

            # select from list
            else:
                # select from list
                while True:
                    lang_list = [l['val'] for l in tables['random_language']['table']]
                    lang = SubMenu( sorted(lang_list), 'Add a language' )
                    if not lang:
                        break
                    if lang in d['languages'] or lang in langs:
                        print( 'They already know {}!'.format(lang) )
                        time.sleep( sleep_time * 2 )
                        continue
                    langs.append( lang )
                    print( 'Selected "{}"'.format(lang) )
                    time.sleep( sleep_time * 2 )
                    if len(langs) >= additional_languages:
                        print( 'Done adding languages')
                        time.sleep( sleep_time * 2 )
                        break
                ans = ynq( 'Got: {}, keep?'.format(arraystr(langs)), 'y' )
                if ans:
                    d['languages'].extend(langs)
                    d['languages'] = list(set(d['languages']))
                    break

    Message( '{} knows: {}'.format(d['name'], arraystr(d['languages'])) )


    # NON-WEAPON-PROFICIENCIES
    # - suggest how many per-level per-DMG
    # - present a list, with write in option,
    # - can add as many as they want


    # FAMILY BACKGROUND
    # - text entry
    ans = text_question( 'Enter some family background about your character' )
    if ans:
        Message( 'Character\'s background: {}'.format(a) )
        d['background'] = ans
    else:
        Message( 'no background' )

    # NEXT OF KIN
    # - text entry
    ans = text_question( 'Next of kin?' )
    if ans:
        Message( 'Next of kin: {}'.format(ans) )
        d['next_of_kin'] = ans
    else:
        Message( 'no next of kin' )

    # HOME CITY
    # - text entry, default: "Greyhawk"
    ans = text_question( 'What is their home town?', 'default: Greyhawk' )
    d['home_town'] = ans if ans else 'Greyhawk'
    Message( 'Home town: {}'.format(d['home_town']) )

    #--------------------
    # note race modifiers
    # note saving throws
    # note class modifiers
    # note proficiency modifiers
    #--------later-------
    # EQUIP CHARACTER
    # ARMOR CLASS (calculated on equip automatically)
    # GEAR WEIGHT (calculated on equip automatically)
    # BASE MOVEMENT RATE (calculated on gear weight change)
    #--------------------
    char.save()
    Message('Congratulations, you have created:\n{}'.format( char.toString() ) )
    return char

def autogen_character():
    """this creates an entire character, completely randomly, including name"""
    char = CharacterSheet()
    attribs = char.data['attribs']
    dice = RandomDiceRoller()
    for a in attribs_ordered:
        attribs[a] = dice.roll( config['rolls'][ config['default_attrib_roll_method'] ] )
    char.data['name'] = input( "Enter the character name: " )
    return char

def shop_at_the_store( char ):
    while True:
        print( '\n{} has {}'.format( char['name'], money_toString( char['money'] ) ) )
        etype = SubMenu( sorted(equipment.keys()), 'What category would you like to peruse?', custom=False )
        if etype is None:
            return
        elif etype is False:
            break

        while True:
            player_money = '{} has {}'.format( char['name'], money_toString( char['money'] ) )
            item = SubMenu( [{ k: v } for k, v in sorted(equipment[etype].items())], player_money+"\nShopkeeper has these for sale. Which would you like to purchase?", custom=False, exit=False )
            if item:
                item_name = [k for k in item.keys()][0]
                subitem = item[item_name]
                amt, kind = subitem['cost'].split(' ')
                print( '"{}" costs {}'.format( item_name, subitem['cost'] ) )
                print( '{} has {}'.format( char['name'], money_toString( char['money'] ) ) )
                change = make_change( char['money'], {kind:amt} )
                if not change:
                    print('\nYou do not have enough for that!\n')
                    continue
                confirm = ynq( 'Are you sure you want to buy "{}"? '.format(item_name), 'y' )
                if config is None:
                    return
                if not confirm:
                    continue
                char.data['money'] = change
                char['inventory'].append(item)
                char.save()
                Message( 'You bought a "{}"!\nCoins remaining: {}'.format( item_name, money_toString(change) ) )
            elif item is None:
                return
            else:
                break


def delete_character_menu():
    global roster
    print('')
    def print_names():
        print('Pick a character to DELETE:')
        for i, character in enumerate(roster):
            print( ' {}: "{}"'.format( i, character.toString() ) )
        print( '\n e] exit back to main menu' )
    while True:
        if len(roster) == 0:
            print( 'Character roster empty' )
            break
        print_names()
        inp = input( 'select> ' )
        if inp == 'e':
            break
        try:
            ival = int(inp)
        except:
            print( 'bad option, not integer' )
            continue
        hmm = yn( 'delete character "{}", are you sure?'.format(roster[ival].data['name']) )
        if not hmm:
            print( 'ok, not deleting. good choice' )
            continue
        name = roster[ival].data['name']
        print( 'deleting "{}"...'.format(roster[ival].data['name']) )
        roster = roster[:ival] + roster[ival+1:]
        os.unlink( datadir + '/characters/' + name )

def configure_rolling_method():
    global config
    def print_menu():
        print( 'stored attribute rolling methods:' )
        for i, r in enumerate(config['rolls']):
            d = '-' * 10 + 'default' if i == config['default_attrib_roll_method'] else ''
            print( " {}: '{}' {}".format( i, r, d ) )
        print( '\n n] add a new method' )
        print( ' d] delete a method' )
        print( ' s] set default' )
        print( ' e] exit to the main menu' )
    while True:
        if len(config['rolls']) == 0:
            print( 'Warning: No stored roll method available. Could cause errors.' )
            break
        print_menu()
        o = input( 'select> ' )
        if o == 'e' or o == 'q':
            break
        if o == 'n':
            print( 'Add New roll method.\nCan be of the types: "d20", "2d4", "3d6 + 10", "2d4 + 3d12", or "4d6 drop lowest"' )
            m = input( 'enter method> ' )
            config['rolls'].append(m)
            write_config()
        elif o == 'd':
            i = getint( 'delete which roll method? ' )
            config['rolls'] = config['rolls'][:i] + config['rolls'][i+1:]
            write_config()
        elif o == 's':
            config['default_attrib_roll_method'] = getint( 'set which as default? ' )
            write_config()
        else:
            print( 'unknown selection' )

def load_data():
    fh = open( './data/phb_equipment.json', 'r' )
    global equipment
    equipment = json.load( fh )
    fh.close()

    fh = open( './data/phb_character.json', 'r' )
    global character
    character = json.load( fh )
    fh.close()

    fh = open( './data/phb_world.json', 'r' )
    global world
    world = json.load( fh )
    fh.close()

    fh = open( './data/phb_tables.json', 'r' )
    global tables
    tables = json.load( fh )
    fh.close()


def list_characters():
    print()
    if len(roster) == 0:
        print( '\n  no characters\n' )
        time.sleep( sleep_time * 2 )
    for i, c in enumerate(roster):
        print( ' {}: {}'.format(i, c.toString()) )
    print()

def check_cmdline_args():
    args = sys.argv[1:]
    for l in ('list','-l','l'):
        if l in sys.argv[1:]:
            list_characters()
            sys.exit(0)
    for c in ('-c','char','character'):
        if c in args:
            try:
                iv = args.index(c) + 1
                if iv >= len(args):   # will throw
                    print( 'invalid argument' )
                    sys.exit(121)
                iv = int(args[iv])
                if iv >= len(roster):
                    sys.exit(123)
                print( roster[iv].gen_character_sheet() )
                sys.exit(0)
            except:
                print( 'invalid argument' )
                sys.exit(122)

def edit_inventory( char ):
    while True:
        print( '\nEditing: "{}", Inventory:'.format(char['name']) )
        if char['inventory']:
            for index, item in enumerate(char['inventory']):
                if type(item) is type({}):
                    item = fmt_item( item )
                print( ' {}: {}'.format( index, item ) )
        else:
            print('* no items')

        ans = input("""\n A)dd new item\n S)hop at The Players Handbook Store\n D)elete item\n Q)uit to previous menu\nselect> """)
        if ans.lower() == 'q':
            break
        elif ans.lower() == 's':
            shop_at_the_store( char )

        elif ans.lower() == 'a':
            while True:
                item = input( 'Enter Item: ' )
                if not item:
                    print('\nbad input (q to quit)')
                    continue
                if item.lower() == 'q':
                    break
                char['inventory'].append(item)
                char.save()
                Message( '"{}" gets {} "{}"'.format(char['name'], article(item,False), item) )
                break

        elif ans.lower() == 'd':
            index = getint( 'delete which> ' )
            if index is False:
                print( '\nskipping' )
                continue
            if index < 0 or index >= len(char['inventory']):
                print( '\ninvalid selection' )
                time.sleep( sleep_time )
                continue
            item = char['inventory'][index]
            if type(item) is type({}):
                item = [k for k in item.keys()][0]
            char.data['inventory'] = char['inventory'][:index] + char['inventory'][index+1:]
            char.save()
            Message( '"{}" dropped "{}"'.format( char['name'], item ) )
        else:
            print('\ndo not understand command')

def edit_attributes( char ):
    print( '\nnot yet' )
    time.sleep( sleep_time )
    # NAME
    # ATTRIBUTES
    # RACE
    # SEX
    # ALIGNMENT
    # CLASS
    # LEVEL
    # HIT_DICE
    # HIT_POINTS
    # AGE
    # STARTING_MONEY
    # WEAPON_PROFICIENCIES
    # KNOWN_SPELLS
    # DIETY
    # HEIGHT
    # WEIGHT
    # LANGUAGES
    # NON WEAPON PROFICIENCIES
    # FAMILY BACKGROUND
    # NEXT OF KIN
    # HOME CITY

def edit_character():
    while True:
        name = SubMenu( sorted([r.data['name'] for r in roster]), '\nEdit which character?', exit=False, default=None, custom=False )
        if not name:
            return

        char = char_for_name( name )
        if not char:
            print( '\n{} not found!'.format(name) )
            continue

        while True:
            actions = [
                'Attributes',
                'Inventory'
            ]
            act = SubMenu( actions, '\nEditing "{}". Which category?'.format(name) )
            if act is None:
                return
            if not act:
                break

            if act == 'Attributes':
                edit_attributes( char )
            elif act == 'Inventory':
                edit_inventory( char )

def ensure_datadir():
    if not os.path.exists(datadir):
        os.mkdir( datadir )
    if not os.path.exists(datadir+'/characters'):
        os.mkdir( datadir+'/characters' )
    if not os.path.exists( datadir + '/config' ):
        with open( datadir + '/config', 'w' ) as f:
            f.write( defconfig )

def read_config():
    global config
    global sleep_time
    global msg_time
    with open( datadir + '/config', 'r' ) as f:
        config = json.loads(f.read())
    sleep_time = config.get('sleep_time', sleep_time)
    msg_time = config.get('msg_time', msg_time)

def write_config():
    with open( datadir + '/config', 'w' ) as f:
        f.write( json.dumps( config, indent=2, sort_keys=True ) )

def load_roster():
    global roster
    character_filepaths = list_dir( datadir + '/characters' )
    for path in character_filepaths:
        with open( path, 'r' ) as f:
            roster.append( CharacterSheet( json.load(f) ) )


##################################################################
#
# entry point
#
##################################################################
ensure_datadir()
read_config()
load_roster()
load_data()

log = logger( logfile_path )

check_cmdline_args()

op = ''
while op != 'q' and op != 'Q':

    op = input( main_menu_string )

    if op.upper() == 'L':                      # list
        list_characters()

    elif op.upper() == 'E':                    # edit character
        edit_character()

    elif op.upper() == 'C':                    # create
        print( 'Creating a Player Character' )
        char = create_character()

    elif op.upper() == 'G':                    # generate
        print( 'Generating a Player Character' )
        char = autogen_character()
        char.print()
        ans = yn( 'keep this character?' )
        if ans:
            char.save()

    elif op.upper() == 'D':                    # delete
        delete_character_menu()

    elif op.upper() == 'R':                    # rolling method
        configure_rolling_method()

    elif op.upper() == 'Q':                    # quit
        break

    else:
        print( "Command Unknown" )

print( 'goodbye' )

