#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
sonos_faves_ramping_alarm.py - a gentle alarm using Sonos Favorites.

This module allows a user to choose a SONOS favorite channel to
play for a gentle alarm. Select the maximum desired volume, the
number of minutes over which to ramp volume from 0 to the chosen
maxium, and choose a favorite to use (by title), and the script
will do the rest.
'''

import argparse
import time
import os.path
import soco

_SPEAKER = '<SPEAKER NAME>'
_CHANNEL = '<CHANNEL NAME>' #can be a partial name
_MINUTES = 30
_MAXVOL = 12

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
    parser.add_argument('-s', '--speaker', type=str,
                        help='The Sonos speaker to use for the alarm',
                        default=_SPEAKER)
    parser.add_argument('-c', '--channel', type=str,
                        help='The Sonos Favorite Channel to use for the alarm',
                        default=_CHANNEL)
    parser.add_argument('-m', '--minutes', type=int,
                        help='The number of minutes the alarm will ramp up over',
                        default=_MINUTES)
    parser.add_argument('-v', '--volume', type=int,
                        help='Set the maximum volume for the alarm',
                        default=_MAXVOL)
    parser.add_argument('-p', '--pause',
                        help='Pause a speaker that is playing.',
                        action='store_true')
    parser.epilog = "The channel you select must be a Sonos Favorite. Because\n"
    parser.epilog += "I'm lazy and didn't feel like figuring out SoCo to get\n"
    parser.epilog += "it working directly with Pandora, which SoCo doesn't seem\n"
    parser.epilog += "to work with yet."
    args = parser.parse_args()

    for speaker in soco.discover():
        if speaker.player_name.lower() == args.speaker.lower():
            player = speaker
            break

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

        if args.minutes == 0:
            player.volume = args.volume
        else:
            player.volume = 0
            seconds = args.minutes * 60
            ramp_interval = seconds / args.volume
            for _ in xrange(args.volume):
                player.volume += 1
                time.sleep(ramp_interval)

if __name__ == "__main__":
    ''' /tmp/holiday allows us to mark when we don't want the alarm to run
    tomorrow.  Especially when we're using cron.
    '''
    if os.path.isfile('/tmp/holiday'):
        print "Today is marked as a holiday, not running the alarm"
    else:
        main()
else:
    print "This file is not intended to be included by other scripts."

