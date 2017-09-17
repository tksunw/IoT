Requirements:

* Python 2.7.x
 * argparse
 * time
 * os.path
 * soco - get it at https://github.com/SoCo/SoCo

----
Sonos Favorites Fade In  Alarm:
    
    Sonos (Favorites) Fade In Alarm - An alarm that fades in a Sonos speaker, or 
    set of speakers, over a configurable lenght of time, to a configurable volume
    level.
    
    usage: sonos-fadein-alarm.py [-h] [-s SPEAKER] [-c CHANNEL]
                                        [-m MINUTES] [-v VOLUME] [-p]
    
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

Look for the default variables near the top of the file.

    _SPEAKER lets you set a default speaker to always use if one isn't specified by command
    line options.

    _CHANNEL lets you specify a default Sonos Favorites channel to play if one isn't specified
    by command line option.

    _MINUTES sets a default timespan for the fade-in.

    _MAXVOL sets a default maximum volume.

    _WEEKEND lets you set certain days of the week (by name) to be skipped on a regular basis.
    Since my company is closed on Saturday and Sunday, those are the days listed.  Change them
    to suit your work schedule.

You can set the defaults to work for your need, or you can just specify everything vi command line options.

I run it in cron, as follows, to run from 7AM to 7:30 AM, playing the 'Everybody Talks Radio' pandora station:

    # m h  dom mon dow   command
    0 7 * * * /usr/bin/python /path/to/sonos-fadein-alarm.py 

Which is the equivalent of running it like this, if I hadn't set the defaults:

    # m h  dom mon dow   command
    0 7 * * * /usr/bin/python /path/to/sonos-fadein-alarm.py -S 'Master Bedroom' -c 'Everybody Talks Radio' -m 30 -v 12

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

----

holidays.txt

    This file just contains a list of dates.  They currently happen to be the dates which my 
    company gives me off, so you should change them to suit your work schedule.


