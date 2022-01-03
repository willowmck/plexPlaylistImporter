import plexapi.exceptions
from plexapi.server import PlexServer
import mutagen
from mutagen.easyid3 import EasyID3
import argparse
import re


def make_connection(baseurl: str, token: str):
    return PlexServer(baseurl, token)


def create_playlist(plex, m3u_file):
    tracks = search_for_tracks(plex, m3u_file)
    playlist_name = m3u_file.split('/')[-1].split('.')[0].strip()
    audio = plex.library.section('Music')
    playlist = plex.createPlaylist(playlist_name, section=audio.key, items=tracks)
    print("Created playlist " + playlist.guid)


def search_for_tracks(plex, m3u_file):
    f = open(m3u_file, "r")
    lines = f.readlines()
    audio = plex.library.section('Music')
    items = []
    for line in lines:
        l: str = line.strip()
        search_string: str = ''
        if l.endswith('ogg'):
            track = mutagen.File(l)
            search_string = track['title'][0]
        elif l.endswith('mp3'):
            try:
                search_string = EasyID3(l).get('title')[0]
            except TypeError as e:
                print(str(e))

        if len(search_string) > 0:
            result = get_matching_track(plex, search_string, audio.key, l)
            if result:
                print('Adding track ' + result.guid)
                items.append(result)
            else:
                result = get_matching_track(plex, search_string, audio.key, l, strip_parens=True)
                if result:
                    print('Adding track ' + result.guid)
                    items.append(result)
                else:
                    print('ERROR: Could not find match for ' + l)
        else:
            print('DEBUG: Skipping ' + l)
    return items


def get_matching_track(plex, search_term, library_id, filename, strip_parens=False):
    try:
        results = plex.search(query=strip_appenders(search_term, strip_parens), mediatype='track', sectionId=library_id)
        if len(results) == 1:
            return results[0]
        else:
            for result in results:
                for medium in result.media:
                    for part in medium.parts:
                        if part.file == filename:
                            return result
    except plexapi.exceptions.PlexApiException as e:
        print(e)
        return None


def strip_appenders(full_title: str, strip_parens=False):
    no_prefix = strip_prefix(full_title)
    return strip_suffix(no_prefix, strip_parens)


def strip_prefix(full_title: str):
    match = re.split(r"^[0-9]*\s-", full_title)
    return match[0]


def strip_suffix(full_title: str, strip_parens=False):
    stripped_title = full_title
    start_bracket = stripped_title.find('[')
    if start_bracket > -1:
        end_bracket = stripped_title.find(']', start_bracket)
        if end_bracket > -1:
            stripped_title = stripped_title[0:start_bracket].strip()
    featuring = stripped_title.lower().find('feat.')
    if featuring > -1:
        stripped_title = stripped_title[0:featuring].strip()
    if strip_parens:
        left_paren = stripped_title.find('(')
        if left_paren > -1:
            right_paren = stripped_title.find(')', left_paren)
            if right_paren > -1:
                stripped_title = stripped_title[0:left_paren].strip()
    return stripped_title


def parse_command_line():
    parser = argparse.ArgumentParser(description='Import m3u audio playlist into Plex.')
    parser.add_argument('m3u_file', metavar='m3u', type=str, help='The audio playlist in m3u format.')
    parser.add_argument('--token', dest='token', type=str, required=True, help='Plex API token')
    parser.add_argument('--plex_url', dest='plex_url', type=str, help='Plex API URL. (Optional)',
                        default='http://localhost:32400')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_command_line()
    print("Reading playlist " + args.m3u_file)
    print("Connecting to Plex at " + args.plex_url)
    plex_instance = make_connection(baseurl=args.plex_url, token=args.token)
    create_playlist(plex_instance, args.m3u_file)
