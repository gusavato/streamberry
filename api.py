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
    try:
        dictio['Year'] = datetime.strptime(
            response['release_date'], '%Y-%m-%d').year
    except:
        dictio['Year'] = 0
    dictio['Duracion'] = response['runtime']
    dictio['Tag_Line'] = response['tagline']
    dictio['Sinopsis'] = response['overview']
    dictio['Genero'] = [gen['name'] for gen in response['genres']]
    dictio['TMDB_rate'] = response['vote_average']
    try:
        dictio['Poster'] = 'https://image.tmdb.org/t/p/w400' + \
            response['poster_path']
    except:
        dictio['Poster'] = ''
    dictio['Productoras'] = [prod['name']
                             for prod in response['production_companies']]
    dictio['Pais'] = [country['iso_3166_1']
                      for country in response['production_countries']]
    try:
        dictio['Fecha_Estreno'] = datetime.strptime(
            response['release_date'], '%Y-%m-%d').strftime('%d-%m-%Y')
    except:
        dictio['Fecha_Estreno'] = '01-01-1900'
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
        try:
            dictio['Foto'] = 'https://image.tmdb.org/t/p/w200' + \
                response['cast'][i]['profile_path']
        except:
            dictio['Foto'] = ''
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

    try:
        video = 'https://www.youtube.com/watch?v=' + \
            response['results'][0]['key']
    except:
        try:
            url = f"https://api.themoviedb.org/3/movie/{TMDB_id}/videos?language=EN"

            response = requests.get(url, headers=headers).json()

            video = 'https://www.youtube.com/watch?v=' + \
                response['results'][0]['key']

        except:
            return ''

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


def save_data(df):
    """
    Función que almacena la nueva información en films.parquet

    """

    scan = pd.read_parquet('scan.parquet')

    lst = []
    for i in df.itertuples():
        try:
            TMDB_id = search_id(i[1], i[2])
        except:
            continue
        dictio = get_data(TMDB_id)
        dictio['Root'] = i[3]
        dictio['Folder'] = i[4]
        dictio['File'] = i[5]
        dictio['Vista'] = False
        dictio['Add'] = datetime.today().date().strftime('%d-%m-%Y')
        lst.append(dictio)
        scan.loc[i[0], 'API_pass'] = True

    scan.to_parquet('scan.parquet', engine='pyarrow')

    films = pd.read_parquet('films.parquet')

    new = pd.DataFrame(lst)

    films = pd.concat([films, new], axis=0).reset_index(drop=True)

    films.to_parquet('films.parquet', engine='pyarrow')


def solve_data(index, TMDB_id=None):
    """
    Función que permite dado el indice corregir una entrada en 
    films.parquet
    """
    films = pd.read_parquet('films.parquet')
    if TMDB_id is None:
        TMDB_id = films.loc[index, 'TMDB_id']
    dictio = get_data(TMDB_id)
    dictio['Folder'] = films.loc[index, 'File']
    dictio['File'] = films.loc[index, 'File']
    dictio['Vista'] = films.loc[index, 'Vista']
    dictio['Add'] = films.loc[index, 'Add']

    films.loc[index, :] = dictio

    films.to_parquet('films.parquet', engine='pyarrow')


def clean_scan(id_scan, TMDB_id):

    scan = pd.read_parquet('scan.parquet')

    lst = []
    for i_scan, i_TMBD in zip(id_scan, TMDB_id):
        dictio = get_data(i_TMBD)
        dictio['Folder'] = 0
        dictio['File'] = scan.loc[i_scan, 'File']
        dictio['Vista'] = False
        dictio['Add'] = datetime.today().date().strftime('%d-%m-%Y')
        lst.append(dictio)
        scan.loc[i_scan, 'API_pass'] = True

    scan.to_parquet('scan.parquet', engine='pyarrow')
    films = pd.read_parquet('films.parquet')
    new = pd.DataFrame(lst)
    films = pd.concat([films, new], axis=0).reset_index(drop=True)
    films.to_parquet('films.parquet', engine='pyarrow')
