from django.test import TestCase
from django.contrib.auth import models
import spotipy
import spotipy.util as util
from django.urls import reverse
import wikipediaapi

CLIENT_ID = 'af0457bbd5df4f6c854a4d60d76e215d'
ID_SECRET = '9371a39a3e0d40d0a03b7fd04a242cd6'
SCOPE = 'ugc-image-upload user-library-read user-top-read playlist-modify-public playlist-modify-private playlist-read-private playlist-read-collaborative user-follow-modify user-follow-read user-library-modify user-library-read'
REDIRECT_URI = 'http://127.0.0.1:8000/musicapp/callback'

token = util.prompt_for_user_token('test', SCOPE, client_id=CLIENT_ID, client_secret=ID_SECRET, redirect_uri=REDIRECT_URI)
sp = spotipy.Spotify(auth=token)
user_id = sp.current_user()['id']


class ViewsResourceTestCase(TestCase):

    def setUp(self):
        models.User.objects.create(username="test", password="test_pass_99")

    def test_callback(self):
        self.client.login(username="test", password="test_pass_99")
        response = self.client.post(reverse('callback'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'musicapp/page1.html')

    def test_playlist(self):

        # Crear playlist
        user = sp.current_user()['display_name']

        name = 'Prueba1'
        description = 'Descripcion de prueba1'

        playlist = sp.user_playlist_create(user, name, public=True, collaborative=False, description=description)
        playlist_id = playlist['id']

        # Get Playlist y comprobar
        playlist_checkl = sp.playlist(playlist_id)
        self.assertEqual(playlist_checkl['owner']['display_name'], user)
        self.assertEqual(playlist_checkl['name'], name)
        self.assertEqual(playlist_checkl['description'], description)

        # Editar Playlist
        # ---------------
        # Cambiar nombre de la playlist
        name = 'Prueba2'
        sp.user_playlist_change_details(user_id, playlist_id, name=name, public=None, collaborative=None, description=None)
        playlist_checkl = sp.playlist(playlist_id)
        self.assertEqual(playlist_checkl['name'], name)

        # Cambiar descripcion de la playlist

        description = 'Descripcion de prueba2 '
        sp.user_playlist_change_details(user_id, playlist_id, name=None, public=None, collaborative=None, description=description)
        playlist_checkl = sp.playlist(playlist_id)
        self.assertEqual(playlist_checkl['description'], description)

        # Editar canciones playlist
        # -------------------------
        # Metemos una cancion
        cancion_id = '1lCRw5FEZ1gPDNPzy1K4zW'
        sp.user_playlist_add_tracks(user_id, playlist_id, [cancion_id], None)

        # Comprobar que están las canciones
        canciones = sp.playlist_tracks(playlist_id)
        is_added = False
        for x in canciones['items']:
            if x['track']['id'] == cancion_id:
                is_added = True

        self.assertTrue(is_added)

        # Quitar cancion
        sp.user_playlist_remove_specific_occurrences_of_tracks(user_id, playlist_id, [{"uri": canciones['items'][0]['track']['uri'], "positions": [0]}], None)

        canciones = sp.playlist_tracks(playlist_id)

        is_removed = True
        # # Comprobar que se eliminó
        for x in canciones['items']:
            if x['track']['id'] == cancion_id:
                is_removed = False

        self.assertTrue(is_removed)

    def test_follow_unfollow_artist(self):

        artist_id = '1dfeR4HaWDbWqFHLkxsg1d'

        # Seguir artista
        sp.user_follow_artists([artist_id])

        # Comprobar que lo sigue
        follow = sp.current_user_following_artists([artist_id])
        self.assertTrue(follow[0])

        # Dejar de seguir artista
        sp.user_unfollow_artists([artist_id])

        # Comprobar que no se sigue artista
        unfollow = sp.current_user_following_artists([artist_id])
        self.assertFalse(unfollow[0])

    def test_follow_unfollow_playlist(self):
        playlist_id = '2eFGqWotVd06fPej6IYn7g'

        # Seguir Playlist
        sp.current_user_follow_playlist(playlist_id)

        # Comprobar que la sigue
        is_following = sp.playlist_is_following(playlist_id, [user_id])
        self.assertTrue(is_following[0])

        # Dejar de seguir playlist
        sp.current_user_unfollow_playlist(playlist_id)

        # Comprobar que no se sigue playlist
        is_following = sp.playlist_is_following(playlist_id, [user_id])
        self.assertFalse(is_following[0])

    def test_follow_unfollow_show(self):
        show_id = '5iKz9gAsyuQ1xLG6MFLtQg'

        # Seguir Show
        sp.current_user_saved_shows_add([show_id])

        # Comprobar que la sigue
        is_following = sp.current_user_saved_shows_contains([show_id])
        self.assertTrue(is_following[0])

        # Dejar de seguir al  Show
        sp.current_user_saved_shows_delete([show_id])

        # Comprobar que no se sigue el Show
        is_following = sp.current_user_saved_shows_contains([show_id])
        self.assertFalse(is_following[0])

    def test_follow_unfollow_album(self):
        album_id = '6SbrIpVsaJ5wgCQtMMwVR2'

        # Seguir Album
        sp.current_user_saved_albums_add([album_id])

        # Comprobar que lo sigue
        is_following = sp.current_user_saved_albums_contains([album_id])
        self.assertTrue(is_following[0])

        # Dejar de seguir al Album
        sp.current_user_saved_albums_delete([album_id])

        # Comprobar que no se sigue el Album
        is_following = sp.current_user_saved_albums_contains([album_id])
        self.assertFalse(is_following[0])

    def test_follow_unfollow_track(self):
        cancion_id = '1lCRw5FEZ1gPDNPzy1K4zW'

        # Añadir Cancion
        sp.current_user_saved_tracks_add([cancion_id])

        # Comprobar que la añadió
        is_following = sp.current_user_saved_tracks_contains([cancion_id])
        self.assertTrue(is_following[0])

        # Eliminarla de la biblioteca
        sp.current_user_saved_tracks_delete([cancion_id])

        # Comprobar que el usuario ya no sigue esa cancion
        is_following = sp.current_user_saved_tracks_contains([cancion_id])
        self.assertFalse(is_following[0])

    def test_search_wikipedia(self):

        artist_name = "Queen"
        wiki = wikipediaapi.Wikipedia('es')
        page = wiki.page(artist_name)
        self.assertTrue(page.exists())
