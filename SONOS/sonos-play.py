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
# on the player(s) specified will be set at _VOLUME, if something
# different is not specified via -v.

_SPEAKER = 'office'
_CHANNEL = 'Sunlounger Radio'
_VOLUME = 6

def get_sonos_favorites(from_speaker):
    ''' get_sonos_favorites: gets the saved "favorites" from a Sonos speaker.
    Args:
        from_speaker (soco.core.Soco object): the speaker to pull favorites from.

    Returns:
        favs (list): a list of Sonos Favorites (title, meta, uri)
    '''
    favs = from_speaker.get_sonos_favorites()['favorites']
    return favs

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
                        help='The Sonos Favorite Channel to use for the alarm',
                        default=_CHANNEL)
    parser.add_argument('-v', '--volume', type=int,
                        help='Set the maximum volume for the alarm',
                        default=_VOLUME)
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

    if args.pause:
        ''' this will stop the indicated sonos speaker.  even if the alarm is
        still running.
        '''
        player.stop()
    else:
        favorites = get_sonos_favorites(player)
        for favorite in favorites:
            if args.channel.lower() in favorite['title'].lower():
                my_choice = favorite
                break

        print "Playing {} on {}".format(my_choice['title'], player.player_name)
        player.play_uri(uri=my_choice['uri'], meta=my_choice['meta'], start=True)

        player.volume = args.volume

if __name__ == "__main__":
        main()
else:
    print "This file is not intended to be included by other scripts."

