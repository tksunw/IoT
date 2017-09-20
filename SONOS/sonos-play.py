#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
sonos-play-alarm.py - Play a Sonos Favorites Channel.

This script allows a user to choose a SONOS favorite channel to
play, at a certain volume, and with one additional or all
additional Sonos speakers on the network.

2017-09-18  initial version
'''

import argparse
import datetime
import time
import os.path
import soco

# Set some default values.  These are mine.  The channel is listed
# by name, and comes from the Sonos players 'favorites'.  Volume
# on the player(s) is specified via -v.

_SPEAKER = 'office'

def get_sonos_favorites(from_speaker):
    ''' get_sonos_favorites: gets the saved "favorites" from a Sonos speaker.
    Args:
        from_speaker (soco.core.Soco object): the speaker to pull favorites from.

    Returns:
        favs (list): a list of Sonos Favorites (title, meta, uri)
    '''
    favs = from_speaker.get_sonos_favorites()['favorites']
    return favs

def toggle_pause(speaker):
    if speaker.get_current_transport_info()['current_transport_state'] == 'PLAYING':
        speaker.pause()
    else:
        speaker.play()

def set_speaker_volume(speaker,volume):
    speaker.volume = volume

def main():
    ''' main function:

        Args:
            None

        Returns:
            None

        Process command line arguments, and turn a Sonos speaker into an alarm
        clock, with the flexibility to ramp the volume slowly over a defined
        time period, to a "max vol" limit.
    '''

    parser = argparse.ArgumentParser(description='Sonos/Favorites ramping alarm.')
    parser.add_argument('-S', '--speaker', type=str,
                        help='The Sonos speaker to use for the alarm',
                        default=_SPEAKER)
    parser.add_argument('-s', '--slave', type=str,
                        help='The Sonos speaker(s) to join to a group for the alarm.  Use the word "all" to join all available players.')
    parser.add_argument('-c', '--channel', type=str,
                        help='The Sonos Favorite Channel to use for the alarm')
    parser.add_argument('-v', '--volume', type=int,
                        help='Set the maximum volume for the alarm')
    parser.add_argument('-p', '--pause',
                        help='Pause a speaker that is playing.',
                        action='store_true')
    parser.epilog = "The channel you select must be a Sonos Favorite. Because\n"
    parser.epilog += "I'm lazy and didn't feel like figuring out SoCo to get\n"
    parser.epilog += "it working directly with Pandora, which SoCo doesn't seem\n"
    parser.epilog += "to work with yet."
    args = parser.parse_args()

    speakers = soco.discover()
    player = [x for x in speakers if x.player_name.lower() == args.speaker.lower()][0]
    if args.slave:
        if args.slave.lower() == 'all':
            [x.join(player) for x in speakers if x.player_name.lower() != player.player_name.lower()]
        else:
            slave = [x for x in speakers if x.player_name.lower() == args.slave.lower()][0]
            slave.join(player)

    curr_state = player.get_current_transport_info()['current_transport_state']

    if args.volume:
        set_speaker_volume(player,args.volume)

    if args.pause:
        ''' depending on the current state of the speaker, let's pause or play,
        as we deem appropriate.
        '''
        toggle_pause(player)
    else:
        if args.channel:
            favorites = get_sonos_favorites(player)
            for favorite in favorites:
                # this fuzzy match lets us type partial channel names
                if args.channel.lower() in favorite['title'].lower():
                    my_choice = favorite
                    break

            print "Playing {} on {}".format(my_choice['title'], player.player_name)
            player.play_uri(uri=my_choice['uri'], meta=my_choice['meta'], start=True)

if __name__ == "__main__":
    main()
else:
    print "This file is not intended to be included by other scripts."

