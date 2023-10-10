import streamlit as st
import pandas as pd
from unidecode import unidecode

# Funciones botones


def click_back():
    index = st.session_state.box[0]
    if index == 0:
        st.session_state.box = tuple_list[-1]
    else:
        st.session_state.box = tuple_list[index - 1]
    if len(gen_var) < 4:
        st.session_state.genero = gen_var


def click_fowd():
    index = st.session_state.box[0]
    if index == len(tuple_list) - 1:
        st.session_state.box = tuple_list[0]
    else:
        st.session_state.box = tuple_list[index + 1]
    if len(gen_var) < 4:
        st.session_state.genero = gen_var


def change_vista():
    global selec
    films_2 = pd.read_parquet('films.parquet')
    if films_2.loc[selec_film.old_index.values[0], 'Vista'] != st.session_state.vista:
        films_2.loc[selec_film.old_index.values[0],
                    'Vista'] = st.session_state.vista
        films_2.to_parquet('films.parquet', engine='pyarrow')
        st.session_state.toggle_vista = False


# Configuración página
st.set_page_config(layout='wide')

# Cargamos df
films = pd.read_parquet('films.parquet').sort_index(
    ascending=False).reset_index(names='old_index')
films['Titulo_unidecode'] = films.Titulo.apply(lambda x: unidecode(x))
films['Director_unidecode'] = films.Director.apply(
    lambda x: [unidecode(i).lower() for i in x])
actors = pd.read_parquet('actors.parquet')
actors['Nombre_unicode'] = actors.Nombre.apply(lambda x: unidecode(x))

# SIDEBAR

# Excepciones valores filtros
# Excepción text_input
try:
    text_search = st.session_state.search

except:
    text_search = ''

try:
    selec_search = st.session_state.search_select
except:
    selec_search = 'Titulo'

# Excepción Genero

try:
    gen_var = st.session_state.genero
    if gen_var == []:
        gen_var = films.Genero.explode().sort_values().unique()

except:
    gen_var = films.Genero.explode().sort_values().unique()

# Excepción nota
try:
    nota_min, nota_max = st.session_state.nota

except:
    nota_min = 0
    nota_max = 10

# Excepción duracion
try:
    time_min, time_max = st.session_state.slider_time

except:
    time_min = films.Duracion.min()
    time_max = films.Duracion.max()


# Excepción año
try:
    year_min, year_max = st.session_state.slider

except:
    year_min = films.Year.min()
    year_max = films.Year.max()

# Excepción toogle
try:
    toog = st.session_state.toggle_vista

except:
    toog = False

# Excepción sort
try:
    check_sort = st.session_state.sort

except:
    check_sort = False

# Dataset aplicado filtros

if toog:
    films = films[films['Vista'] == False].reset_index(drop=True)

if text_search == '':
    df_selec = films[(films['Year'] <= year_max) &
                     (films['Year'] >= year_min) &
                     (films['Duracion'] >= time_min) &
                     (films['Duracion'] <= time_max) &
                     (films['Genero'].apply(lambda x: any(item in gen_var for item in x))) &
                     (films['TMDB_rate'] >= nota_min) &
                     (films['TMDB_rate'] <= nota_max)].reset_index(drop=True)

else:
    if selec_search == 'Titulo':

        df_selec = films[(films['Titulo_unidecode'].str.lower().str.contains(text_search.lower())) &
                         (films['Year'] <= year_max) &
                         (films['Year'] >= year_min) &
                         (films['Duracion'] >= time_min) &
                         (films['Duracion'] <= time_max) &
                         (films['Genero'].apply(lambda x: any(item in gen_var for item in x))) &
                         (films['TMDB_rate'] >= nota_min) &
                         (films['TMDB_rate'] <= nota_max)].reset_index(drop=True)

    elif selec_search == 'Reparto':

        id_actor = actors[actors.Nombre_unicode.str.lower(
        ).str.contains(text_search.lower())]['Id'].to_list()

        df_selec = films[(films['Reparto'].apply(lambda x: any(item in id_actor for item in x))) &
                         (films['Year'] <= year_max) &
                         (films['Year'] >= year_min) &
                         (films['Duracion'] >= time_min) &
                         (films['Duracion'] <= time_max) &
                         (films['Genero'].apply(lambda x: any(item in gen_var for item in x))) &
                         (films['TMDB_rate'] >= nota_min) &
                         (films['TMDB_rate'] <= nota_max)].reset_index(drop=True)

    elif selec_search == 'Director':

        df_selec = films[(films['Director_unidecode'].apply(lambda x: any(text_search.lower() in i for i in x))) &
                         (films['Year'] <= year_max) &
                         (films['Year'] >= year_min) &
                         (films['Duracion'] >= time_min) &
                         (films['Duracion'] <= time_max) &
                         (films['Genero'].apply(lambda x: any(item in gen_var for item in x))) &
                         (films['TMDB_rate'] >= nota_min) &
                         (films['TMDB_rate'] <= nota_max)].reset_index(drop=True)


# Excepción por si df_selec está vacío
if df_selec.empty:
    df_selec = films
    st.sidebar.write('Sin resultados en la búsqueda')

if check_sort:
    df_selec = df_selec.sort_values('Titulo').reset_index(drop=True)

tuple_list = [(i.Index, i.Titulo) for i in df_selec.itertuples()]
selec = st.sidebar.selectbox(
    'Título', options=tuple_list, key='box')


# Definimos selección
selec_film = df_selec.loc[st.session_state.box[0]]
st.write(len(tuple_list) - 1)
st.session_state.box[0]
selec_film
df_selec
# Sidebar: botones Next / Foward
sd_col1, sd_col2, sd_col3 = st.sidebar.columns([0.25, 0.25, 0.5])

with sd_col1:
    back = st.button(label=':arrow_backward:', on_click=click_back)

with sd_col2:
    fowd = st.button(label=':arrow_forward:', on_click=click_fowd)

with sd_col3:
    sort = st.toggle('Ordenar A-Z', key='sort')

check_vista = st.sidebar.checkbox('Vista', key='vista',
                                  on_change=change_vista,
                                  value=selec_film.Vista)

st.sidebar.image(selec_film.Poster, width=250)

# Filtros

# Géneros
selec_gen = st.sidebar.multiselect('Género', options=films.Genero.explode().sort_values().unique(),
                                   key='genero')

# Búsqueda
search = st.sidebar.text_input('Búsqueda', key='search')
search_select = st.sidebar.radio(label='Opción', horizontal=True, options=[
                                 'Titulo', 'Reparto', 'Director'],
                                 key='search_select')

with st.sidebar.expander('Mas filtros', expanded=True):

    # Filtro Vista/No vista
    toggle_vista = st.toggle('No vistas', key='toggle_vista')

    # Filtro nota
    nota = st.slider(label='Valoración', min_value=0,
                     max_value=10, key='nota',
                     value=[0, 10])

    # Filtro año
    slider_year = st.slider(label='Año', min_value=films.Year.min(),
                            max_value=films.Year.max(), key='slider',
                            value=[films.Year.min(), films.Year.max()])

    # Filtro Duración
    slider_time = st.slider(label='Duración', min_value=films.Duracion.min(),
                            max_value=films.Duracion.max(), key='slider_time',
                            value=[films.Duracion.min(), films.Duracion.max()])

    # Index
    st.markdown(f'Index: {selec_film.old_index}')


# PAGINA PRINCIPAL

# Titulo + Rate + Vista

col_01, col_02 = st.columns([0.4, 0.2])

with col_01:
    st.markdown(
        f"""
    <h1 style='font-size: 70px; color: #b82c16;'>{st.session_state.box[1]}</h1>
    """,
        unsafe_allow_html=True)
    st.write(selec_film.Tag_Line)

with col_02:
    st.write("TMDB rate:")
    st.markdown(f"""
        <h3 style='font-size: 50px; color: #e2e2a7;'>{selec_film.TMDB_rate}</h3>
        """, unsafe_allow_html=True)

# Director, Año, Duración, Imdb
col_11, col_12, col_13, col_14 = st.columns(4)

with col_11:
    for director in selec_film.Director:

        st.markdown(f"""
        <h2 style='font-size: 20px;'>{director}</h2>
        """,
                    unsafe_allow_html=True)

with col_12:
    st.markdown(f"""
        <h2 style='font-size: 20px;'>{selec_film.Year}</h2>
        """,
                unsafe_allow_html=True)

with col_13:
    st.markdown(f"""
        <h2 style='font-size: 20px;'>{selec_film.Duracion} minutos</h2>
        """,
                unsafe_allow_html=True)

with col_14:
    st.markdown(f"""
        <a href=https://www.imdb.com/title/{selec_film.IMDB_id} 
        style='font-size: 25px; color: #e2b616;'>Imdb<a>
        """,
                unsafe_allow_html=True)

st.divider()

col_21, col_22 = st.columns([0.6, 0.4], gap='large')

# Sinopsis
with col_21:
    st.markdown(f"""
        <h3 style='font-size: 20px; color: #f55742;'>Sinopsis</h3>
        """,
                unsafe_allow_html=True)
    st.write(selec_film.Sinopsis)

    col_211, col_212, col_213 = st.columns([0.2, 0.2, 0.6])

    # Generos
    with col_211:

        st.markdown(f"""
            <h3 style='font-size: 20px; color: #f55742;'>Generos</h3>
            """,
                    unsafe_allow_html=True)
        for gen in selec_film.Genero:
            st.write(gen)

    # Paises
    with col_212:
        st.markdown(f"""
            <h3 style='font-size: 20px; color: #f55742;'>Paises</h3>
            """,
                    unsafe_allow_html=True)

        for country in selec_film.Pais:
            st.write(country)

    # Ubicación
    with col_213:
        st.markdown(f"""
            <h3 style='font-size: 20px; color: #f55742;'>Ubicación:</h3>
            """,
                    unsafe_allow_html=True)
        ubi = {'E:\Emule': 'Emule',
               r'F:\\': 'My Passport',
               'G:\Pelis WD Elements': 'Pelis WD Elements'}
        st.write(
            f"{ubi.get(selec_film.Root,'None')}:")
        st.write(
            f"{selec_film.Folder}//{selec_film.File[:60]}...{selec_film.File[-3:]}")

    st.divider()

    # Video
    try:
        st.video(selec_film.Video, 'rb')
    except:
        pass

    col_231, col_232, col_233 = st.columns(3, gap='large')

    with col_231:
        st.markdown(f"""
            <h3 style='font-size: 20px; color: #f55742;'>Productoras</h3>
            """,
                    unsafe_allow_html=True)

        for prod in selec_film.Productoras:
            st.write(prod)

    with col_232:
        st.markdown(f"""
            <h3 style='font-size: 20px; color: #f55742;'>Fecha de Estreno</h3>
            """,
                    unsafe_allow_html=True)
        st.write(selec_film.Fecha_Estreno)

    with col_233:
        st.markdown(f"""
            <h3 style='font-size: 20px; color: #f55742;'>Guion</h3>
            """,
                    unsafe_allow_html=True)

        for writer in selec_film.Guion:
            st.write(writer)

# Titulo Original + Reparto
with col_22:

    st.markdown(f"""
        <h3 style='font-size: 20px; color: #f55742;'>Título Original:</h3>
        """,
                unsafe_allow_html=True)

    st.markdown(f"### **{selec_film.Titulo_Original}**")

    st.divider()

    st.markdown(f"""
        <h3 style='font-size: 20px; color: #f55742;'>Reparto:</h3>
        """,
                unsafe_allow_html=True)

    for act in selec_film.Reparto:
        try:
            st.image(actors[actors.Id == act].Foto.values[0], width=50)
        except:
            pass
        st.markdown(f"""
        <h3 style='font-size: 20px;'>{actors[actors.Id == act].Nombre.values[0]}</h3>
    """,
                    unsafe_allow_html=True)
