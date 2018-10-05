#!/usr/bin

from gmusicapi import Mobileclient

import argparse
import datetime
import json
import os.path
import random

###
# Globals
### 
CONFIG_FILENAME = "config.json"
CONFIG_FILE_TEMPLATE = {"username": "username", "password": "password", "albums": ["",""]}
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
    help='Output verbosely.  Only for use with createplaylist and dumpalbums.')

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
    parser.error("-R is only for use with createplaylist")
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

        wanted_songs = {}
        for song in songs:
            for album in config_json_data['albums']:
                if song['album'] == album:
                    if song['album'] not in wanted_songs:
                        wanted_songs[song['album']] = {song['trackNumber']: song['id']}
                        if args.verbose:
                            print("Adding song: " + song['title'] + " - " + song['artist'])
                    else:
                        wanted_songs[song['album']].update({song['trackNumber']: song['id']})
                        if args.verbose:
                            print("Adding song: " + song['title'] + " - " + song['artist'])

        # Create new playlist
        print("Creating playlist")
        if args.playlist_name is not None:
            new_playlist = api.create_playlist(args.playlist_name)
        else:
            new_playlist = api.create_playlist(datetime.datetime.now().strftime("%Y-%m-%d"))

        # Goes through each album and creates a new list of all song IDs
        song_ids = []
        wanted_songs_keys = list(wanted_songs.keys())
        if len(wanted_songs_keys) is not len(config_json_data['albums']):
            print("{0} albums wanted, only {1} found.".format(len(config_json_data['albums']), len(wanted_songs_keys)))
            print("These albums weren't found.  Their're probly misspeled.")

            # Prints albums that aren't in both lists
            # Thanks StackOverflow!
            missing_albums = []
            combined_list = wanted_songs_keys + config_json_data['albums']
            for i in range(0, len(combined_list)):
                if ((combined_list[i] not in wanted_songs_keys) or (combined_list[i] not in config_json_data['albums'])) and (combined_list[i] not in missing_albums):
                     missing_albums[len(missing_albums):] = [combined_list[i]]

            for value in missing_albums:
                print(value)
        else:
            # If not asked to be in order then shuffle
            if args.is_in_order:
                print("Unshuffling... no, really...")
                wanted_songs_keys = sorted(wanted_songs_keys, key=config_json_data['albums'].index)
            else:
                print("Shuffling")
                random.shuffle(wanted_songs_keys)

            if args.verbose:
                print("Albums are being added in this order:")
                for album in wanted_songs_keys:
                    print(album)

            for key in wanted_songs_keys:
                for track_number, track_id in wanted_songs[key].items():
                    song_ids.append(track_id)

            api.add_songs_to_playlist(new_playlist, song_ids)