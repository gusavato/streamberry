import os
import re
from password import FOLDER

"""
Funciones de escaneo de las ubiciones de los archivos
"""


def extract_nyf():
    """
    Función que extrae le nombre, año ,formato y nombre del archivo, para cada
    uno de los archivos ubicados en FOLDER
    """

    # Patron regex para detectar los años. Busca 4 digitos que empiecen por
    # 19xx o 20xx
    patron_y = r"\b(19\d{2}|20\d{2})\b"

    # Patron regex para extraer el título
    patron_t = r"^(.*?)(?=\()"

    new_movies = []
    for _file in os.listdir(FOLDER):
        try:
            ext = re.findall(r'\.[^.]*$', _file)[0][1:]
        except:
            continue
        if ext != 'mkv':
            continue
        try:
            name = re.findall(patron_t, _file)[0]
            name = name[:-1].replace('.', ' ')
        except:
            name = ''
        try:
            year = re.findall(patron_y, _file)[0]
        except:
            year = ''

        new_movies.append((name, year, ext, _file))

    return new_movies
