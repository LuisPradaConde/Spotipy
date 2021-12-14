
import pandas as pd
from pandas import json_normalize
import spotipy
import spotipy.oauth2 as oauth
import matplotlib.pyplot as plt
import wikipediaapi
from GoogleNews import GoogleNews
import lyricsgenius

lyricsgenius_TOKEN = 'wuuxXS_LUDjHe8eD0KMf8s6eAhSpR7mqMg5fecJUBfIVjFxdB5ZbRIGBy3DtHxv_'
pd.options.mode.chained_assignment = None


def get_user_info(sp):

    info = sp.current_user()
    df_info = pd.DataFrame(json_normalize(info))
    return df_info


def get_user_playlists(count, sp):
    response = sp.current_user_playlists(limit=count)
    df = pd.DataFrame(json_normalize(response['items']))
    col_list = ['Nombre', 'Propietario', 'Canciones']
    if not df.empty:
        df = df.rename(columns={'name': 'Nombre', 'owner.display_name': 'Propietario',
                                                  'tracks.total': 'Canciones'})
        col_list = ['Nombre', 'Propietario', 'Canciones']
        return df[col_list]
    else:
        empty = pd.DataFrame(columns=col_list)
        return empty


def set_dataframe_artist_genre(data, key, modo):
    q = 0
    for x in data[key]:
        str = ' '
        i = 0
        for a in x:
            i += 1
            if (i == len(x)):
                if (modo == 'genero'):
                    str += a
                else:
                    str += a['name']
            else:
                if (modo == 'genero'):
                    str += a + ' , '
                else:
                    str += a['name'] + ' , '
        data[key][q] = str
        q += 1
    return data


def set_dataframe_images(data, key):
    q = 0
    for x in data[key]:
        if x == []:
            data[key][q] = '<img src=" [] " >'
        else:
            data[key][q] = '<img src="' + x[0]['url'] + '">'
        q += 1
    return data


def get_user_songs(count, sp):
    response = sp.current_user_saved_tracks(count)
    df = pd.json_normalize(response['items'])
    col_list = ['Título', 'Artistas']
    if not df.empty:
        df = set_dataframe_artist_genre(df, 'track.artists', 'artista')
        df = df.rename(columns={'track.name': 'Título', 'track.artists': 'Artistas',
                                'tracks.total': 'Canciones'})
        return df[col_list]
    else:
        empty = pd.DataFrame(columns=col_list)
        return empty


def get_user_albums(count, sp):
    response = sp.current_user_saved_albums(count)
    df = pd.DataFrame(json_normalize(response['items']))
    col_list = ['Imagen', 'Titulo', 'Artistas']
    if not df.empty:
        df = set_dataframe_images(df, 'album.images')
        df = set_dataframe_artist_genre(df, 'album.artists', 'artista')
        df = df.rename(columns={'album.name': 'Titulo', 'album.artists': 'Artistas',
                                'album.images': 'Imagen'})
        return df[col_list]
    else:
        empty = pd.DataFrame(columns=col_list)
        return empty


def get_user_artist(count, sp):
    response = sp.current_user_followed_artists(count)
    df = pd.DataFrame(json_normalize(response['artists']['items']))
    col_list = ['Imagen', 'Nombre']
    if not df.empty:
        df = set_dataframe_images(df, 'images')
        df = df.rename(columns={'name': 'Nombre', 'images': 'Imagen'})
        return df[col_list]
    else:
        empty = pd.DataFrame(columns=col_list)
        return empty


def get_user_shows(count, sp):
    response = sp.current_user_saved_shows(count)
    df = pd.DataFrame(json_normalize(response['items']))
    col_list = ['Imagen', 'Nombre']
    if not df.empty:
        df = set_dataframe_images(df, 'show.images')
        df = df.rename(columns={'show.name': 'Nombre', 'show.images': 'Imagen'})
        return df[col_list]
    else:
        empty = pd.DataFrame(columns=col_list)
        return empty


def search_box(q, count, offset, type, sp):
    response = sp.search(q, count, offset, type)
    type = type + 's'
    df_search = pd.DataFrame(json_normalize(response[type]['items']))
    if not df_search.empty:
        return df_search
    else:
        return None


def get_artist_albums(id, sp):
    response = sp.artist_albums(id, 'album', None, 50, 0)
    df = pd.DataFrame(json_normalize(response['items']))
    col_list = ['Imagen', 'Titulo', 'Fecha']
    if not df.empty:
        df = set_dataframe_images(df, 'images')
        df = df.rename(columns={'name': 'Titulo', 'release_date': 'Fecha',
                                'images': 'Imagen'})
        return df[col_list]
    else:
        empty = pd.DataFrame(columns=col_list)
        return empty


def get_artist_tracks(id, sp):
    response = sp.artist_top_tracks(id, 'ES')
    df = pd.DataFrame(json_normalize(response['tracks']))
    col_list = ['Titulo', 'Fecha', 'Popularidad']
    if not df.empty:
        df = df.rename(columns={'name': 'Titulo',
                       'album.release_date': 'Fecha', 'popularity': 'Popularidad'})
        return df[col_list]
    else:
        empty = pd.DataFrame(columns=col_list)
        return empty


def get_playlist_tracks(id, sp):
    response = sp.playlist_tracks(id, None, 100, 0, 'ES', ('track',))
    df = pd.DataFrame(json_normalize(response['items']))

    col_list = ['Titulo', 'Artistas', 'Album', 'Duracion', 'Fecha']
    if not df.empty:
        df = set_dataframe_artist_genre(df, 'track.artists', 'artista')
        df['track.duration_ms'] = pd.to_datetime(
            df['track.duration_ms'], unit='ms').dt.strftime('%H:%M:%S')
        df = df.rename(columns={'track.name': 'Titulo', 'track.artists': 'Artistas',
                                'track.album.name': 'Album', 'track.duration_ms': 'Duracion',
                                'track.album.release_date': 'Fecha'})
        return df[col_list]
    else:
        empty = pd.DataFrame(columns=col_list)
        return empty


def get_album_tracks(id, sp):
    response = sp.album_tracks(id, 50, 0, None)
    df = pd.DataFrame(json_normalize(response['items']))

    col_list = ['Numero', 'Titulo', 'Artistas', 'Duracion']
    if not df.empty:
        df = set_dataframe_artist_genre(df, 'artists', 'artista')
        df['duration_ms'] = pd.to_datetime(df['duration_ms'], unit='ms').dt.strftime('%H:%M:%S')
        df = df.rename(columns={'track_number': 'Numero', 'name': 'Titulo', 'artists': 'Artistas',
                                'duration_ms': 'Duracion'})
        return df[col_list]
    else:
        empty = pd.DataFrame(columns=col_list)
        return empty


def get_show_episodes(id, sp):
    response = sp.show_episodes(id, 50, 0, None)
    df = pd.DataFrame(json_normalize(response['items']))
    df['Episodio'] = range(1, (len(df)+1))
    col_list = ['Episodio', 'Nombre', 'Descripcion', 'Duracion', 'Fecha']
    if not df.empty:

        df['duration_ms'] = pd.to_datetime(df['duration_ms'], unit='ms').dt.strftime('%H:%M:%S')
        df = df.rename(columns={'name': 'Nombre', 'description': 'Descripcion',
                                'duration_ms': 'Duracion', 'release_date': 'Fecha'})
        return df[col_list]
    else:
        empty = pd.DataFrame(columns=col_list)
        return empty


def user_top_artists(n, offset, term, sp):

    response = sp.current_user_top_artists(n, 0, term)

    df = pd.DataFrame(json_normalize(response['items']))
    col_list = ['Posicion', 'Imagen', 'Artista']
    df['Posicion'] = range(1, (len(df)+1))
    if not df.empty:
        df = set_dataframe_images(df, 'images')
        df = df.rename(columns={'images': 'Imagen', 'name': 'Artista'})
        return df[col_list]
    else:
        empty = pd.DataFrame(columns=col_list)
        return empty


def user_top_tracks(n, offset, term, sp):

    response = sp.current_user_top_tracks(n, 0, term)

    df = pd.json_normalize(response['items'])
    col_list = ['Posicion', 'Imagen', 'Titulo']
    df['Posicion'] = range(1, (len(df)+1))
    if not df.empty:
        df = set_dataframe_images(df, 'album.images')
        df = df.rename(columns={'album.images': 'Imagen', 'name': 'Titulo'})
        return df[col_list]
    else:
        empty = pd.DataFrame(columns=col_list)
        return empty


def info_wikipedia(nombre):
    wiki = wikipediaapi.Wikipedia('es')
    page = wiki.page(nombre)

    if page.exists() is True:
        res = page.summary
    else:
        res = 'No se ha encontrado ninguna coincidencia en Wikipedia'
    return res


def info_noticias(nombre, n):
    google = GoogleNews()
    google.clear()
    google = GoogleNews(period='7d')
    google = GoogleNews(encode='utf-8')
    google = GoogleNews(lang='es')
    google.search(nombre + 'cantante')
    news = []
    try:
        google.search(nombre)
        for i in range(n):
            news.append({'title': google.results()[i]['title'], 'desc': google.results()[
                        i]['desc'], 'link': google.results()[i]['link']})
    except Exception:

        news = [{'title': 'No hay noticias ', 'desc': 'No hay descripcion ', 'link': 'No hay enlace '}]

    return news


def get_lyrics(artista, cancion):
    genius = lyricsgenius.Genius(lyricsgenius_TOKEN)
    genius.exclude_terms = ["(Live)"]
    song = genius.search_song(cancion, artista)

    try:
        letra = song.lyrics
    except Exception:
        letra = "No hay letra"

    return letra


def siguiente_item(siguiente, n, si, comboOrd, sf3, sf4):
    if (comboOrd is None):
        if siguiente == 0:
            si = False
            if sf3 == '1':
                siguiente = siguiente + 1
                n = siguiente
                si = True
        elif siguiente == 1:
            if sf4 == '2':
                siguiente = siguiente - 1
                n = siguiente
                si = False
            elif sf3 == '1':
                siguiente = siguiente + 1
                n = siguiente
                si = True
        elif siguiente < 0:
            si = False
            siguiente = 0
        elif siguiente > 0:
            if sf4 == '2':
                siguiente = siguiente - 1
                n = siguiente
                si = True
            elif sf3 == '1':
                siguiente = siguiente + 1
                n = siguiente
                si = True
    else:
        ord = comboOrd

    return[siguiente, n, si, comboOrd]


def set_images(data, key, i1, i2):
    if len(data[key]) != 0:
        if (data[key][i1] == []):
            imagen = []
        else:
            try:
                imagen = data[key][i1][i2]['url']
            except Exception:
                imagen = data[key][i1]['url']
    else:
        imagen = []
    return imagen
