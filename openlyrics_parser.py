import xml.etree.ElementTree as ET

from song import Line, Song


class OpenLyricsParser:
    def parse_open_lyrics(self, title, author, song_xml: str) -> Song:
        song = Song(None, title, author)
        root = ET.fromstring(song_xml)
        verses = root.findall(".//verse")

        for verse in verses:
            song.addSection(
                verse.items()[0][1]
            )  # TODO: translate c: chorus, v: verse etc? and add section numbers?
            for line_text in verse.text.split("\n"):
                line = Line(line_text)
                line.add_lyrics(line_text)
                song.add_line(line)

        return song
