# ==================================================
# 🦅 SPEK AVCISI V12
# TEK HİSSE + BIST TARAMA PANELİ
# ==================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import time


# ==================================================
# SAYFA
# ==================================================

st.set_page_config(
    page_title="Spek Avcısı",
    page_icon="🦅",
    layout="wide"
)


# ==================================================
# VERİ AL
# ==================================================

@st.cache_data(
    ttl=300
)

def veri_al(hisse):

    sembol = (
        hisse
        + ".IS"
    )

    veri = yf.download(
        sembol,
        period="1y",
        interval="1d",
        progress=False,
        auto_adjust=True
    )

    if veri.empty:

        return None


    if isinstance(
        veri.columns,
        pd.MultiIndex
    ):

        veri.columns = (
            veri.columns
            .get_level_values(0)
        )


    return (
        veri
        .dropna()
    )


# ==================================================
# ANALİZ
# ==================================================

def analiz_et(veri):

    kapanis = veri["Close"]

    yuksek = veri["High"]

    dusuk = veri["Low"]

    hacim = veri["Volume"]


    # Fiyat

    son_fiyat = float(
        kapanis.iloc[-1]
    )

    onceki_fiyat = float(
        kapanis.iloc[-2]
    )

    degisim = (
        (
            son_fiyat
            -
            onceki_fiyat
        )
        /
        onceki_fiyat
    ) * 100


    # MA

    ma20 = (
        kapanis
        .rolling(20)
        .mean()
    )

    ma50 = (
        kapanis
        .rolling(50)
        .mean()
    )


    son_ma20 = float(
        ma20.iloc[-1]
    )

    son_ma50 = float(
        ma50.iloc[-1]
    )


    # RSI

    fark = (
        kapanis
        .diff()
    )

    yukselis = (
        fark
        .clip(
            lower=0
        )
    )

    dusus = (
        -fark
        .clip(
            upper=0
        )
    )


    ort_yukselis = (
        yukselis
        .rolling(14)
        .mean()
    )

    ort_dusus = (
        dusus
        .rolling(14)
        .mean()
        .replace(
            0,
            0.000001
        )
    )


    rs = (
        ort_yukselis
        /
        ort_dusus
    )


    rsi = (
        100
        -
        (
            100
            /
            (1 + rs)
        )
    )


    son_rsi = float(
        rsi.iloc[-1]
    )


    # MACD

    ema12 = (
        kapanis
        .ewm(
            span=12,
            adjust=False
        )
        .mean()
    )

    ema26 = (
        kapanis
        .ewm(
            span=26,
            adjust=False
        )
        .mean()
    )


    macd = (
        ema12
        -
        ema26
    )


    macd_sinyal = (
        macd
        .ewm(
            span=9,
            adjust=False
        )
        .mean()
    )


    son_macd = float(
        macd.iloc[-1]
    )

    son_macd_sinyal = float(
        macd_sinyal.iloc[-1]
    )


    # Hacim

    son_hacim = float(
        hacim.iloc[-1]
    )

    ort_hacim = float(
        hacim
        .rolling(20)
        .mean()
        .iloc[-1]
    )


    hacim_orani = (
        son_hacim
        /
        ort_hacim
    )


    # CMF

    aralik = (
        yuksek
        -
        dusuk
    ).replace(
        0,
        np.nan
    )


    para_carpani = (
        (
            (
                kapanis
                -
                dusuk
            )
            -
            (
                yuksek
                -
                kapanis
            )
        )
        /
        aralik
    )


    para_carpani = (
        para_carpani
        .replace(
            [
                np.inf,
                -np.inf
            ],
            0
        )
        .fillna(0)
    )


    para_hacmi = (
        para_carpani
        *
        hacim
    )


    cmf = (
        para_hacmi
        .rolling(20)
        .sum()
        /
        hacim
        .rolling(20)
        .sum()
    )


    son_cmf = float(
        cmf.iloc[-1]
    )


    # Destek - direnç

    destek = float(
        dusuk
        .tail(20)
        .min()
    )

    direnc = float(
        yuksek
        .tail(20)
        .max()
    )


    kontrol = (
        destek
        *
        0.98
    )


    # Skor

    skor = 0


    if (
        son_fiyat
        >
        son_ma20
        and
        son_ma20
        >
        son_ma50
    ):

        skor += 25


    elif (
        son_fiyat
        >
        son_ma20
    ):

        skor += 15


    if (
        52
        <=
        son_rsi
        <=
        68
    ):

        skor += 15


    elif (
        45
        <=
        son_rsi
        <
        52
    ):

        skor += 8


    if (
        son_macd
        >
        son_macd_sinyal
    ):

        skor += 15


    if (
        hacim_orani
        >=
        1.5
    ):

        skor += 15


    elif (
        hacim_orani
        >=
        1
    ):

        skor += 8


    if (
        son_cmf
        >
        0.10
    ):

        skor += 15


    elif (
        son_cmf
        >
        0
    ):

        skor += 8


    skor = min(
        skor,
        100
    )


    # Sinyal

    if skor >= 75:

        sinyal = (
            "🟢 GÜÇLÜ AL"
        )


    elif skor >= 60:

        sinyal = (
            "🟩 AL / İZLE"
        )


    elif skor >= 40:

        sinyal = (
            "🟡 BEKLE"
        )


    else:

        sinyal = (
            "🔴 KAÇIN"
        )


    return {

        "Fiyat":
        son_fiyat,

        "Değişim":
        degisim,

        "RSI":
        son_rsi,

        "Hacim":
        hacim_orani,

        "CMF":
        son_cmf,

        "Destek":
        destek,

        "Direnç":
        direnc,

        "Kontrol":
        kontrol,

        "Skor":
        skor,

        "Sinyal":
        sinyal,

        "MA20":
        ma20,

        "MA50":
        ma50

    }


# ==================================================
# BAŞLIK
# ==================================================

st.title(
    "🦅 SPEK AVCISI"
)

st.caption(
    "BIST teknik görünüm ve hacim tarama paneli"
)


# ==================================================
# SEKME
# ==================================================

sekme1, sekme2 = st.tabs([

    "🔎 Tek Hisse",

    "📡 BIST Tarayıcı"

])


# ==================================================
# TEK HİSSE
# ==================================================

with sekme1:

    hisse = st.text_input(

        "Hisse kodu",

        value="THYAO"

    ).strip().upper()


    if st.button(

        "🦅 ANALİZ ET",

        use_container_width=True

    ):


        with st.spinner(

            "Analiz yapılıyor..."

        ):


            veri = veri_al(

                hisse

            )


        if veri is None:


            st.error(

                "Hisse bulunamadı."

            )


        else:


            sonuc = analiz_et(

                veri

            )


            c1, c2, c3, c4 = (

                st.columns(4)

            )


            c1.metric(

                "Fiyat",

                f"{sonuc['Fiyat']:.2f} TL",

                f"%{sonuc['Değişim']:.2f}"

            )


            c2.metric(

                "RSI",

                f"{sonuc['RSI']:.1f}"

            )


            c3.metric(

                "Hacim",

                f"{sonuc['Hacim']:.2f}x"

            )


            c4.metric(

                "Skor",

                f"{sonuc['Skor']}/100"

            )


            st.subheader(

                f"🚦 {sonuc['Sinyal']}"

            )


            d1, d2, d3 = (

                st.columns(3)

            )


            d1.metric(

                "Destek",

                f"{sonuc['Destek']:.2f}"

            )


            d2.metric(

                "Direnç",

                f"{sonuc['Direnç']:.2f}"

            )


            d3.metric(

                "Kontrol",

                f"{sonuc['Kontrol']:.2f}"

            )


            grafik = pd.DataFrame({

                "Kapanış":

                veri["Close"],


                "MA20":

                sonuc["MA20"],


                "MA50":

                sonuc["MA50"]

            })


            st.line_chart(

                grafik.tail(120)

            )


# ==================================================
# BIST TARAMA
# ==================================================

with sekme2:


    st.subheader(

        "📡 BIST Hızlı Tarama"

    )


    st.write(

        "Seçili hisseler "

        "teknik skorlarına göre "

        "sıralanır."

    )


    HISSELER = [

        "THYAO",

        "ASELS",

        "TUPRS",

        "EREGL",

        "KCHOL",

        "SAHOL",

        "AKBNK",

        "GARAN",

        "YKBNK",

        "BIMAS",

        "SISE",

        "FROTO",

        "TOASO",

        "PETKM",

        "SASA"

    ]


    if st.button(

        "📡 HİSSELERİ TARA",

        use_container_width=True

    ):


        ilerleme = (

            st.progress(0)

        )


        sonuclar = []


        for i, hisse in enumerate(

            HISSELER

        ):


            try:


                veri = veri_al(

                    hisse

                )


                if veri is not None:


                    sonuc = analiz_et(

                        veri

                    )


                    sonuclar.append({


                        "Hisse":

                        hisse,


                        "Fiyat":

                        round(

                            sonuc["Fiyat"],

                            2

                        ),


                        "RSI":

                        round(

                            sonuc["RSI"],

                            1

                        ),


                        "Hacim":

                        round(

                            sonuc["Hacim"],

                            2

                        ),


                        "CMF":

                        round(

                            sonuc["CMF"],

                            3

                        ),


                        "Skor":

                        sonuc["Skor"],


                        "Sinyal":

                        sonuc["Sinyal"]

                    })


            except Exception:

                pass


            ilerleme.progress(

                int(

                    (

                        i + 1

                    )

                    /

                    len(HISSELER)

                    *

                    100

                )

            )


            time.sleep(

                0.1

            )


        tablo = (

            pd.DataFrame(

                sonuclar

            )

            .sort_values(

                "Skor",

                ascending=False

            )

        )


        st.success(

            "Tarama tamamlandı"

        )


        st.dataframe(

            tablo,

            use_container_width=True

        )


        st.info(

            "Skor; trend, RSI, "

            "MACD, hacim ve CMF "

            "verilerinin birleşimidir. "

            "Kesin alım-satım "

            "garantisi değildir."

        )
