from django.shortcuts import render, redirect
from django.http import HttpResponse
from musicapp.forms import LoginForm, SignupForm
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
import spotipy
from spotipy import SpotifyOAuth
import pandas as pd
from pandas import json_normalize
from musicapp.functions import *
import time
import webbrowser


# Create your views here.
CLIENT_ID = 'af0457bbd5df4f6c854a4d60d76e215d'
ID_SECRET = '9371a39a3e0d40d0a03b7fd04a242cd6'
SCOPE = 'ugc-image-upload user-library-read user-top-read playlist-modify-public playlist-modify-private playlist-read-private playlist-read-collaborative user-follow-modify user-follow-read user-library-modify user-library-read'
REDIRECT_URI = 'http://127.0.0.1:8000/musicapp/callback'


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('index')
    return render(request, 'musicapp/signup.html', {'form': form})


def logout_view(request):
    logout(request)
    url = 'https://www.spotify.com/es/logout/'
    webbrowser.open(url)
    return redirect('index')


def login_spotify(request):
    auth = spotipy.oauth2.SpotifyOAuth(
        username=request.user, client_id=CLIENT_ID, client_secret=ID_SECRET, redirect_uri=REDIRECT_URI, scope=SCOPE)
    return redirect(auth.get_authorize_url())


def index(request):
    loginError = ""

    if 'username' in request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
        else:
            loginError = "Error de login"

    loginForm = LoginForm()
    signupForm = SignupForm()

    if request.user.is_authenticated:
        context = {'user': request.user, 'login_form': loginForm,
                   'signup_form': signupForm, 'loginError': loginError}
        return redirect('login_spotify')
    else:
        context = {'login_form': loginForm, 'signup_form': signupForm, 'loginError': loginError}
        return render(request, 'musicapp/index.html', context)


def callback(request):
    auth = spotipy.oauth2.SpotifyOAuth(
        username=request.user, client_id=CLIENT_ID, client_secret=ID_SECRET, redirect_uri=REDIRECT_URI, scope=SCOPE)
    token_info = auth.get_access_token(code=request.GET.get('code'))
    request.session['id'] = None
    # Refreshing token if it has expired
    if (token_info['expires_at'] - int(time.time()) < 60):
        auth = spotipy.oauth2.SpotifyOAuth(
            username=request.user, client_id=CLIENT_ID, client_secret=ID_SECRET, redirect_uri=REDIRECT_URI, scope=SCOPE)
        token_info = auth.refresh_access_token(token_info['refresh_token'])

    request.session['token_info'] = token_info
    sp = spotipy.Spotify(auth=token_info['access_token'])

    request.session['user_info'] = sp.current_user()
    request.session['n'] = 0

    playlist = get_user_playlists(20, sp)
    playlist_html = playlist.to_html(index=False, index_names=False,
                                     classes='table table-striped', justify='center')

    canciones = get_user_songs(20, sp)
    canciones_html = canciones.to_html(index=False, index_names=False,
                                       classes='table table-striped', justify='center')

    albums = get_user_albums(20, sp)
    albums_html = albums.to_html(index=False, index_names=False,
                                 classes='table table-striped', justify='center', escape=False)

    artist = get_user_artist(20, sp)
    artists_html = artist.to_html(index=False, index_names=False,
                                  classes='table table-striped', justify='center', escape=False)

    podcasts = get_user_shows(20, sp)
    podcasts_html = podcasts.to_html(index=False, index_names=False,
                                     classes='table table-striped', justify='center', escape=False)

    context = {'playlists': playlist_html, 'canciones': canciones_html,
               'albums': albums_html, 'artists': artists_html, 'podcasts': podcasts_html, 'id': request.session['user_info']['id']}
    return render(request, 'musicapp/page1.html', context)


def search(request):

    tipo = (request.POST.get('comboType'))
    request.session['tipo'] = tipo
    nombre = request.POST.get('findBar')
    request.session['nombre'] = nombre
    request.session['nombre_cancion'] = nombre

    if tipo == 'artist':
        return redirect('artist')
    elif tipo == 'track':
        return redirect('track')
    elif tipo == 'playlist':
        return redirect('playlist')
    elif tipo == 'show':
        return redirect('show')
    elif tipo == 'album':
        return redirect('album')

    tipo = tipo.upper()


def artist(request):

    token_info = request.session['token_info']
    sp = spotipy.Spotify(auth=token_info['access_token'])
    nombre = request.session['nombre']

    tipo = request.session['tipo']

    siguiente = request.session['n']
    si = True
    ord = ""
    list = siguiente_item(siguiente, request.session['n'], si, request.POST.get('comboOrd'),
                          request.POST.get('systemForm'), request.POST.get('systemForm2'))
    siguiente = list[0]
    request.session['n'] = list[1]
    si = list[2]
    ord = list[3]

    resultado = search_box(nombre, 1, siguiente, tipo, sp)
    if resultado is None:
        return render(request, 'musicapp/noexiste.html')
    else:
        res = info_wikipedia(resultado.name[0])
        info = info_noticias(resultado.name[0], 5)
        request.session['id'] = resultado.id[0]
        imagen = set_images(resultado, 'images', 0, 0)

        artist_albums = get_artist_albums(resultado.id[0], sp)

        if ord is None or ord == "":
            albums_html = artist_albums.to_html(
                index=False, index_names=False, classes='table table-striped', justify='center', escape=False)
        else:
            albums_html = artist_albums.sort_values(ord).to_html(
                index=False, index_names=False, classes='table table-striped', justify='center', escape=False)

        artist_top_tracks = get_artist_tracks(resultado.id[0], sp)
        artist_top_tracks = artist_top_tracks.style.bar(
            subset=['Popularidad'], align='mid', color='orange').hide_index().render(uuid="my_id")

        follow = sp.current_user_following_artists([resultado.id[0]])

        resultado['genres'] = set_dataframe_artist_genre(resultado, 'genres', 'genero')
        context = {'nombre': resultado.name[0], 'imagen': imagen, 'genero': resultado['genres'][0],
                   'tipo': tipo, 'albums': albums_html, 'tracks': artist_top_tracks, 'resumen': res, 'noticias': info, 'is_follow': follow[0], 'si': si}
        return render(request, 'musicapp/artista.html', context)


def track(request):

    token_info = request.session['token_info']
    sp = spotipy.Spotify(auth=token_info['access_token'])
    tipo = 'track'
    siguiente = request.session['n']
    si = True
    add_track = request.POST.get('add_track')
    if add_track is not None:
        nombre = request.POST.get('add_input')
        request.session['nombre_cancion'] = nombre
    else:
        nombre = request.session['nombre_cancion']

    list = siguiente_item(siguiente, request.session['n'], si, None,
                          request.POST.get('systemForm'), request.POST.get('systemForm2'))
    siguiente = list[0]
    request.session['n'] = list[1]
    si = list[2]

    resultado = search_box(nombre, 1, siguiente, tipo, sp)
    if resultado is None:
        return render(request, 'musicapp/noexiste.html')
    else:
        request.session['id_track'] = resultado.id[0]
        letra = get_lyrics(resultado['artists'][0][0]['name'], resultado.name[0])
        letra = "</br><br>".join(letra.split("\n"))
        letra = '<br>' + letra
        added = sp.current_user_saved_tracks_contains([resultado.id[0]])
        resultado['artists'] = set_dataframe_artist_genre(resultado, 'artists', 'artista')
        imagen = set_images(resultado, 'album.images', 0, 0)
        resultado['duration_ms'] = pd.to_datetime(resultado['duration_ms'], unit='ms').dt.strftime('%H:%M:%S')
        context = {'Titulo': resultado.name[0], 'imagen': imagen,
                   'tipo': tipo, 'artistas': resultado['artists'][0],
                   'is_added': added[0], 'letra': letra, 'si': si,
                   'id_playlist': request.session['id'], 'is_explicit': resultado.explicit[0], 'duracion': resultado.duration_ms[0]}
        return render(request, 'musicapp/cancion.html', context)


def playlist(request):

    token_info = request.session['token_info']
    sp = spotipy.Spotify(auth=token_info['access_token'])

    tipo = 'playlist'
    if request.session['id'] is None:
        nombre = request.session['nombre']
        resultado = search_box(nombre, 1, 0, tipo, sp)
        request.session['id'] = resultado.id[0]
        name = resultado.name[0]
        owner = resultado['owner.display_name'][0]
        owner_id = resultado['owner.id'][0]
        total = resultado['tracks.total'][0]
        descripcion = resultado['description'][0]
    else:
        resultado = sp.playlist(request.session['id'])
        request.session['nombre'] = resultado['name']
        request.session['id'] = resultado['id']
        name = resultado['name']
        owner = resultado['owner']['display_name']
        owner_id = resultado['owner']['id']
        total = resultado['tracks']['total']
        descripcion = resultado['description']

    if resultado is None:
        return render(request, 'musicapp/noexiste.html')
    else:

        imagen = set_images(resultado, 'images', 0, 0)

        follow = sp.playlist_is_following(
            request.session['id'], [request.session['user_info']['id']])

        if request.session['user_info']['id'] == owner_id:
            is_owner = True
        else:
            is_owner = False

        playlist_tracks = get_playlist_tracks(request.session['id'], sp)
        ord = request.POST.get('comboOrd')
        if ord is None or ord == "":
            playlist_tracks_html = playlist_tracks.to_html(index=False, index_names=False,
                                                           classes='table table-striped',
                                                           justify='center', escape=False)
        else:
            playlist_tracks_html = playlist_tracks.sort_values(ord).to_html(index=False, index_names=False,
                                                                            classes='table table-striped',
                                                                            justify='center', escape=False)
        context = {'Nombre': name, 'imagen': imagen, 'tipo': tipo,
                   'propietario': owner, 'canciones': 'Canciones: ' + str(total),
                   'tracks': playlist_tracks_html, 'ord': ord, 'is_follow': follow[0],
                   'descripcion': descripcion, 'is_owner': is_owner}

        return render(request, 'musicapp/playlist.html', context)


def show(request):

    token_info = request.session['token_info']
    sp = spotipy.Spotify(auth=token_info['access_token'])
    nombre = request.session['nombre']
    tipo = request.session['tipo']

    siguiente = request.session['n']
    si = True
    ord = ""
    list = siguiente_item(siguiente, request.session['n'], si, request.POST.get('comboOrd'),
                          request.POST.get('systemForm'), request.POST.get('systemForm2'))
    siguiente = list[0]
    request.session['n'] = list[1]
    si = list[2]
    ord = list[3]

    resultado = search_box(nombre, 1, siguiente, tipo, sp)
    if resultado is None:
        return render(request, 'musicapp/noexiste.html')
    else:

        request.session['id'] = resultado.id[0]
        added = sp.current_user_saved_shows_contains([resultado.id[0]])
        show_episodes = get_show_episodes(resultado.id[0], sp)
        imagen = set_images(resultado, 'images', 0, 0)

        if ord is None or ord == "":
            show_episodes_html = show_episodes.to_html(index=False, index_names=False,
                                                       classes='table table-striped', justify='center',
                                                       escape=False)
        else:
            show_episodes_html = show_episodes.sort_values(ord).to_html(index=False, index_names=False,
                                                                        classes='table table-striped',
                                                                        justify='center', escape=False)

        context = {'nombre': resultado.name[0], 'imagen': imagen,
                   'autor': resultado.publisher[0],
                   'Nepisodios': resultado['total_episodes'][0],
                   'descripcion': resultado.description[0], 'idioma': resultado.languages[0][0],
                   'episodios': show_episodes_html, 'is_added': added[0], 'si': si}
        return render(request, 'musicapp/podcast.html', context)


def album(request):

    token_info = request.session['token_info']
    sp = spotipy.Spotify(auth=token_info['access_token'])
    nombre = request.session['nombre']
    tipo = request.session['tipo']

    siguiente = request.session['n']
    si = True
    ord = ""
    list = siguiente_item(siguiente, request.session['n'], si, request.POST.get('comboOrd'),
                          request.POST.get('systemForm'), request.POST.get('systemForm2'))
    siguiente = list[0]
    request.session['n'] = list[1]
    si = list[2]
    ord = list[3]

    resultado = search_box(nombre, 1, siguiente, tipo, sp)
    if resultado is None:
        return render(request, 'musicapp/noexiste.html')
    else:
        request.session['id'] = resultado.id[0]
        added = sp.current_user_saved_albums_contains([resultado.id[0]])
        album_tracks = get_album_tracks(resultado.id[0], sp)
        imagen = set_images(resultado, 'images', 0, 0)

        if ord is None or ord == "":
            album_tracks_html = album_tracks.to_html(index=False, index_names=False,
                                                     classes='table table-striped', justify='center',
                                                     escape=False)
        else:
            album_tracks_html = album_tracks.sort_values(ord).to_html(index=False, index_names=False,
                                                                      classes='table table-striped', justify='center',
                                                                      escape=False)

        resultado = set_dataframe_artist_genre(resultado, 'artists', 'artista')
        context = {'Nombre': resultado.name[0], 'imagen': imagen,
                   'tipo': tipo, 'artistas': resultado.artists[0],
                   'canciones': resultado['total_tracks'][0],
                   'fecha': resultado['release_date'][0], 'tracks': album_tracks_html,
                   'is_added': added[0], 'si': si}

        return render(request, 'musicapp/album.html', context)


def createplaylists(request):
    user_id = request.session['user_info']['id']
    token_info = request.session['token_info']
    sp = spotipy.Spotify(auth=token_info['access_token'])
    nombre = request.POST.get('findBarName')
    descripcion = request.POST.get('texareaDescription')
    playlist = sp.user_playlist_create(user_id, nombre, None, None, descripcion)
    request.session['id'] = playlist['id']
    return redirect('playlist')


def perfil(request):
    token_info = request.session['token_info']
    sp = spotipy.Spotify(auth=token_info['access_token'])

    tipo = request.POST.get('comboPer')
    count = request.POST.get('comboCount')

    if tipo is None:
        tipo = 'long_term'

    if count == '':
        count = 25

    artists = user_top_artists(count, 0, tipo, sp)
    artists_html = artists.to_html(
        index=False, classes='table table-striped', justify='center', escape=False)

    canciones = user_top_tracks(count, 0, tipo, sp)
    canciones_html = canciones.to_html(
        index=False, classes='table table-striped', justify='center', escape=False)

    imagen = request.session['user_info']['images']
    if imagen != []:
        imagen = imagen[0]['url']

    context = {'artists': artists_html, 'tracks': canciones_html,
               'followers': request.session['user_info']['followers']['total'],
               'perfil': request.session['user_info']['external_urls']['spotify'],
               'imagen': imagen,
               'id': request.session['user_info']['id']}

    return render(request, 'musicapp/perfil.html', context)


def follow_artist(request):

    token_info = request.session['token_info']
    sp = spotipy.Spotify(auth=token_info['access_token'])
    sp.user_follow_artists([request.session['id']])
    return redirect('artist')


def unfollow_artist(request):

    token_info = request.session['token_info']
    sp = spotipy.Spotify(auth=token_info['access_token'])
    sp.user_unfollow_artists([request.session['id']])
    return redirect('artist')


def add_track(request):

    token_info = request.session['token_info']
    sp = spotipy.Spotify(auth=token_info['access_token'])
    sp.current_user_saved_tracks_add([request.session['id_track']])
    return redirect('track')


def remove_track(request):

    token_info = request.session['token_info']
    sp = spotipy.Spotify(auth=token_info['access_token'])
    sp.current_user_saved_tracks_delete([request.session['id_track']])
    return redirect('track')


def follow_playlist(request):

    token_info = request.session['token_info']
    sp = spotipy.Spotify(auth=token_info['access_token'])
    sp.current_user_follow_playlist(request.session['id'])
    return redirect('playlist')


def unfollow_playlist(request):

    token_info = request.session['token_info']
    sp = spotipy.Spotify(auth=token_info['access_token'])
    sp.current_user_unfollow_playlist(request.session['id'])
    return redirect('playlist')


def add_show(request):
    token_info = request.session['token_info']
    sp = spotipy.Spotify(auth=token_info['access_token'])
    sp.current_user_saved_shows_add([request.session['id']])
    return redirect('show')


def remove_show(request):
    token_info = request.session['token_info']
    sp = spotipy.Spotify(auth=token_info['access_token'])
    sp.current_user_saved_shows_delete([request.session['id']])
    return redirect('show')


def add_album(request):
    token_info = request.session['token_info']
    sp = spotipy.Spotify(auth=token_info['access_token'])
    sp.current_user_saved_albums_add([request.session['id']])
    return redirect('album')


def remove_album(request):
    token_info = request.session['token_info']
    sp = spotipy.Spotify(auth=token_info['access_token'])
    sp.current_user_saved_albums_delete([request.session['id']])
    return redirect('album')


def edit_playlist(request):
    token_info = request.session['token_info']
    sp = spotipy.Spotify(auth=token_info['access_token'])

    if request.POST.get('editName') == "":
        nombre = request.session['nombre']
    else:
        nombre = request.POST.get('editName')
        request.session['nombre'] = nombre

    if request.POST.get('editDescription') == "":
        descripcion = None
    else:
        descripcion = request.POST.get('editDescription')

    sp.user_playlist_change_details(
        request.session['user_info']['id'], request.session['id'], nombre, None, None, descripcion)
    return redirect('playlist')


def add_track_playlist(request):

    token_info = request.session['token_info']
    sp = spotipy.Spotify(auth=token_info['access_token'])
    nombre = request.POST.get('findBarName')
    request.session['nombre'] = nombre

    canciones = sp.user_playlist_tracks(
        request.session['user_info']['id'], request.session['id'], None, 100, 0, None)

    if canciones['total'] != 0:
        for x in canciones['items']:
            if request.session['id_track'] == x['track']['id']:
                context = {'ya_esta': "La cancion ya está añadida en la playlist"}
                return render(request, 'musicapp/added.html', context)
            else:
                id_cancion = request.session['id_track']
                sp.user_playlist_add_tracks(
                    request.session['user_info']['id'], request.session['id'], [id_cancion], None)
                return redirect('playlist')
    else:
        id_cancion = request.session['id_track']
        sp.user_playlist_add_tracks(
            request.session['user_info']['id'], request.session['id'], [id_cancion], None)
        return redirect('playlist')


def remove_track_playlist(request):

    token_info = request.session['token_info']
    sp = spotipy.Spotify(auth=token_info['access_token'])
    nombre = request.POST.get('findBarName')

    canciones = sp.user_playlist_tracks(
        request.session['user_info']['id'], request.session['id'], None, 100, 0, None)
    cancion = search_box(nombre, 1, 0, 'track', sp)
    pos = 0

    if cancion is not None:
        for x in canciones['items']:
            if cancion['id'][0] == x['track']['id']:
                sp.user_playlist_remove_specific_occurrences_of_tracks(request.session['user_info']['id'], request.session['id'], [
                                                                       {"uri": x['track']['uri'], "positions": [pos]}], None)
                return redirect('playlist')
            pos += 1

            context = {'no_esta': "La cancion que desea eliminar no se encuentra en la playlist"}
            return render(request, 'musicapp/added.html', context)
    else:
        return render(request, 'musicapp/noexiste.html')

    context = {'no_esta': "La cancion que desea eliminar no se encuentra en la playlist"}
    return render(request, 'musicapp/added.html', context)
