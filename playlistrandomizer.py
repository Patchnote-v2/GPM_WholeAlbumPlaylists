#!/usr/bin

from gmusicapi import Mobileclient

import pprint
import argparse
import datetime
import json
import os.path
import random

# todo: ability to specify artists to include the entire discography of
# todo: ability to specify quantities of each album/artist

###
# Globals
### 
# CONFIG_FILENAME = "old-config-final.json"
CONFIG_FILENAME = "configjson"
CONFIG_FILE_TEMPLATE = {"username": "username", "password": "password", "albums": {"": 0,"": 0}, "artists": {"": 0, "": 0}}
ALBUM_DUMP_FILENAME = "album_dump.json"

# Config settings
config_json_data = ""

###
# Arguments
###
parser = argparse.ArgumentParser(
    description='Randomize (or not) a list of albums and create a Google Play Music playlist in that order')

parser.add_argument('-v',
    action='store_true',
    dest='verbose',
    help='Only for use with createplaylist and dumpalbums. Output verbosely.')

parser.add_argument('-o',
    action='store_true',
    dest='is_in_order',
    help='Only for use with createplaylist.  Creates playlist in the order listed in the config, not randomized.')

parser.add_argument('-n',
    dest='playlist_name',
    help='Only for use with createplaylist.  Specifies a name for the playlist.  If not provided it defaults to the date in YYYY-MM-DD format.')

parser.add_argument('create_file',
    choices=('createconfig', 'dumpalbums', 'createplaylist'),
    help='Which action to perform.  Allowed options: createconfig, dumpalbums, createplaylist',
    metavar='ACTION')

args = parser.parse_args()

# Check if order and name flags are only being used with createplaylist
if args.is_in_order is True and args.create_file != 'createplaylist':
    parser.error("-o is only for use with createplaylist")
if args.playlist_name != None and args.create_file != 'createplaylist':
    parser.error("-n is only for use with createplaylist")

###
# Functions
###
# Opens and writes new config from template
def newConfigFileFromTemplate():
    with open(CONFIG_FILENAME, "w") as config_file:
        json.dump(CONFIG_FILE_TEMPLATE, config_file, sort_keys=True)
    print("Config file created at ./" + CONFIG_FILENAME)

# Loads login data from config file and attempts to log in, exits if unable
def login():
    # Loads config JSON to global variable config_json_data
    global config_json_data
    if os.path.exists(CONFIG_FILENAME):
        with open(CONFIG_FILENAME, "r") as config_file:
            config_json_data = json.load(config_file)
    else:
        exit("Config file does not exist.  Please run \"python playlistrandomizer.py createconfig\" and fill in the appropriate login information.")

    # Attempt login
    api = Mobileclient(debug_logging=False)
    logged_in = api.login(config_json_data['username'], config_json_data['password'], Mobileclient.FROM_MAC_ADDRESS)

    if not logged_in:
        exit("Unable to login with the provided credentials.")    
    else:
        return api

###
# Main
###
if args.create_file == "createconfig":
    # Writes a brand-new config file from a template, with overwritting detection
    # Check if file exists then create
    if not os.path.exists(CONFIG_FILENAME):
        print("tests")
        newConfigFileFromTemplate()

    # Open file and check if it matches the template; if not, ask about overwriting
    with open(CONFIG_FILENAME, "r") as config_file:
        template_string = json.dumps(CONFIG_FILE_TEMPLATE, sort_keys=True)
        config_file_string = json.dumps(json.loads(config_file.read()), sort_keys=True)

        if template_string != config_file_string:
            answer = input("The config file has been altered.  Do you wish to overwrite and create a fresh one? (y/N)")
            if answer == '' or answer[:1].lower() == 'n':
                print("Config file NOT overwritten")

            elif answer != '' and answer[:1].lower() == 'y':
                print("Config file overwritten")
                newConfigFileFromTemplate()

            else:
                print("Invalid response")
    exit()

elif args.create_file == "dumpalbums":
    print("Logging in")
    api = login()
    if api is not None:
        # Get list of all songs
        print("Downloading all song metadata")
        songs = api.get_all_songs()

        album_list = {}
        for song in songs:
            # Add artist to dict if not already in there
            if song['artist'] not in album_list:
                album_list[song['artist']] = []

            # Add album to artist's album list if not already in there
            else:
                if song['album'] not in album_list[song['artist']]:
                    album_list[song['artist']].append(song['album'])
                    # Verbose output
                    if args.verbose:
                        print("Adding album: " + song['album'])

        # Write to file
        print("Writing to file")
        with open(ALBUM_DUMP_FILENAME, "w") as album_dump_file:
            json.dump(album_list, album_dump_file, indent=4, sort_keys=True)

elif args.create_file == "createplaylist":
    print("Logging in")
    api = login()
    if api is not None:
        print("Downloading all song metadata")
        songs = api.get_all_songs()

        running_album_list = set()
        wanted_albums = {}

        # Get all albums listed into order
        # Structure looks like dict[album][n][song_number]
        for album, amount in config_json_data['albums'].items():
            running_album_list.add(album)
            count = 0
            wanted_albums[album] = {}
            while count < amount:
                wanted_albums[album][count] = {}
                count += 1

        running_album_list_from_artists = set()
        # Go through all songs and add if it's in the wanted_albums list then add the song to the tracklist(s)
        for song in songs:
            # For each song see if it's from a wanted artist
            # Optimization is definitely to be had here
            for artist, amount in config_json_data['artists'].items():
                if song['artist'] == artist:

                    # Check if album has already been added
                    if song['album'] not in running_album_list_from_artists:
                        # Add album to list so next song from the album doesn't add it again
                        running_album_list_from_artists.add(song['album'])

                        # If album wasn't already specified explicitly in the config there isn't an entry already in wanted_albums 
                        if song['album'] not in wanted_albums:
                            count = 0
                            wanted_albums[song['album']] = {}
                            while count < amount:
                                wanted_albums[song['album']][count] = {}
                                count += 1
                        # If album was stated explicitly in the config then append the album X amount of times to the already existing entry
                        else:
                            count = len(wanted_albums[song['album']])
                            total = count + amount
                            while count < total:
                                wanted_albums[song['album']][count] = {}
                                count += 1

            # Checks if song is in an album that is in wanted_albums
            # If yes then add to each entry for the album
            # Could possibly combine this with the code above where the album is added to the wanted_albums list in the first place
            # Will I?  Probably not because it's not worth the time
            for album, number_of_times in wanted_albums.items():
                if song['album'] == album:
                    for number, tracklist in number_of_times.items():
                        tracklist.update({song['trackNumber']: song['id']})
                        if args.verbose:
                            print("Adding song: " + song['title'] + " - " + song['artist'])

        # Combine the two album lists from specified albums and specified artists
        running_album_list.update(running_album_list_from_artists)

        # Used for finding missing albums and unshuffling
        album_keys = list(wanted_albums.keys())

        # Checks if the total number of albums listed is the same as the total number of albums found
        if len(album_keys) is not len(running_album_list):
            print("{0} albums wanted, only {1} found.".format(len(running_album_list), len(album_keys)))
            print("These albums weren't found.  Their're probaly misspeled.")

            # Prints albums that aren't in both lists
            # Thanks StackOverflow!
            missing_albums = []
            combined_list = album_keys + list(running_album_list)
            for i in range(0, len(combined_list)):
                if ((combined_list[i] not in album_keys) or (combined_list[i] not in running_album_list)) and (combined_list[i] not in missing_albums):
                     missing_albums[len(missing_albums):] = [combined_list[i]]

            for value in missing_albums:
                print(value)
        else:
            final_song_order = [] # The final order of all song IDs that will be added to the playlist

            # If in order then unshuffle and add to final order
            if args.is_in_order:
                print("Unshuffling... no, really...")
                album_keys.sort()

                # Say what order the albums are being added in if it's verbose and it's not randomized
                if args.verbose:
                    print("Albums are being added in this order:")
                    for album in album_keys:
                        print(album)

                # Add songs to final list in the order they'll be added to the playlist
                for key in album_keys:
                    for number, tracklist in wanted_albums[key].items():
                        for track_number, song_id in tracklist.items():
                            final_song_order.append(song_id)

            # Shuffle the album order
            else:
                # Remove album name from all tracklists and add them to a list to be shuffled 
                albums_without_album_names = []
                for album_name, album_tracklists in wanted_albums.items():
                    for number, album_tracklist in album_tracklists.items():
                        albums_without_album_names.append(album_tracklist)

                print("Shuffling")
                random.shuffle(albums_without_album_names)
                # Add songs to final list in the order they'll be added to the playlist
                for tracklist in albums_without_album_names:
                    for track_number, song_id in tracklist.items():
                        final_song_order.append(song_id)

            # Create new playlist
            print("Creating playlist")
            if args.playlist_name is not None:
                new_playlist = api.create_playlist(args.playlist_name)
            else:
                new_playlist = api.create_playlist(datetime.datetime.now().strftime("%Y-%m-%d"))
            print("Final playlist length: {0}".format(len(final_song_order)))

            # And we're finally done...
            api.add_songs_to_playlist(new_playlist, final_song_order)