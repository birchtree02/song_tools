import difflib
import logging
import os
import sqlite3
import xml.etree.ElementTree as ET
from typing import List

import requests
from openlyrics_parser import OpenLyricsParser
from song import Song


class Service:
    def __init__(self):
        self.conn_url = "http://0.0.0.0:4316/api/v2"

    def make_request(self, url: str, method: str, data: dict = None):
        return requests.request(method, self.conn_url + url, json=data)

    def add_song(self, song: Song):
        service_song = self.make_request(
            "/plugins/songs/search?text=" + song.title, "GET"
        ).json()
        if service_song:
            service_song = service_song[0][0]  # id of first item
            print(service_song)
            return self.add_song_by_id(service_song)
        else:
            pass

    def add_song_by_id(self, song_id: int):
        logging.info(f"Adding song with id {song_id}")
        return self.make_request(
            "/plugins/songs/add", "POST", data={"id": int(song_id)}
        )


service = Service()


def load_database(data_dir: str):
    SONGS_DB = os.path.join(data_dir, "songs", "songs.sqlite")
    # Connect to the database
    conn = sqlite3.connect(SONGS_DB)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT songs.title, songs.alternate_title, songs.lyrics, songs.ccli_number, songs.search_title, songs.search_lyrics, authors.display_name, songs.id
        FROM songs
        JOIN authors_songs ON songs.id = authors_songs.song_id
        JOIN authors ON authors_songs.author_id = authors.id
    """
    )

    openlp_songs = cursor.fetchall()
    conn.close()

    return openlp_songs


def get_all_songs(openlp: List[tuple]) -> List[Song]:
    pass


def get_songs(songs: List[Song]):
    pass


def find_song(song_to_find: Song, openlp: List[tuple]):
    titles = [song[4].strip("@") for song in openlp]

    matched_songs = difflib.get_close_matches(
        song_to_find.title.lower(), titles, cutoff=0, n=1
    )

    matched_openlp = [song for song in openlp if song[4].strip("@") in matched_songs]
    matched_openlp.sort(key=lambda song: matched_songs.index(song[4].strip("@")))
    return matched_songs, matched_openlp


def create_service(songs: List[Song]):
    pass


if __name__ == "__main__":
    DATA_DIR = "/Users/edwardbirchall/Library/Application Support/openlp/Data"
    openlp_songs = load_database(DATA_DIR)

    TEST_TITLE = "Cannons"
    TEST_TITLE = "Be Entroned"

    test_song = Song("", title=TEST_TITLE)
    song_res = find_song(test_song, openlp_songs)
    song = OpenLyricsParser().parse_open_lyrics(
        song_res[1][0][0], song_res[1][0][6], song_res[1][0][2]
    )

    # print(song)

    service = Service()
    print(service.add_song_by_id(song_res[1][0][7]).content)

    print(service.add_song_by_id(1))

    print(service.add_song(song))
