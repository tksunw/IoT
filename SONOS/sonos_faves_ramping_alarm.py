#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
sonos_faves_ramping_alarm.py - a gentle alarm using Sonos Favorites.

This module allows a user to choose a SONOS favorite channel to
play for a gentle alarm. Select the maximum desired volume, the
number of minutes over which to ramp volume from 0 to the chosen
maxium, and choose a favorite to use (by title), and the script
will do the rest.

2017-01-21  my new alarm clock.
2017-09-15  added ability to group a second speaker to the main speaker
            also aded the ability to specify 'all' to group all 
            available speakers to the main speaker.
'''

import argparse
import time
import os.path
import soco

# Set some default values.  These are mine.  The channel is listed
# by name, and comes from the Sonos players 'favorites'.  Volume
# on the player(s) specified will ramp up from 0 to MAXVOL over
# the number of minutes specified.  For me, I like a 30 minute
# ramp from 0 to 12.  So the volume will increase by 1 every 2.5
# minutes.
_SPEAKER = 'master bedroom'
_CHANNEL = 'Everybody Talks Radio'
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
    parser.add_argument('-S', '--speaker', type=str,
                        help='The Sonos speaker to use for the alarm',
                        default=_SPEAKER)
    parser.add_argument('-s', '--slave', type=str,
                        help='The Sonos speaker(s) to join to a group for the alarm.  Use the word "all" to join all available players.')
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

