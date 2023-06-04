import streamlit as st
st.set_page_config(page_title="Immobilienbewertung", page_icon="logo-thiasos.png")
from PIL import Image

st.header("Thiasos")
st.subheader("Bewertung von Immobilien aus Zwangsversteigerungen")

image = Image.open('logo-thiasos.png')
st.image(image, width = 120, caption='Logo-Thiasos')