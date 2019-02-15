## Google Play Music Random Album Playlist

If you're into listening to albums as a whole rather than picking and choosing some of your favorite songs, there's no good way to listen to whole albums in a randomized order.  You can go through and add albums to a playlist in whatever order you choose, but what if you want it randomized and, well, automated?

This script allows you to do just that.  Just fill in the list with the names of the album, enter the appropriate login information, and run the script.

Now with the ability to have an album featured multiply times!

It's recommended that you create an [app password](https://security.google.com/settings/security/apppasswords) for use with this script.

### Dependencies
gmusicapi is required for this to work.  You can install this via pip:

`pip install gmusicapi`

### Things To Know
If you name an album directly, and then also specify to include every album from that artist the total amount of times that album will be in the final playlist is cumulative.  For example, if you say you want every album from Pink Flyod three times, and also state that you want Dark Side of the Moon two times, then Dark Side of the Moon will be in the final playlist five times.

#### Examples:

`python playlistrandomizer.py createconfig`

`python playlistrandomizer.py dumpalbums`

`python playlistrandomizer.py createplaylist`

```
usage: playlistrandomizer.py [-h] [-v] [-o] [-n PLAYLIST_NAME] ACTION

Randomize (or not) a list of albums and create a Google Play Music playlist in
that order

positional arguments:
  ACTION            Which action to perform. Allowed options: createconfig,
                    dumpalbums, createplaylist

optional arguments:
  -h, --help        show this help message and exit
  -v                Output verbosely. Only for use with createplaylist and
                    dumpalbums.
  -o                Only for use with createplaylist. Creates playlist in the
                    order listed in the config, not randomized.
  -n PLAYLIST_NAME  Only for use with createplaylist. Specifies a name for the
                    playlist. If not provided it defaults to the date in YYYY-
                    MM-DD format.
```