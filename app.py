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
# ==================================================
# 🦅 SPEK AVCISI
# BIST TEKNİK ANALİZ WEB UYGULAMASI
# ==================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# ==================================================
# SAYFA AYARI
# ==================================================

st.set_page_config(
    page_title="Spek Avcısı",
    page_icon="🦅",
    layout="wide"
)


# ==================================================
# ANALİZ FONKSİYONU
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

    return veri.dropna()


def analiz_et(veri):

    kapanis = veri["Close"]
    yuksek = veri["High"]
    dusuk = veri["Low"]
    hacim = veri["Volume"]


    # ----------------------------------------------
    # FİYAT
    # ----------------------------------------------

    son_fiyat = float(
        kapanis.iloc[-1]
    )

    onceki_fiyat = float(
        kapanis.iloc[-2]
    )

    degisim = (
        (
            son_fiyat
            - onceki_fiyat
        )
        /
        onceki_fiyat
    ) * 100


    # ----------------------------------------------
    # MA20 - MA50
    # ----------------------------------------------

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


    # ----------------------------------------------
    # RSI
    # ----------------------------------------------

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


    # ----------------------------------------------
    # MACD
    # ----------------------------------------------

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
        - ema26
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


    # ----------------------------------------------
    # HACİM
    # ----------------------------------------------

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


    # ----------------------------------------------
    # CMF
    # ----------------------------------------------

    aralik = (
        yuksek
        - dusuk
    ).replace(
        0,
        np.nan
    )


    para_carpani = (
        (
            (
                kapanis
                - dusuk
            )
            -
            (
                yuksek
                - kapanis
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
        * hacim
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


    # ----------------------------------------------
    # DESTEK - DİRENÇ
    # ----------------------------------------------

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
        * 0.98
    )


    # ----------------------------------------------
    # SKOR
    # ----------------------------------------------

    skor = 0


    if (
        son_fiyat
        > son_ma20
        and
        son_ma20
        > son_ma50
    ):

        skor += 25

    elif (
        son_fiyat
        > son_ma20
    ):

        skor += 15


    if (
        52
        <= son_rsi
        <= 68
    ):

        skor += 15

    elif (
        45
        <= son_rsi
        < 52
    ):

        skor += 8


    if (
        son_macd
        > son_macd_sinyal
    ):

        skor += 15


    if (
        hacim_orani
        >= 1.5
    ):

        skor += 15

    elif (
        hacim_orani
        >= 1
    ):

        skor += 8


    if (
        son_cmf
        > 0.10
    ):

        skor += 15

    elif (
        son_cmf
        > 0
    ):

        skor += 8


    skor = min(
        skor,
        100
    )


    # ----------------------------------------------
    # SİNYAL
    # ----------------------------------------------

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

        "Fiyat": son_fiyat,

        "Değişim": degisim,

        "RSI": son_rsi,

        "Hacim": hacim_orani,

        "CMF": son_cmf,

        "Destek": destek,

        "Direnç": direnc,

        "Kontrol": kontrol,

        "Skor": skor,

        "Sinyal": sinyal,

        "MA20": ma20,

        "MA50": ma50

    }


# ==================================================
# ANA EKRAN
# ==================================================

st.title(
    "🦅 SPEK AVCISI"
)

st.caption(
    "BIST fiyat, hacim ve teknik görünüm analiz paneli"
)


hisse = st.text_input(
    "BIST hisse kodu",
    value="THYAO"
).strip().upper()


if st.button(
    "🦅 ANALİZ ET",
    use_container_width=True
):

    with st.spinner(
        "Veriler analiz ediliyor..."
    ):

        veri = veri_al(
            hisse
        )


    if veri is None:

        st.error(
            "Hisse bulunamadı. "
            "Örnek: THYAO, ASELS, TUPRS"
        )

    else:

        sonuc = analiz_et(
            veri
        )


        st.success(
            f"{hisse} analizi tamamlandı"
        )


        # ------------------------------------------
        # ÜST KARTLAR
        # ------------------------------------------

        c1, c2, c3, c4 = st.columns(4)


        c1.metric(
            "Son Fiyat",
            f"{sonuc['Fiyat']:.2f} TL",
            f"%{sonuc['Değişim']:.2f}"
        )


        c2.metric(
            "RSI",
            f"{sonuc['RSI']:.1f}"
        )


        c3.metric(
            "Hacim Oranı",
            f"{sonuc['Hacim']:.2f}x"
        )


        c4.metric(
            "Teknik Skor",
            f"{sonuc['Skor']}/100"
        )


        # ------------------------------------------
        # SİNYAL
        # ------------------------------------------

        st.subheader(
            f"🚦 Sinyal: "
            f"{sonuc['Sinyal']}"
        )


        # ------------------------------------------
        # TEKNİK BÖLGELER
        # ------------------------------------------

        st.subheader(
            "🧱 Teknik Bölgeler"
        )


        d1, d2, d3 = st.columns(3)


        d1.metric(
            "Destek",
            f"{sonuc['Destek']:.2f} TL"
        )


        d2.metric(
            "Direnç",
            f"{sonuc['Direnç']:.2f} TL"
        )


        d3.metric(
            "Kontrol Seviyesi",
            f"{sonuc['Kontrol']:.2f} TL"
        )


        # ------------------------------------------
        # EK GÖSTERGELER
        # ------------------------------------------

        st.subheader(
            "📊 Para ve Hacim"
        )


        st.write(
            "CMF:",
            round(
                sonuc["CMF"],
                3
            )
        )


        st.write(
            "Hacim:",
            round(
                sonuc["Hacim"],
                2
            ),
            "kat"
        )


        # ------------------------------------------
        # GRAFİK
        # ------------------------------------------

        st.subheader(
            "📈 Fiyat ve Trend"
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


        # ------------------------------------------
        # AÇIKLAMA
        # ------------------------------------------

        st.info(
            "Bu panel fiyat, hacim ve "
            "teknik göstergelerden olası "
            "güçlenme veya zayıflama "
            "izlerini değerlendirir. "
            "Kesin alım-satım garantisi vermez."
        )
