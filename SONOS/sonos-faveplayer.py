#!/usr/bin/env python3
''' docstring goes here
'''

#from __future__ import print_function, division  #You don't need this in Python3
from bs4 import BeautifulSoup
import curses
from math import ceil, floor
import operator
import sys
import soco
import time

SPKRS = sorted(soco.discover(), key=operator.attrgetter('player_name'))
if not SPKRS:
    print("An error occured during soco.discover(). Please check your network and try again")
    sys.exit(1)

FAVES = SPKRS[0].music_library.get_sonos_favorites()
CHANS = {f.get_uri().replace('%3a',':').replace('&amp;','&'): f.title for f in FAVES}
ALPHABET = [chr(c) for c in range(97, 123)]
MAXROWS = 10 #max number of rows

def print_error(*args, **kwargs):
    ''' an easy way to print to stderr
    '''
    if kwargs:
        print(kwargs, file=sys.stderr)
    if args:
        print(args, file=sys.stderr)

def progress_bar_pct(position, duration):
    ''' docstring
    '''
    p_int = sum(int(i) * 60**index for index, i in enumerate(position.split(":")[::-1]))
    d_int = sum(int(i) * 60**index for index, i in enumerate(duration.split(":")[::-1]))
    p_secs = p_int if p_int > 0 else 1
    d_secs = d_int if d_int > 0 else 1
    percent = 100.0 * p_secs / d_secs
    p_pct = percent if percent < 101 else 1
    return p_pct

def progress_bar(p_pct):
    ''' docstring
    '''
    p_string = '#' * int(((p_pct * 60) / 100.0))
    return p_string

def selector(mainscreen, choicetype):
    ''' docstring
    '''
    box = curses.newwin(MAXROWS + 2, 64, 4, 4)
    box.box()
    if choicetype is 'channels':
        available_choices = [chan.title for chan in FAVES]
    elif choicetype is 'speakers':
        available_choices = [spkr.player_name for spkr in SPKRS]
    else:
        return 0
    row_num = len(available_choices)
    pages = int(ceil(row_num / MAXROWS))
    position = 2
    page = 1
    choice = 'p'
    mainscreen.refresh()
    box.refresh()

    while choice != 27:
        if choice == curses.KEY_DOWN:
            if page == 1:
                if position < page * MAXROWS:
                    position = position + 1
                else:
                    if pages > 1:
                        page = page + 1
                        position = 1 + (MAXROWS * (page - 1))
            elif page == pages:
                if position < row_num:
                    position = position + 1
            else:
                if position < MAXROWS + (MAXROWS * (page - 1)):
                    position = position + 1
                else:
                    page = page + 1
                    position = 1 + (MAXROWS * (page - 1))

        if choice == curses.KEY_UP:
            if page == 1:
                if position > 1:
                    position = position - 1
            else:
                if position > (1 + (MAXROWS * (page - 1))):
                    position = position - 1
                else:
                    page = page - 1
                    position = MAXROWS + (MAXROWS * (page - 1))

        if choice == curses.KEY_LEFT:
            if page > 1:
                page = page - 1
                position = 1 + (MAXROWS * (page - 1))

        if choice == curses.KEY_RIGHT:
            if page < pages:
                page = page + 1
                position = (1 + (MAXROWS * (page - 1)))

        if choice == ord("\n") and row_num != 0:
            box.erase()
            box.border(0)
            del box
            return position

        if choice == ord('q'):
            curses.endwin()
            exit()

        box.erase()
        mainscreen.border(0)
        box.border(0)

        maxrowpage = MAXROWS * (page - 1)
        for i in range(1 + maxrowpage, MAXROWS + 1 + maxrowpage):
            option = available_choices[i-1]
            cpair = curses.A_REVERSE if i + maxrowpage == position + maxrowpage else curses.A_NORMAL
            box.addstr(i - maxrowpage, 2, option, cpair)
            if i == row_num:
                break

        mainscreen.refresh()
        box.refresh()
        choice = mainscreen.getch()


def get_channel_name(curr_info):
    clean = curr_info['title'].replace('%3a',':').replace('&amp;','&')
    return CHANS[clean]

def draw_player(mainscreen, curr_state, curr_info, speaker, channel):
    ''' docstring
    '''
    if curr_state == 'TRANSITIONING':
        time.sleep(2)
        curr_state = get_curr_state(speaker)
        curr_info = get_curr_info(speaker)
        draw_player(mainscreen, curr_state, curr_info, speaker, channel)
    elif curr_state == 'STOPPED':
        curr_info['title'] = ''
    elif curr_state == 'PLAYING':

        if curr_info['title'].startswith('x-sonosapi'):
            xml = BeautifulSoup(curr_info['metadata'], 'html.parser')
            dat = xml.find_all()[3]
            splits = dat.text.split('|')
            if len(splits) < 3:
                curr_state = get_curr_state(speaker)
                curr_info = get_curr_info(speaker)
                draw_player(mainscreen, curr_state, curr_info, speaker, channel)
            else:
                curr_info['title'] = splits[2].replace('TITLE ','')
                curr_info['artist'] = splits[3].replace('ARTIST ','')

    box = curses.newwin(13, 64, 2, 1)
    box.box()
    curr_vol = str(speaker.volume) + ' (MUTED)' if speaker.mute else str(speaker.volume)
    track_pos = curr_info['position'] if curr_info['position'] != 'NOT_IMPLEMENTED' else '0:00:00'
    track_dur = curr_info['duration'] if curr_info['duration'] != 'NOT_IMPLEMENTED' else '0:00:00'
    mainscreen.addstr(1, 1, 'Sonos Favorites Player')
    box.addstr(1, 2, 'Now ' + curr_state + ' on Sonos Speaker: ' + speaker.player_name)
    box.addstr(2, 2, 'Channel: ' + channel.title)
    box.addstr(3, 2, 'Volume: ' + curr_vol)
    box.hline(4, 2, '-', 60)
    box.addstr(5, 2, '  Artist: ' + curr_info['artist'])
    box.addstr(6, 2, '   Album: ' + curr_info['album'])
    box.addstr(7, 2, '   Track: ' + curr_info['title'])
    box.hline(8, 2, '-', 60)
    box.addstr(9, 2, progress_bar(progress_bar_pct(track_pos, track_dur)))
    box.hline(10, 2, '-', 60)
    box.addstr(11, 2, '[ ' + track_pos + ' / ' + track_dur  + ' ]')
    box.touchwin()
    mainscreen.refresh()
    box.refresh()
    return None

def get_curr_state(speaker):
    return speaker.group.coordinator.get_current_transport_info()['current_transport_state']

def get_curr_info(speaker):
    return speaker.group.coordinator.get_current_track_info()

def main(screen):
    ''' draw the main screen
    '''
    screen.addstr(1, 1, 'Sonos Favorites Player')
    curses.halfdelay(10)
    choice = 0
    speaker = None
    channel = None
    while choice is not ord('q'):
        if choice is ord('s') or speaker is None:
            screen.erase()
            screen.addstr(1, 1, 'Sonos Favorites Player')
            screen.addstr(3, 4, 'Select a speaker to listen to:')
            choice = selector(screen, 'speakers')
            speaker = SPKRS[choice-1]
            screen.erase()
            screen.addstr(1, 1, 'Sonos Favorites Player')
            screen.addstr(20, 1, 'Selected: ' + str(choice) + ' [' +
                          speaker.player_name + ']')
            screen.touchwin()
            screen.refresh()

        curr_state = get_curr_state(speaker)
        curr_info = get_curr_info(speaker)

        if choice is ord('c') or channel is None:
            if channel is None:
                channel = soco.data_structures.DidlFavorite(title='unknown', parent_id='N/A', item_id='N/A')
                if curr_info['title'].startswith('x-sonos'):
                    channel.title = get_channel_name(curr_info)
            else:
                screen.erase()
                screen.addstr(1, 1, 'Sonos Favorites Player')
                screen.addstr(3, 4, 'Select a channel to listen to:')
                choice = selector(screen, 'channels')
                channel = FAVES[choice - 1]
                screen.erase()
                screen.addstr(1, 1, 'Sonos Favorites Player')
                screen.addstr(20, 1, 'Selected: ' + str(choice) + ' [' + channel.title + ']')
                screen.touchwin()
                screen.refresh()
                title = channel.title
                uri = channel.get_uri()
                meta = channel.resource_meta_data
                speaker.group.coordinator.play_uri(uri=uri,meta=meta)

        if choice is ord('+'):
            speaker.group.coordinator.volume += 1

        if choice is ord('-'):
            speaker.group.coordinator.volume -= 1

        if choice is ord('m'):
            speaker.group.coordinator.mute = not speaker.group.coordinator.mute

        if choice is ord(' '):
            if curr_state == 'PLAYING':
                speaker.group.coordinator.pause()
            else:
                speaker.group.coordinator.play()

        draw_player(screen, curr_state, curr_info, speaker, channel)

        choice = screen.getch()

    curses.endwin()
    exit()

if __name__ == '__main__':
    curses.wrapper(main)
else:
    print('not in __main__')
