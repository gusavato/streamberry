import streamlit as st
import pandas as pd

# Funciones botones


def click_back():
    global df_selec
    index = df_selec[df_selec['Titulo'] == selec].index.to_list()[0]
    if index == 0:
        index = df_selec.shape[0]
    st.session_state.box = df_selec.loc[index - 1, 'Titulo']


def click_fowd():
    global df_selec
    index = df_selec[df_selec['Titulo'] == selec].index.to_list()[0]
    if index == df_selec.shape[0]-1:
        index = -1
    st.session_state.box = df_selec.loc[index + 1, 'Titulo']


# Configuración página
st.set_page_config(layout='wide')

# Cargamos df
films = pd.read_parquet('films.parquet').sort_index(ascending=False)
actors = pd.read_parquet('actors.parquet')

# Sidebar

# Excepciones valores filtros
# Excepción año
try:
    year_min, year_max = st.session_state.slider

except:
    year_min = films.Year.min()
    year_max = films.Year.max()

# Dataset aplicado filtros
df_selec = films[(films['Year'] <= year_max) &
                 (films['Year'] >= year_min)].reset_index(drop=True)


selec = st.sidebar.selectbox(
    'Título', options=df_selec.Titulo, key='box')

# Sidebar: botones Next / Foward
sd_col1, sd_col2 = st.sidebar.columns(2)

with sd_col1:
    back = st.button(label=':arrow_backward:', on_click=click_back)

with sd_col2:
    fowd = st.button(label=':arrow_forward:', on_click=click_fowd)

# Definimos selección

selec_film = films[films['Titulo'] == st.session_state.box]

st.sidebar.image(selec_film.Poster.values[0])

# Filtros

# Filtro año
slider_year = st.sidebar.slider(label='Año', min_value=films.Year.min(),
                                max_value=films.Year.max(), key='slider',
                                value=[films.Year.min(), films.Year.max()])


# PAGINA PRINCIPAL

st.markdown(
    f"""
    <h1 style='font-size: 70px; color: #b82c16;'>{st.session_state.box}</h1>
    """,
    unsafe_allow_html=True)

st.write(selec_film.Tag_Line.values[0])

col_1, col_2, col_3 = st.columns(3)
with col_1:
    for director in selec_film.Director.values[0]:

        st.markdown(f"""
        <h2 style='font-size: 20px;'>{director}</h2>
        """,
                    unsafe_allow_html=True)

with col_2:
    st.markdown(f"""
        <h2 style='font-size: 20px;'>{selec_film.Year.values[0]}</h2>
        """,
                unsafe_allow_html=True)

with col_3:
    st.markdown(f"""
        <h2 style='font-size: 20px;'>{selec_film.Duracion.values[0]} minutos</h2>
        """,
                unsafe_allow_html=True)

st.divider()
col_4, col_5 = st.columns(2, gap='large')

with col_4:
    st.markdown(f"""
        <h3 style='font-size: 20px; color: #f55742;'>Sinopsis</h3>
        """,
                unsafe_allow_html=True)
    st.write(selec_film.Sinopsis.values[0])

    col_41, col_42, col_43 = st.columns(3)

    with col_41:

        st.markdown(f"""
            <h3 style='font-size: 20px; color: #f55742;'>Generos</h3>
            """,
                    unsafe_allow_html=True)
        for gen in selec_film.Genero.values[0]:
            st.write(gen)

    with col_42:
        st.markdown(f"""
            <h3 style='font-size: 20px; color: #f55742;'>Paises</h3>
            """,
                    unsafe_allow_html=True)

        for country in selec_film.Pais.values[0]:
            st.write(country)

    with col_43:
        st.markdown(f"""
            <h3 style='font-size: 20px; color: #f55742;'>Productoras</h3>
            """,
                    unsafe_allow_html=True)

        for prod in selec_film.Productoras.values[0]:
            st.write(prod)

    try:
        st.video(selec_film.Video.values[0], 'rb')
    except:
        pass


with col_5:
    col_51, col_52 = st.columns(2)

    with col_51:
        for act in selec_film.Reparto.values[0][::2]:
            try:
                st.image(actors[actors.Id == act].Foto.values[0], width=50)
            except:
                pass
            st.markdown(f"""
            <h3 style='font-size: 20px;'>{actors[actors.Id == act].Nombre.values[0]}</h3>
        """,
                        unsafe_allow_html=True)

    with col_52:
        for act in selec_film.Reparto.values[0][1::2]:
            try:
                st.image(actors[actors.Id == act].Foto.values[0], width=50)
            except:
                pass
            st.markdown(f"""
            <h3 style='font-size: 20px;'>{actors[actors.Id == act].Nombre.values[0]}</h3>
        """,
                        unsafe_allow_html=True)

st.write(selec_film)
st.write(st.session_state.slider)
st.write(slider_year)
