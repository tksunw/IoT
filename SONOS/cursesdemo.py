#!/usr/bin/env python2.7
''' docstring goes here
'''
from __future__ import print_function, division  #You don't need this in Python3
import curses
from math import ceil, floor
import operator
import sys
import soco

#SPKRS = sorted([s for s in soco.discover()])
SPKRS = sorted(soco.discover(), key=operator.attrgetter('player_name'))
FAVES = SPKRS[0].get_sonos_favorites()['favorites']

ALPHABET = [chr(c) for c in range(97, 123)]

MAXROWS = 10 #max number of rows

def print_error(*args, **kwargs):
    ''' an easy way to print to stderr
    '''
    print(*args, file=sys.stderr, **kwargs)

def time_to_seconds(time):
    ''' docstring
    '''
    split_time = time.split(':')
    rev_split_time = reversed(split_time)
    total_seconds = sum(int(val) * 60 ** key for key, val in enumerate(rev_split_time))
    return total_seconds if total_seconds > 0 else 1

def progress_bar_pct(position, duration):
    ''' docstring
    '''
    p_secs = time_to_seconds(position) if position > 0 else 1
    d_secs = time_to_seconds(duration) if duration > 0 else 100
    p_pct = 100.0 * p_secs / d_secs
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
        available_choices = [chan['title'] for chan in FAVES]
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

def draw_player(mainscreen, curr_state, curr_info, speaker, channel):
    ''' docstring
    '''
    box = curses.newwin(13, 64, 2, 1)
    box.box()
    mainscreen.refresh()
    curr_vol = str(speaker.volume + '(MUTED)') if speaker.mute else str(speaker.volume)
    track_pos = curr_info['position']
    track_dur = curr_info['duration']
    mainscreen.addstr(1, 1, 'Sonos Favorites Player')
    box.addstr(1, 2, 'Now ' + curr_state + ' on Sonos Speaker: ' + speaker.player_name)
    box.addstr(2, 2, 'Channel: ' + channel['title'])
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
    box.refresh()
    return None

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

        if choice is ord('c') or channel is None:
            if channel is None:
                channel = {'title': 'unknown'}
            else:
                screen.erase()
                screen.addstr(1, 1, 'Sonos Favorites Player')
                screen.addstr(3, 4, 'Select a channel to listen to:')
                choice = selector(screen, 'channels')
                channel = FAVES[choice - 1]
                screen.erase()
                screen.addstr(1, 1, 'Sonos Favorites Player')
                screen.addstr(20, 1, 'Selected: ' + str(choice) + ' [' + channel['title'] + ']')
                screen.touchwin()
                screen.refresh()

        curr_state = speaker.get_current_transport_info()['current_transport_state']
        curr_info = speaker.get_current_track_info()

        if choice is ord(' '):
            if curr_state == 'PLAYING':
                speaker.pause()
            else:
                speaker.play()

        #screen.erase()
        draw_player(screen, curr_state, curr_info, speaker, channel)

        choice = screen.getch()

    curses.endwin()
    exit()

if __name__ == '__main__':
    curses.wrapper(main)

else:
    print('not in __main__')
