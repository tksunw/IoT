#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
sonos-play.py - Play a Sonos Favorites Channel.

This script allows a user to choose a SONOS favorite channel to
play, at a certain volume, and with one additional or all
additional Sonos speakers on the network.

2017-09-18  initial version
'''

import argparse
import sys
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

def set_speaker_volume(speaker, volume):
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

    # Validate volume range
    if args.volume is not None and (args.volume < 0 or args.volume > 100):
        print("Error: Volume must be between 0 and 100")
        sys.exit(1)

    # Discover Sonos speakers
    speakers = soco.discover()
    if not speakers:
        print("Error: No Sonos speakers found on the network")
        sys.exit(1)

    # Find the main player
    player = next((x for x in speakers if x.player_name.lower() == args.speaker.lower()), None)
    if not player:
        print(f"Error: Speaker '{args.speaker}' not found")
        print(f"Available speakers: {', '.join(s.player_name for s in speakers)}")
        sys.exit(1)

    # Handle slave speakers
    if args.slave:
        if args.slave.lower() == 'all':
            for speaker in speakers:
                if speaker.player_name.lower() != player.player_name.lower():
                    try:
                        speaker.join(player)
                    except Exception as e:
                        print(f"Warning: Failed to join {speaker.player_name}: {e}")
        else:
            slave = next((x for x in speakers if x.player_name.lower() == args.slave.lower()), None)
            if not slave:
                print(f"Error: Slave speaker '{args.slave}' not found")
                sys.exit(1)
            try:
                slave.join(player)
            except Exception as e:
                print(f"Error: Failed to join speakers: {e}")
                sys.exit(1)

    if args.volume is not None:
        try:
            set_speaker_volume(player, args.volume)
        except Exception as e:
            print(f"Error: Failed to set volume: {e}")
            sys.exit(1)

    if args.pause:
        ''' depending on the current state of the speaker, let's pause or play,
        as we deem appropriate.
        '''
        try:
            toggle_pause(player)
        except Exception as e:
            print(f"Error: Failed to toggle pause: {e}")
            sys.exit(1)
    else:
        if args.channel:
            try:
                favorites = get_sonos_favorites(player)
            except Exception as e:
                print(f"Error: Failed to get favorites: {e}")
                sys.exit(1)

            my_choice = None
            for favorite in favorites:
                # this fuzzy match lets us type partial channel names
                if args.channel.lower() in favorite['title'].lower():
                    my_choice = favorite
                    break

            if not my_choice:
                print(f"Error: Channel '{args.channel}' not found in favorites")
                print(f"Available favorites: {', '.join(f['title'] for f in favorites)}")
                sys.exit(1)

            print(f"Playing {my_choice['title']} on {player.player_name}")
            try:
                player.play_uri(uri=my_choice['uri'], meta=my_choice['meta'], start=True)
            except Exception as e:
                print(f"Error: Failed to play URI: {e}")
                sys.exit(1)

if __name__ == "__main__":
    main()
else:
    print("This file is not intended to be included by other scripts.")

