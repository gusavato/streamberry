import streamlit as st
import pandas as pd


def click_back():
    global films
    index = films[films['Titulo'] == selec].index.to_list()[0]
    if index == 0:
        index = films.shape[0]
    st.session_state.box = films.loc[index - 1, 'Titulo']


def click_fowd():
    global films
    index = films[films['Titulo'] == selec].index.to_list()[0]
    if index == films.shape[0]-1:
        index = -1
    st.session_state.box = films.loc[index + 1, 'Titulo']


films = pd.read_parquet('films.parquet')

selec = st.sidebar.selectbox(
    'Título', options=films.Titulo, key='box')


st_col1, st_col2 = st.sidebar.columns(2)

with st_col1:
    back = st.button(label=':arrow_backward:', on_click=click_back)

with st_col2:
    fowd = st.button(label=':arrow_forward:', on_click=click_fowd)
