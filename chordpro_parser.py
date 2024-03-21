import re

from song import Line, Song


class ChordProParser:
    """https://codepen.io/gschoppe/pen/wqbJZp"""

    CHORDREGEX = re.compile(r"\[([^\]]*)\]")
    INWORD = re.compile(r"[a-z]$")
    COMMENT = re.compile(r"^#")
    COMMAND = re.compile(r"^\{.*\}$")
    NOTES = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]

    def __init__(self):
        pass

    def parseChordPro(self, songString: str, title="New Song"):
        song = Song(songString, title=title)
        for line in songString.split("\n"):
            cur_line = None
            if re.match(self.COMMENT, line):
                pass
            elif re.search(self.CHORDREGEX, line):
                cur_line = Line(line)
                chordlen = 0
                for i, split in enumerate(re.split(self.CHORDREGEX, line)):
                    dash = 0
                    if i % 2 == 0:  # Lyrics
                        cur_line.add_lyrics(split)
                    else:  # Chord
                        chordlen = cur_line.add_chord(
                            split.replace("[", "").replace("]", "")
                        )
            elif re.match(self.COMMAND, line):  # command block
                matches = re.match(
                    r"^\{(title|t|subtitle|st|comment|c|author|a):\s*(.*)\}$", line
                )
                if matches:
                    if matches.group(1) == "title" or matches.group(1) == "t":
                        song.set_title(matches.group(2))
                    elif matches.group(1) == "author" or matches.group(1) == "a":
                        song.set_author(matches.group(2))
                    elif matches.group(1) == "subtitle" or matches.group(1) == "st":
                        pass
                    elif matches.group(1) == "comment" or matches.group(1) == "c":
                        cur_line = Line(line)
                        song.addSection(matches.group(2))
                else:
                    cur_line = Line(line)
            else:
                cur_line = Line(line)
                cur_line.add_lyrics(line)

            if cur_line:
                song.add_line(cur_line)
        return song


def getSongFromFile(fname: str):
    parser = ChordProParser()
    with open(fname, "r") as f:
        return parser.parseChordPro(f.read())


if __name__ == "__main__":
    import sys

    parser = ChordProParser()
    with open(sys.argv[1], "r") as f:
        song = parser.parseChordPro(f.read())

    print(song)
