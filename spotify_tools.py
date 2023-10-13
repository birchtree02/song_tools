import logging
import spotipy
import json
import os

DEFAULT_SCOPE = "playlist-modify-private"


class SpotifyTools:
    def __init__(self, username):
        with open(os.path.join(os.getcwd(), "spot_cred.json")) as f:
            credentials = json.load(f)

        os.environ["SPOTIPY_CLIENT_ID"] = credentials["CLIENT_ID"]
        os.environ["SPOTIPY_CLIENT_SECRET"] = credentials["CLIENT_SECRET"]
        os.environ["SPOTIPY_REDIRECT_URI"] = "http://localhost:8081/"
        os.environ["SPOTIPY_REDIRECT_URI"] = "http://localhost"
        token = spotipy.util.prompt_for_user_token(username, scope=DEFAULT_SCOPE)
        self.sp = spotipy.Spotify(auth=token)
        self.user = self.sp.current_user()["id"]

    def get_playlist_id_from_name(self, playlist_name):
        playlists = self.sp.user_playlists(self.user)["items"]
        for playlist in playlists:
            if playlist["name"] == playlist_name:
                return playlist["id"]

    def create_playlist(self, playlist_name, track_uris=[], public=False):
        playlist = self.sp.user_playlist_create(self.user, playlist_name, public)
        playlist = playlist["id"]
        if track_uris:
            self.add_tracks_to_playlist(playlist, track_uris)
        return playlist

    def add_tracks_to_playlist(self, playlist_id, track_uris):
        self.sp.playlist_add_items(playlist_id, track_uris)

    def get_song_uri(self, song_name, artist_name, limit=1):
        results = self.sp.search(
            q=f"{song_name} {artist_name}", type="track", limit=limit
        )["tracks"]["items"]

        return [song["uri"] for song in results]

    def get_song_details(self, song_name, artist_name, limit=1):
        results = self.sp.search(
            q=f"{song_name} {artist_name}", type="track", limit=limit
        )["tracks"]["items"]
        logging.info(results)
        return results


if __name__ in {"__main__", "__mp_main__"}:
    pass
