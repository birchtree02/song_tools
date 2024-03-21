from airium import Airium

from song_tools import song


class ANSIColors:
    BOLD = "\033[1m"
    END = "\033[0m"


class SongRenderer:
    # TODO: add logic for nashville/transposition
    pass


class TextRenderer(SongRenderer):
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


class HTMLRenderer(SongRenderer):
    def renderline(self, line, renderChords):
        if len(line.lyrics) + len(line.chords) == 0:
            return

        rendered_lyrics = ""
        rendered_chords = ""
        for i, chord in enumerate(line.chords):  # TODO: more sensible HTML method
            if i < len(line.lyrics):
                rendered_lyrics += line.lyrics[i]
            if renderChords:
                rendered_chords += (
                    " " * (len(rendered_lyrics) - len(rendered_chords)) + chord
                )
        if renderChords:
            rendered_chords += "<br />"
        rendered_lyrics += line.lyrics[-1] + "<br />"
        with self.page.span():
            self.page(rendered_chords)
        with self.page.span():
            self.page(rendered_lyrics)

    def render(self, song, needs_styling=False, renderChords=True):
        #     <link href="https://unpkg.com/tailwindcss@^1.0/dist/tailwind.min.css" rel="stylesheet">

        self.page = Airium()
        with self.page.html():
            if needs_styling:
                with self.page.head():
                    self.page.script(src="https://cdn.tailwindcss.com")

            with self.page.body():
                with self.page.div(klass="flex flex-wrap flex-col print:block"):
                    with self.page.h1():
                        self.page(song.title)

                    for section_name, lines in song.get_sections():
                        with self.page.div(
                            klass=f"flex flex-col flex-wrap items-start {section_name.split(' ')[0]}"
                        ):
                            with self.page.span().klass("text-2xl"):
                                self.page(section_name)
                            for line in lines:
                                with self.page.span(
                                    klass=(
                                        "grid grid-rows-2 grid-flow-col"
                                        if line.chords
                                        else ""
                                    )
                                ):
                                    for chord, lyric in zip(
                                        [""] + line.chords, line.lyrics
                                    ):
                                        if renderChords:
                                            with self.page.span(
                                                klass="row-start-1 font-medium translate-y-2 pr-1"
                                            ):
                                                self.page(chord)
                                        with self.page.span(klass="row-start-2 pr-1"):
                                            self.page(lyric)

        return str(self.page)
