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
                dictio = dict()

                dictio['Root'] = fold
                dictio['Folder'] = raiz.replace(fold, '').replace('\\', '')
                dictio['File'] = archivo

                lst.append(dictio)

    return pd.DataFrame(lst)


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

    df = root_file(fold)

    set_2 = set(df.File)
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

        dictio = dict()
        dictio['Titulo'] = name
        dictio['Year'] = year
        dictio['Root'] = fold
        dictio['Folder'] = df[df.File == _file]['Folder'].values[0]
        dictio['File'] = _file
        dictio['API_pass'] = False

        new_movies.append(dictio)

    return pd.DataFrame(new_movies)


def insert_scan(fold):
    """
    Función para insertar nueva información en scan.parquet 
    """
    extract = extract_nyf(fold)

    if extract.empty:
        return None

    scan = pd.read_parquet('scan.parquet')

    scan = pd.concat([scan, extract], axis=0).reset_index(drop=True)

    scan.to_parquet('scan.parquet', engine='pyarrow')
