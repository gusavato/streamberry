import streamlit as st
import pandas as pd


def click_back():
    global index_selec
    index = films[films.Titulo == selec].index.to_list()[0]
    index_selec = index - 1
    st.write(index_selec)


def click_fowd():
    global index_selec
    index = films[films.Titulo == selec].index.to_list()[0]
    index_selec = index + 1
    st.write(index_selec)


films = pd.read_parquet('films.parquet')

if 'index_selec' not in locals():
    index_selec = 0

st_col1, st_col2 = st.sidebar.columns(2)

with st_col1:
    back = st.button(label=':arrow_backward:', on_click=click_back)


with st_col2:
    fowd = st.button(label=':arrow_forward:', on_click=click_fowd)


selec = st.sidebar.selectbox(
    'Título', options=films['Titulo'], index=index_selec)

st.write(index_selec)
