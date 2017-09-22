#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
docstring goes here
'''
from __future__ import print_function
import curses
import locale
import sys
import soco


locale.setlocale(locale.LC_ALL, '')
ENCODING = locale.getpreferredencoding()
ARROW_UP = u'\u2191'.encode(ENCODING) # ↑
ARROW_RT = u'\u2192'.encode(ENCODING) # ↓
ARROW_DN = u'\u2193'.encode(ENCODING) # ↓

SCREEN = curses.initscr()
curses.cbreak()
curses.halfdelay(10)
curses.noecho()
SCREEN.keypad(1)
STARTLINE = 6
STARTCOL = 10

SPEAKERS = soco.discover()
SPEAKER_NAMES = [s.player_name for s in SPEAKERS]
PLAYER = [x for x in SPEAKERS if x.player_name.lower() == 'office'][0]

FAVORITES = sorted(PLAYER.get_sonos_favorites()['favorites'])
FAVORITE_NAMES = [f['title'] for f in sorted(FAVORITES)]
# I haven't figured out where to pull the current channel, so we start
# with 'Unknown', and update it when we change things
CHANNEL_NAME = 'Unknown'
HR = 60 * '-'

def print_error(*args, **kwargs):
    ''' an easy way to print to stderr
    '''
    print(*args, file=sys.stderr, **kwargs)

def drawchooserpad(choice_type):
    ''' enable a user to choose a channel from sonos faves.
    '''
    #menupad = SCREEN.subpad(len(FAVORITES) + 8, 60, 4, 4)
    menupad = SCREEN.subpad(4, 4)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
    menupad.keypad(1)
    pos = 1
    menupad.refresh()
    choice = None
    selection = False
    option_set = []

    while choice != ord('\n'):
        if choice in [27, ord('q')]:
            return 'nochoice'
        if choice_type == 'speakers':
            option_header = 'Available Sonos Speakers:'
            option_set = SPEAKER_NAMES
        elif choice_type == 'favorites':
            option_header = 'Sonos Favorites:'
            option_set = FAVORITE_NAMES

        menupad.clear()
        menupad.border(0)
        menupad.addstr(2, 2, option_header, curses.A_STANDOUT)
        menupad.addstr(4, 2, "Please select an option...", curses.A_BOLD)
        cpair1 = curses.color_pair(1)
        cpair2 = curses.A_NORMAL
        cidx = 0
        for option in option_set:
            cidx += 1
            colorset = cpair1 if pos == cidx else cpair2
            try:
                menupad.addstr(STARTLINE + cidx, STARTCOL, option, colorset)
            except Exception, err:
                print_error('got error: ' + str(err))

        for _ in xrange(len(option_set)):
            if choice == _:
                pos = _
        if choice == 258:
            pos += 1 if (pos < len(option_set)) else 1
        elif choice == 259:
            pos -= 1 if (pos > 1) else len(option_set)
        choice = menupad.getch()

    selection = option_set[pos-1]
    if choice_type == 'speakers':
        try:
            selected = [p for p in SPEAKERS if p.player_name == selection][0]
        except Exception:
            pass
    elif choice_type == 'favorites':
        try:
            print_error("got favorites selection for " + selection)
            new_fave = [c for c in sorted(FAVORITES) if c['title'] == selection][0]
            PLAYER.play_uri(uri=new_fave['uri'], meta=new_fave['meta'], start=True)
            selected = new_fave['title']
        except soco.exceptions.SoCoUPnPException:
            sys.exc_clear()
    return selected

def drawscreen(speaker, track_info):
    ''' draws the curses display of album/track info
    '''
    SCREEN.erase()
    SCREEN.border(0)
    SCREEN.addstr(STARTLINE + 0, STARTCOL, HR)
    SCREEN.addstr(STARTLINE + 1, STARTCOL, 'Now '
                  + speaker.get_current_transport_info()['current_transport_state']
                  + ' on Sonos speaker: '
                  + speaker.player_name)
    SCREEN.addstr(STARTLINE + 2, STARTCOL, 'Sonos Favorite Channel: ' + CHANNEL_NAME)
    if speaker.mute:
        volume = str(speaker.volume) + ' (MUTED)'
    else:
        volume = str(speaker.volume)
    SCREEN.addstr(STARTLINE + 3, STARTCOL, 'Volume Level: ' + volume)
    SCREEN.addstr(STARTLINE + 4, STARTCOL, HR)
    SCREEN.addstr(STARTLINE + 5, STARTCOL, '  Artist: ' + track_info['artist'])
    SCREEN.addstr(STARTLINE + 6, STARTCOL, '   Album: ' + track_info['album'])
    SCREEN.addstr(STARTLINE + 7, STARTCOL, '   Track: ' + track_info['title'])
    SCREEN.addstr(STARTLINE + 8, STARTCOL, HR)
    SCREEN.addstr(STARTLINE + 9, STARTCOL, '[ '
                  + track_info['position']
                  + ' / '
                  + track_info['duration']
                  + ']')
    SCREEN.addstr(STARTLINE + 10, STARTCOL, HR)
    SCREEN.addstr(STARTLINE + 11, STARTCOL, str(KEY))
    SCREEN.addstr(STARTLINE + 13, STARTCOL, HR)
    SCREEN.addstr(STARTLINE + 14, STARTCOL, 'Controls:')
    controls = "Play/Pause [P]/[SPACE], Skip = [" + ARROW_RT + "], Quit = [Q]"
    SCREEN.addstr(STARTLINE + 15, STARTCOL, controls)
    controls2 = "Volume: [ctrl] + [" + ARROW_UP + "], or [" + ARROW_DN + "]"
    SCREEN.addstr(STARTLINE + 16, STARTCOL, controls2)
    SCREEN.refresh()

STATE = PLAYER.get_current_transport_info()['current_transport_state']
if STATE != 'PLAYING':
    CHANNEL_NAME = drawchooserpad('favorites')
    PLAYER.play()

KEY = ''
while KEY != 113:
    STATE = PLAYER.get_current_transport_info()['current_transport_state']
    KEYS_PAUSE = [32, 80, 112] # keys: [space], [P], [p]
    KEYS_SKIP = [261] # keys: [→]
    KEYS_MUTE = [77, 109] # keys: [m], or [M]
    KEYS_VOLUME_UP = [566] # [ctrl] + [↑]
    KEYS_VOLUME_DOWN = [525] # [ctrl] + [↓]
    KEYS_CHANNEL = [99, 67] # [c] and [C]
    KEYS_SPEAKER = [115, 83] # keys: [s] or [S]
    if KEY in KEYS_CHANNEL:
        NEW_CHANNEL = drawchooserpad('favorites')
        CHANNEL_NAME = CHANNEL_NAME if NEW_CHANNEL == 'nochoice' else NEW_CHANNEL
    if KEY in KEYS_SPEAKER:
        NEW_PLAYER = drawchooserpad('speakers')
        PLAYER = PLAYER if NEW_PLAYER == 'nochoice' else NEW_PLAYER
    if KEY in KEYS_PAUSE:
        _ = PLAYER.pause() if STATE == 'PLAYING' else PLAYER.play()
    if KEY in KEYS_SKIP:
        PLAYER.next()
    if KEY in KEYS_MUTE:
        PLAYER.mute = False if PLAYER.mute else True
    if KEY in KEYS_VOLUME_UP:
        PLAYER.volume += 1
    if KEY in KEYS_VOLUME_DOWN:
        PLAYER.volume -= 1

    INFO = PLAYER.get_current_track_info()
    drawscreen(PLAYER, INFO)
    KEY = SCREEN.getch()

SCREEN.clear()

curses.endwin()
