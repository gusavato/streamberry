import requests
from password import *
import pandas as pd
from datetime import datetime
import time

"""
Funciones consulta API TMDB

"""

headers = {"accept": "application/json", "Authorization": f"Bearer {TOKEN}"}


def search_id(title, year):
    """Función que devuelve el id de TMDB para un título"""

    format_title = title.replace(' ', '%20')

    url = f"https://api.themoviedb.org/3/search/movie?query={format_title}&include_adult=false&language=ES&page=1&year={year}"

    response = requests.get(url, headers=headers).json()

    return response['results'][0]['id']


def get_details(TMDB_id):
    """Función que devuelve los detalles de la pelicula"""

    url = f"https://api.themoviedb.org/3/movie/{TMDB_id}?language=ES"

    response = requests.get(url, headers=headers).json()

    dictio = dict()
    dictio['Titulo'] = response['title']
    dictio['Titulo_Original'] = response['original_title']
    dictio['Year'] = datetime.strptime(
        response['release_date'], '%Y-%m-%d').year
    dictio['Duracion'] = response['runtime']
    dictio['Tag_Line'] = response['tagline']
    dictio['Sinopsis'] = response['overview']
    dictio['Genero'] = [gen['name'] for gen in response['genres']]
    dictio['TMDB_rate'] = response['vote_average']
    dictio['Poster'] = 'https://image.tmdb.org/t/p/w400' + \
        response['poster_path']
    dictio['Productoras'] = [prod['name']
                             for prod in response['production_companies']]
    dictio['Pais'] = [country['iso_3166_1']
                      for country in response['production_countries']]
    dictio['Fecha_Estreno'] = datetime.strptime(
        response['release_date'], '%Y-%m-%d').strftime('%d-%m-%Y')
    dictio['TMDB_id'] = response['id']
    dictio['IMDB_id'] = response['imdb_id']

    return dictio


def get_cast(TMDB_id):
    """Función que retorna los 8 primeros actores de una película"""

    url = f"https://api.themoviedb.org/3/movie/{TMDB_id}/credits?language=ES"

    response = requests.get(url, headers=headers).json()

    lst = []

    for i in range(min(8, len(response['cast']))):
        dictio = dict()
        dictio['Id'] = response['cast'][i]['id']
        dictio['Nombre'] = response['cast'][i]['name']
        dictio['Foto'] = 'https://image.tmdb.org/t/p/w200' + \
            response['cast'][i]['profile_path']
        lst.append(dictio)

    df = pd.DataFrame(lst)
    actors = pd.read_parquet('actors.parquet')
    actors = pd.concat(
        [actors, df], axis=0).drop_duplicates().reset_index(drop=True)
    actors.to_parquet('actors.parquet', engine='pyarrow')

    return df


def get_director_writer(TMDB_id):

    url = f"https://api.themoviedb.org/3/movie/{TMDB_id}/credits?language=ES"

    response = requests.get(url, headers=headers).json()

    df = pd.DataFrame(response['crew'])

    dictio = dict()
    dictio['Director'] = df[df.job == 'Director']['name'].to_list()
    dictio['Guion'] = df[df.job == 'Screenplay']['name'].to_list()

    return dictio


def get_video(TMDB_id):

    url = f"https://api.themoviedb.org/3/movie/{TMDB_id}/videos?language=ES"

    response = requests.get(url, headers=headers).json()

    video = 'https://www.youtube.com/watch?v=' + response['results'][0]['key']

    return video


def get_data(TMDB_id):
    """
    Función que une toda la información extraida de la API
    """

    dictio = get_details(TMDB_id)
    dictio['Reparto'] = get_cast(TMDB_id)['Id'].to_list()
    dictio = {**dictio, **get_director_writer(TMDB_id)}
    dictio['Video'] = get_video(TMDB_id)

    return dictio


def save_data():

    scan = pd.read_parquet('scan.parquet')
    files = scan[scan.API_pass == False]

    lst = []
    for i in files.itertuples():
        time.sleep(0.03)
        try:
            TMDB_id = search_id(i[1], i[2])
        except:
            continue
        dictio = get_data(TMDB_id)
        dictio['File'] = i[4]
        lst.append(dictio)
        # Modificar bool de scan
