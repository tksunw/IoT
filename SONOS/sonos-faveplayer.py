#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
docstring goes here
'''
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

SPEAKERS = soco.discover()

STARTLINE = 6
STARTCOL = 10

PLAYER = [x for x in SPEAKERS if x.player_name.lower() == 'office'][0]
FAVES = sorted(PLAYER.get_sonos_favorites()['favorites'])
CHANNEL_NAME = 'Unknown'
HR = 60 * '-'

STATE = PLAYER.get_current_transport_info()['current_transport_state']
if STATE != 'PLAYING':
    print '\n\nState is', STATE
    CHANNEL_NAME = channelchooser()
    PLAYER.play()

def drawmenu(chan_menu, pos, cpair1, cpair2):
    ''' draw the actual channel menu
    '''
    chan_menu.clear()
    chan_menu.border(0)
    chan_menu.addstr(2, 2, "Sonos Favorites:", curses.A_STANDOUT)
    chan_menu.addstr(4, 2, "Please select an option...", curses.A_BOLD)
    # Detect what is highlighted by the 'pos' variable.
    cidx = 0
    for channel in [f['title'] for f in FAVES]:
        cidx += 1
        if pos == cidx:
            chan_menu.addstr(STARTLINE + cidx, STARTCOL, channel, cpair1)
        else:
            chan_menu.addstr(STARTLINE + cidx, STARTCOL, channel, cpair2)



def channelchooser():
    ''' enable a user to choose a channel from sonos faves.
    '''
    chan_menu = SCREEN.subpad(len(FAVES) + 10, 60, 4, 4)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
    chan_menu.keypad(1)
    pos = 1
    chan_menu.refresh()
    choice = None
    # I'm going to be lazy and save some typing here.
    cpair1 = curses.color_pair(1)
    cpair2 = curses.A_NORMAL
    while choice != ord('\n'):
        #chan_menu.clear()
        #chan_menu.border(0)
        #chan_menu.addstr(2, 2, "Sonos Favorites:", curses.A_STANDOUT)
        #chan_menu.addstr(4, 2, "Please select an option...", curses.A_BOLD)
        ## Detect what is highlighted by the 'pos' variable.
        #cidx = 0
        #for channel in [f['title'] for f in FAVES]:
        #    cidx += 1
        #    if pos == cidx:
        #        chan_menu.addstr(STARTLINE + cidx, STARTCOL, channel, cpair1)
        #    else:
        #        chan_menu.addstr(STARTLINE + cidx, STARTCOL, channel, cpair2)
        drawmenu(chan_menu, pos, cpair1, cpair2)

        choice = chan_menu.getch()
        channel = FAVES[pos-1]

        for _ in xrange(len(FAVES)):
            if choice == _:
                pos = _
        if choice == 258:
            if pos < len(FAVES):
                pos += 1
            else:
                pos = 1
        elif choice == 259:
            if pos > 1:
                pos += -1
            else:
                pos = len(FAVES)
        elif choice != ord('\n'):
            curses.flash()

    try:
        PLAYER.play_uri(uri=channel['uri'], meta=channel['meta'], start=True)
    except soco.exceptions.SoCoUPnPException:
        sys.exc_clear()

    return channel['title']

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
    controls = "Play/Pause [P]/[SPACE], Skip = [S]/[ " + ARROW_RT + " ], Quit = [Q]"
    SCREEN.addstr(STARTLINE + 15, STARTCOL, controls)
    controls2 = "Volume: [ctrl] + [ " + ARROW_UP + " ], or [ " + ARROW_DN + " ]"
    SCREEN.addstr(STARTLINE + 16, STARTCOL, controls2)
    SCREEN.refresh()

KEY = ''
while KEY != ord('q'):
    STATE = PLAYER.get_current_transport_info()['current_transport_state']
    KEYS_PAUSE = [32, 80, 112] # keys: [space], [P], [p]
    KEYS_SKIP = [261, 83, 115] # keys: [→], [S], or [s]
    KEYS_MUTE = [77, 109] # keys: [m], or [M]
    KEYS_VOLUME_UP = [566] # [ctrl] + [↑]
    KEYS_VOLUME_DOWN = [525] # [ctrl] + [↓]
    KEYS_CHANNEL = [99, 67] # [c] and [C]
    if KEY in KEYS_CHANNEL:
        CHANNEL_NAME = channelchooser()
    if KEY in KEYS_PAUSE:
        if STATE == 'PLAYING':
            PLAYER.pause()
        else:
            PLAYER.play()
    if KEY in KEYS_SKIP:
        PLAYER.next()
    if KEY in KEYS_MUTE:
        if PLAYER.mute:
            PLAYER.mute = False
        else:
            PLAYER.mute = True
    if KEY in KEYS_VOLUME_UP:
        PLAYER.volume += 1
    if KEY in KEYS_VOLUME_DOWN:
        PLAYER.volume -= 1

    INFO = PLAYER.get_current_track_info()
    drawscreen(PLAYER, INFO)
    KEY = SCREEN.getch()

SCREEN.clear()

curses.endwin()
