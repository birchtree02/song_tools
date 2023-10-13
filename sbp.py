import json
import logging
import os
import re
import zipfile
from typing import Tuple

FOLDER_NAME = "songs-folder"
SBP_FILE = re.compile(".*\.sbp *[0-9]*")


class SBP_backup:
    def __init__(self, backup_file=None, backup_text=None, folder=FOLDER_NAME):
        """
        backup_file (str): Name of the sbp backup file
        """

        self.folder = folder
        if not self.folder:
            self.folder = FOLDER_NAME
            if not os.path.exists(self.folder):
                os.makedirs(self.folder)

        if backup_file:
            logging.info("Loading backup file: %s", backup_file)
            self._load_backup(backup_file)
        else:
            if backup_text:
                logging.info("Loading backup text")
                self._load_backup_from_text(backup_text)
            else:
                logging.debug(backup_text)
                raise ValueError("Must provide either backup_file or backup_text")

        #'Id', 'author', 'Capo', 'content', 'hash', 'key', 'KeyShift', 'name', 'subTitle', 'type', 'ModifiedDateTime', 'Deleted', 'SyncId', 'timeSig', 'ZoomFactor', 'Duration', 'Duration2', '_displayParams', 'TempoInt', '_tags', 'Url', 'Copyright', 'NotesText', 'Zoom', 'SectionOrder', 'SongNumber', 'HasChildren', 'ParentId', 'vName', 'locked', 'LinkedAudio', 'Chords', 'midiOnLoad', '_folders', 'drawingPathsBackup'])

        self.songs_data = self.data["songs"]
        self.song_names = [song["name"] for song in self.songs_data]
        self.songs_dict = {
            song["Id"]: {
                "name": song["name"],
                "content": song["content"],
                "author": song["author"],
            }
            for song in self.songs_data
        }
        self.sets = []

    def _load_backup(self, backup_file):  # TODO: work from a zip
        if re.match(SBP_FILE, backup_file):
            with zipfile.ZipFile(backup_file, mode="r") as backup:
                self._load_backup_from_text(
                    backup.read("dataFile.txt").decode("utf-8").split("\n")[1]
                )
        else:
            self._load_backup_file(backup_file)

    def _load_backup_file(self, backup_file):
        with open(backup_file, "r") as f:
            self.data = json.loads(f.readlines()[1])

    def _load_backup_from_text(self, text):
        text = text.split("\n")[1]
        self.data = json.loads(text)

    def create_all_cho_files(self):
        logging.info(f"Creating {len(self.songs_dict)} .cho files:")
        for songid in self.songs_dict.keys():
            filename = self.get_song_file_from_id(songid)
            logging.info(f"\t{filename}")

    def _display_song_names_id(self):
        for songid in self.songs_dict.keys():
            logging.info(f'{str(songid).zfill(3)} {self.songs_dict[songid]["name"]}')

    def get_song_file_from_id(self, song_id):
        song_id = int(song_id)
        if filename := self._check_song_file_exists(song_id):
            return filename
        else:
            return self._create_song_file_from_id(song_id)

    def _create_filename(self, song_id, ext=".cho"):
        return (
            str(song_id)
            + "_"
            + self.songs_dict[song_id]["name"].lower().replace(" ", "_")
            + ext
        )

    def _check_song_file_exists(self, song_id):
        for file in os.listdir(self.folder):
            if file.startswith(str(song_id)):
                return os.path.join(self.folder, file)

    def _create_song_file_from_id(self, song_id):
        filename = os.path.join(self.folder, self._create_filename(song_id))
        song = self.songs_dict[song_id]
        with open(filename, "w") as f:
            # # write header data
            print("{" + f'title: {song["name"]}' + "}", file=f)
            print("{" + f'author: {song["author"]}' + "}", file=f)

            # write content
            print(song["content"], file=f)

        return filename

    def get_setlist_names(self):
        self._load_setlists()
        for i, set in enumerate(self.sets):
            logging.info(f'{i} {set["details"]["name"]}')

    def _load_setlists(self):
        self.sets = self.data["sets"]

    def _get_song_info(self, id):
        song = self.songs_dict[id]
        return [song["name"], song["author"], id]

    def aggregate_notes(self, notes):
        aggregated_note = ""
        for note in notes:
            note = json.loads(note)
            aggregated_note += f"\n**{note.pop(0)['insert']}**\n"
            aggregated_note += "\n".join([line["insert"] for line in note])

        return aggregated_note

    def get_setlist_info(self, set_id) -> Tuple[list, list]:
        if not self.sets:
            self._load_setlists()
        songs = []
        notes = []
        for song in self.sets[set_id]["contents"]:
            if song["SongId"] == 0:  # Handle notes
                # Id, Order, Capo, SetId, SongId, keyOfset, ModifiedDateTime, Deleted, SyncId, NotesText, SectionOrder, ItemType, Content
                notes.append(song["Content"])
            else:
                songs.append(self._get_song_info(song["SongId"]))
        notes = self.aggregate_notes(notes)
        return songs, notes

    def removeParentheses(self, string):
        m = re.search("\\([^)]*\\)", string)
        string = string[: m.start()] + string[m.end() :] if m else string
        m = re.search("\\[[^)]*\\]", string)
        string = string[: m.start()] + string[m.end() :] if m else string
        return string


if __name__ == "__main__":
    import sys

    from spotify_tools import SpotifyTools

    # sbp = SBP_backup('files/dataFile.txt')
    sbp = SBP_backup(sys.argv[1])
    if len(sys.argv) > 2:
        FOLDER_NAME = sys.argv[2]
        logging.info(FOLDER_NAME)
    sbp.create_all_cho_files()
