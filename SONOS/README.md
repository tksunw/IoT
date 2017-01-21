Sonos Favorites Ramping Alarm:
    
    usage: sonos_faves_ramping_alarm.py [-h] [-s SPEAKER] [-c CHANNEL]
                                        [-m MINUTES] [-v VOLUME] [-p]
    
    Sonos/Favorites ramping alarm.
    
    optional arguments:
      -h, --help            show this help message and exit
      -s SPEAKER, --speaker SPEAKER
                            The Sonos speaker to use for the alarm
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
