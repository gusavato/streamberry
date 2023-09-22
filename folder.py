import os
import re
import pandas as pd

"""
Funciones de escaneo de las ubiciones de los archivos
"""


def root_file(fold):
    lst = []
    for raiz, _, archivos in os.walk(fold):
        for archivo in archivos:
            if archivo[-3:] in ['mkv', 'avi']:

                lst.append({raiz.replace(fold, '').replace('\\', ''): archivo})

    return lst


def extract_nyf(fold):
    """
    Función que extrae le nombre, año ,formato y nombre del archivo, para cada
    uno de los archivos ubicados en FOLDER
    """

    # Patron regex para detectar los años. Busca 4 digitos que empiecen por
    # 19xx o 20xx
    patron_y = r"\b(19\d{2}|20\d{2})\b"

    # Patron regex para extraer el título
    patron_t = r"^(.*?)(?=\()"

    # Cargamos df donde se registran los archivos de FOLDER
    scan = pd.read_parquet('scan.parquet')

    # Establecemos que se revisen solo los ficheros no registrados
    set_1 = set(scan.File)

    lst = root_file(fold)

    set_2 = set([a for dicc in lst for a in dicc.values()])
    set_to_scan = set_2.difference(set_1)

    # Extraemos información
    new_movies = []
    for _file in set_to_scan:

        try:
            name = re.findall(patron_t, _file)[0]
            name = name[:-1].replace('.', ' ')
        except:
            name = ''
        try:
            year = re.findall(patron_y, _file)[0]
        except:
            year = ''

        new_movies.append((name, year, ext, _file, False))

    return new_movies


def insert_scan(fold):
    """
    Función para insertar nueva información en scan.parquet 
    """
    scan = pd.read_parquet('scan.parquet')

    extract = pd.DataFrame(extract_nyf(fold), columns=scan.columns)

    if extract.empty:
        return None

    scan = pd.read_parquet('scan.parquet')

    scan = pd.concat([scan, extract], axis=0).reset_index(drop=True)

    scan.to_parquet('scan.parquet', engine='pyarrow')
