import streamlit as st

st.set_page_config(
    page_title="Spek Avcısı",
    page_icon="🦅"
)

st.title("🦅 SPEK AVCISI")

st.write(
    "BIST Akıllı Teknik Analiz Paneli"
)

hisse = st.text_input(
    "Hisse kodu",
    value="THYAO"
)

if st.button("ANALİZ ET"):
    st.success(
        hisse.upper()
        + " seçildi."
    )
