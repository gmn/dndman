

class CharacterSheet:
    def __init__( self, blob = False ):
        self.data = blob if blob is not False else default_character

    def __getitem__( self, index ):
        return self.data[ index ]

    def save( self ):
        # write to disk
        with open( datadir + '/characters/' + self.data['name'], 'w' ) as f:
            f.write( json.dumps( self.data, indent = 2, sort_keys=True ) )
        # update roster
        global roster
        for c in roster:
            if c.data['name'] == self.data['name']:
                c.data = self.data
                return
        roster.append( self )

    def load( self ):
        pass

    def LevelName( self ):
        class_names = character['classes']
        if self.data['class'] in class_names:
            if self.data['level'] >= len( class_names[ self.data['class'] ]['names'] ):
                return class_names[ self.data['class'] ]['names'][-1] + ' (' + number_end( self.data['level'] ) + ' Level)'
            else:
                return class_names[ self.data['class'] ]['names'][ self.data['level'] - 1 ]
        return self.data.get( 'class' )

    def fmt_attrib( self ):
        return fmt_attrib( self.data['attribs'] )

    def short_attrib( self ):
        attribs = self.data['attribs']
        s = ''
        for a in attribs_ordered:
            s += '{}, '.format( attribs[a] )
        return s.rstrip()[:-1]

    def print( self ):
        print( self.toString() )

    def toString( self ):
        race = self.data['race']
        if race in character['races']:
            race = character['races'][ race ]['pl']
        # Barney the Prestidigitator, Lv 1 Fighter: 16 14 13 12 16 12, ( 144 gp )
        return '"{}" the {}, Lv {} {} {}: {}'.format( self.data['name'], self.LevelName(), self.data['level'], race, self.data['class'], self.short_attrib() )

    def gen_character_sheet( self ):
        d = self.data
        race = d['race']
        if race in character['races']:
            race = character['races'][ race ]['pl']
        s = '\n "{}" the {}, Lv {} {} {}\n\n'.format( d['name'], self.LevelName(), d['level'], race, d['class'] )
        for a in attribs_ordered:
            s += '  {}: {}\n'.format( a.upper(), d['attribs'][a] )
        if d['inventory']:
            s += '\n Inventory:\n'
        for item in d['inventory']:
            if type(item) is type({}):
                item = fmt_item( item )
            s += ' - {}\n'.format( item )
        return s


