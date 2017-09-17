Requirements:

* Python 2.7.x
 * argparse
 * time
 * os.path
 * soco - get it at https://github.com/SoCo/SoCo

----
Sonos Favorites Ramping Alarm:
    
    usage: sonos-fadein-alarm.py [-h] [-s SPEAKER] [-c CHANNEL]
                                        [-m MINUTES] [-v VOLUME] [-p]
    
    Sonos/Favorites ramping alarm.
    
    optional arguments:
      -h, --help            show this help message and exit
      -S SPEAKER, --speaker SPEAKER
                            The Sonos speaker to use for the alarm
      -s SPEAKER, --slave SPEAKER
                            The Sonos speaker to join to a master
                            'All' causes all available speakers to join.
      -c CHANNEL, --channel CHANNEL
                            The Sonos Favorite Channel to use for the alarm
      -m MINUTES, --minutes MINUTES
                            The number of minutes the alarm will ramp up over
      -v VOLUME, --volume VOLUME
                            Set the maximum volume for the alarm
      -p, --pause           Pause a speaker that is playing.
    
    The channel you select must be a Sonos Favorite. Because I'm lazy and didn't
    feel like figuring out SoCo to get it working directly with Pandora, which
    SoCo doesn't seem to work with yet.

----

How To Use It:

I run it in cron, as follows:

    # m h  dom mon dow   command
    0 7 * * * /usr/bin/python /path/to/sonos-fadein-alarm.py -S 'Master Bedroom' -c 'pulse' -m 30 -v 12

This tells cron to run it every weekday, at 07:00 HRS, on the Speaker labeled
'Master Bedroom', and 'pulse' matches the SiriusXM channel 'The Pulse'.  My alarm
then runs for 30 minutes, during which it ramps the volume slowly from 0 to 12.

My son prefers to wake up with a Pandora Channel built from the VolBeat version
of Battleship Chains.  So the crontab entry for him looks like:

    # m h dom mon dow   command
    30 7 * * * /usr/bin/python /path/to/sonos-fadein-alarm.py -S "J's Room" -c 'battleship chains' -m 30 -v 12

If my wife is travelling, I'll join my son in waking up to the battleship chains channel.

    # m h  dom mon dow   command
    30 7 * * * /usr/bin/python /path/to/sonos-fadein-alarm.py -S "J's Room" -s 'master bedroom' -c 'battleship chains' -m 30 -v 12


