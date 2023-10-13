import re


# TODO: move ANSIColors, SongRenderer, TextRenderer to a separate file
class ANSIColors:
    BOLD = "\033[1m"
    END = "\033[0m"


class SongRenderer:
    pass


class TextRenderer(SongRenderer):
    def __init__(self):
        pass

    def renderline(self, line, renderChords):
        if len(line.lyrics) + len(line.chords) == 0:
            return ""

        rendered_lyrics = ""
        rendered_chords = ""
        for i, chord in enumerate(line.chords):
            if i < len(line.lyrics):
                rendered_lyrics += line.lyrics[i]
            if renderChords:
                rendered_chords += (
                    " " * (len(rendered_lyrics) - len(rendered_chords)) + chord
                )
        if renderChords:
            rendered_chords += "\n"
        rendered_lyrics += line.lyrics[-1] + "\n"
        return rendered_chords + rendered_lyrics

    def render(self, song, renderChords=True):
        rendered = song.title + "\n"
        for section, lines in song.get_sections():
            # rendered += colored("\n" + section + "\n", attrs=['bold'])
            rendered += f"\n{ANSIColors.BOLD}{section}{ANSIColors.END}\n"
            for line in lines:
                rendered += self.renderline(line, renderChords)

        return rendered


class Line:
    def __init__(self, plain: str):
        self.plain_text = plain
        self.lyrics = []
        self.chords = []

    def add_lyrics(self, lyrics: str):
        self.lyrics.append(lyrics)

    def add_chord(self, chord: str):
        """
        chord: string of the chord to be added

        returns: the length of the chord
        """
        self.chords.append(chord)
        return len(chord)


class Song:
    def __init__(self, plain: str, title: str = "New Song", author: str = ""):
        self.plain_text = plain
        self.title = title
        self.author = author

        self.lines = []
        self.section = ""
        self.sections = [self.lines]

    def __str__(self):
        self.get_sections()
        return TextRenderer().render(self)

    def tokenize(self, ignore_chords=True):
        tokens = []
        sections = self.get_sections()

        for line in [line for section in sections for line in section[1]]:
            if ignore_chords:
                text = " ".join(line.lyrics)
                text = "".join(line.lyrics)
            else:
                text = " ".join(line.chords) + " ".join(line.lyrics)
            words = re.findall(r"\w+", text.lower())
            if words:
                tokens += [" ".join(words)]
        return tokens

    def display_diff(self, self_tokens, other_tokens, char="-"):
        diff_set = set(self_tokens).symmetric_difference(other_tokens)
        diff = []
        for token in self_tokens:
            if token in diff_set:
                # Check if token is a substring of a token in other_tokens
                for other_token in other_tokens:
                    if token in other_token:
                        diff.append("* " + token)
                        break
                    if other_token in token:
                        diff.append("%" + token)
                        break
                else:
                    diff.append(char + token)
            else:
                diff.append(" " + token)

        return "\n".join(diff)

    def diff(self, other, ignore_chords=True):
        # TODO: deal with similar lines
        self_tokens = self.tokenize(ignore_chords)
        other_tokens = other.tokenize(ignore_chords)

        if set(self_tokens) == set(other_tokens):
            return False
        else:
            return self.display_diff(
                self_tokens, other_tokens, char="-"
            ), self.display_diff(other_tokens, self_tokens, char="+")

    def get_sections(self):
        if self.section:  # Add the last section
            self.sections.append([self.section, self.lines[:]])
            self.section = ""
            self.lines = []

        if len(self.sections) == 1:
            return [["", self.sections[0]]]
        else:
            return self.sections[1:]

    def set_title(self, title: str):
        self.title = title

    def set_author(self, author: str):
        self.author = author

    def add_line(self, line: Line):
        if line.chords or line.lyrics:
            self.lines.append(line)

    def addSection(self, section: str):
        if self.lines:  # Add the previous section to the song
            self.sections.append([self.section, self.lines[:]])
        self.section = section
        self.lines = []
