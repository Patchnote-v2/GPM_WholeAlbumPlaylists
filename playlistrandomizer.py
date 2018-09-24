#!/usr/bin

from gmusicapi import Mobileclient
import random
import datetime

import argparse
import json

# todo: check for playlist size limit
# todo: dumping album names and IDs to file
# todo: allow custom names
# todo: allow non-random playlists
"""
create
dump

-r
-n "Name"
"""

CONFIG_FILE_NAME = "config.json"

# Temporary?
config_json_data = ""

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


# Case sensitive!
# For albums with unicode characters (e.g. Tool's "Aenima") you have to do this: "\u00c6nima"
album_list = [
    "The Time Traveller",
    "Transcension",
    "Karnivool",
    "Persona",
    "Themata",
    "Sound Awake",
    "Asymmetry",
    "Altered State",
    "Polaris",
    "Sonder",
    "Arktis.",
    "\u00c1mr",
    "Living as Ghosts With Buildings as Teeth",
    "Feathergun",
    "Eidolon",
    "Terras Fames",
    "The Carbon Copy Silver Lining",
    "inter.funda.stifle",
    "Fables From a Mayfly: What I Tell You Three Times is True",
    "Arrows & Anchors",
    "From Mars To Sirius",
    "L'Enfant Sauvage (Special Edition)",
    "Magma",
    "Tall Poppy Syndrome",
    "Bilateral",
    "Coal",
    "The Congregation",
    "Malina",
    "Sampler 2009",
    "Cognitive",
    "Tellurian",
    "Lykaia",
    "The Way of All Flesh",
    "Golden Prayers",
    "Odyssey to the West",
    "MYR",
    "\u00c6nima",
    "10,000 Days",
    "Lateralus",
    # "Opiate",
    "Little Histories",
    "Fade",
    "Let Yourself Be Huge",
    "Beacons",
    "The Discovery",
    "Woum",
    "Subsume",
    "Hello",
    "]]][[[",
    "Portmanteau",
    "The Map Is Not the Territory",
    "The Joy of Motion",
    "The Madness Of Many",
    "Savage Sinusoid",
    "Sunhead",
    "Salt + Charcoal",
    "Singles (2012-2014)",
    "Handmade Cities",
    "The End of Everything",
    "Sweet Nothings",
    "Other Things"
]

# todo: detect if current config file is changed and ask for overwrite if true
# Writes a brand-new config file from a template
def generateConfigFile():
    template = {"username": "username", "password": "password", "albums": ["",""],}
    with open(CONFIG_FILE_NAME, "rw") as config_file:
        template_string = json.dumps(template)
        config_file_string = json.loads(write_file)
        json.dump(template, write_file)

# Loads config JSON to global variable config_json_data
def loadConfigFile():
    with open(CONFIG_FILE_NAME, "r") as config_file:
        config_json_data = json.load(config_file)


"""
# Temporary to load from external file
file = open("config-real", 'r')
username = file.readline()
password = file.readline()

api = Mobileclient(debug_logging=False)
logged_in = api.login(username, password, Mobileclient.FROM_MAC_ADDRESS)

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