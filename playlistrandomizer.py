#!/usr/bin

from gmusicapi import Mobileclient
import random
import datetime

import argparse
import json
import os.path
import pprint

# todo: check for playlist size limit
# todo: dumping album names and IDs to file
# todo: allow custom names
# todo: allow non-random playlists


###
# Globals
### 
CONFIG_FILENAME = "config-real.json"
CONFIG_FILE_TEMPLATE = {"username": "username", "password": "password", "albums": ["",""]}
ALBUM_DUMP_FILENAME = "album_dump.json"

# Populated from loadConfigFile()
config_json_data = ""

###
# Arguments
###
parser = argparse.ArgumentParser(
    description='Randomize a list of albums and create a Google Play Music playlist in that order')

parser.add_argument('-R',
    action='store_true',
    dest='is_randomized',
    help='Only for use with createplaylist.  Creates playlist in the order listed; that is, not randomized')

parser.add_argument('-n',
    dest='playlist_name',
    help='Only for use with createplaylist.  Specifies a name for the playlist.  If not provided it defaults to the date in MM-DD-YYYY format.')

parser.add_argument('create_file',
    choices=('createconfig', 'dumpalbums', 'createplaylist'),
    help='Which action to perform.  Allowed options: createconfig, dumpalbums, createplaylist',
    metavar='ACTION')

args = parser.parse_args()
print(args)

if args.is_randomized is True and args.create_file != 'createplaylist':
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

# Writes a brand-new config file from a template, with overwritting detection
def generateConfigFile():
    # Check if file exists then create
    if not os.path.exists(CONFIG_FILENAME):
        print("tests")
        newConfigFileFromTemplate()
        return

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


# Loads config JSON to global variable config_json_data
def loadConfigFile():
    global config_json_data
    if os.path.exists(CONFIG_FILENAME):
        with open(CONFIG_FILENAME, "r") as config_file:
            config_json_data = json.load(config_file)
            print(config_json_data)
    else:
        exit("Config file does not exist.  Please run \"python playlistrandomizer.py createconfig\" and fill in the appropriate login information.")

# Loads login data from config file and attempts to log in, exits if unable
def login():
    loadConfigFile()
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
    generateConfigFile()
    exit()

elif args.create_file == "dumpalbums":
    api = login()
    if api is not None:
        # Get list of all songs
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

        # Write to file
        with open(ALBUM_DUMP_FILENAME, "w") as album_dump_file:
            json.dump(album_list, album_dump_file, indent=4, sort_keys=True)

elif args.create_file == "createplaylist":
    api = login()
    if api is not None:
        pass

"""
# Get list of all songs
songs = api.get_all_songs()

wanted_songs = {}
for song in songs:
    for album in album_list:
        if song['album'] == album:
            if song['album'] not in wanted_songs:
                wanted_songs[song['album']] = {song['trackNumber']: song['id']}
            else:
                wanted_songs[song['album']].update({song['trackNumber']: song['id']})

# Create new playlist with today's date as name
new_playlist = api.create_playlist(datetime.datetime.now().strftime("%Y-%m-%d"))

# Goes through each album and creates a new list of all song IDs
song_ids = []
wanted_songs_keys = list(wanted_songs.keys())
if len(wanted_songs_keys) is not len(album_list):
    print("{0} albums wanted, only {1} found.".format(len(album_list), len(wanted_songs_keys)))
    print("These albums weren't found.  Their're probably misspeled.")

    # Prints albums that aren't in both lists
    missing_albums = []
    combined_list = wanted_songs_keys + album_list
    for i in range(0, len(combined_list)):
        if ((combined_list[i] not in wanted_songs_keys) or (combined_list[i] not in album_list)) and (combined_list[i] not in missing_albums):
             missing_albums[len(missing_albums):] = [combined_list[i]]

    for value in missing_albums:
        print(value)
else:
    random.shuffle(wanted_songs_keys)
    for key in wanted_songs_keys:
        for track_number, track_id in wanted_songs[key].items():
            song_ids.append(track_id)

    api.add_songs_to_playlist(new_playlist, song_ids)"""