import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import time
from datetime import datetime

# ==================================================
# 🦅 SPEK AVCISI V15
# ==================================================

st.set_page_config(
    page_title="Spek Avcısı V15",
    page_icon="🦅",
    layout="wide"
)

st.title("🦅 SPEK AVCISI V15")
st.caption(
    "BIST teknik güç, hacim, para akışı ve tahta izi takip paneli"
)

# ==================================================
# VERİ AL
# ==================================================

@st.cache_data(ttl=300)
def veri_al(hisse):

    sembol = hisse.strip().upper() + ".IS"

    veri = yf.download(
        sembol,
        period="1y",
        interval="1d",
        progress=False,
        auto_adjust=True
    )

    if veri.empty:
        return None

    if isinstance(veri.columns, pd.MultiIndex):
        veri.columns = veri.columns.get_level_values(0)

    return veri.dropna()


# ==================================================
# ANALİZ MOTORU
# ==================================================

def analiz_et(veri):

    kapanis = veri["Close"]
    yuksek = veri["High"]
    dusuk = veri["Low"]
    hacim = veri["Volume"]

    son_fiyat = float(kapanis.iloc[-1])
    onceki_fiyat = float(kapanis.iloc[-2])

    degisim = (
        (son_fiyat - onceki_fiyat)
        / onceki_fiyat
        * 100
    )

    # ------------------------------------------------
    # HAREKETLİ ORTALAMALAR
    # ------------------------------------------------

    ma20 = kapanis.rolling(20).mean()
    ma50 = kapanis.rolling(50).mean()

    son_ma20 = float(ma20.iloc[-1])
    son_ma50 = float(ma50.iloc[-1])

    # ------------------------------------------------
    # RSI
    # ------------------------------------------------

    fark = kapanis.diff()

    yukselis = fark.clip(lower=0)
    dusus = -fark.clip(upper=0)

    ort_yukselis = yukselis.rolling(14).mean()
    ort_dusus = dusus.rolling(14).mean()

    rs = (
        ort_yukselis
        / ort_dusus.replace(0, np.nan)
    )

    rsi_seri = (
        100
        -
        100 / (1 + rs)
    )

    son_rsi = float(
        rsi_seri.iloc[-1]
    )

    onceki_rsi = float(
        rsi_seri.iloc[-2]
    )

    # ------------------------------------------------
    # MACD
    # ------------------------------------------------

    ema12 = kapanis.ewm(
        span=12,
        adjust=False
    ).mean()

    ema26 = kapanis.ewm(
        span=26,
        adjust=False
    ).mean()

    macd = ema12 - ema26

    macd_sinyal = macd.ewm(
        span=9,
        adjust=False
    ).mean()

    son_macd = float(
        macd.iloc[-1]
    )

    son_macd_sinyal = float(
        macd_sinyal.iloc[-1]
    )

    # ------------------------------------------------
    # HACİM
    # ------------------------------------------------

    son_hacim = float(
        hacim.iloc[-1]
    )

    ort_hacim = float(
        hacim.rolling(20).mean().iloc[-1]
    )

    if ort_hacim > 0:

        hacim_orani = (
            son_hacim
            / ort_hacim
        )

    else:

        hacim_orani = 1

    # ------------------------------------------------
    # CMF PARA AKIŞI
    # ------------------------------------------------

    fiyat_araligi = (
        yuksek - dusuk
    ).replace(
        0,
        np.nan
    )

    para_carpani = (

        (
            (kapanis - dusuk)
            -
            (yuksek - kapanis)
        )

        / fiyat_araligi

    )

    para_carpani = (

        para_carpani

        .replace(
            [np.inf, -np.inf],
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

    onceki_cmf = float(
        cmf.iloc[-2]
    )

    # ------------------------------------------------
    # DESTEK - DİRENÇ
    # ------------------------------------------------

    destek = float(
        dusuk.tail(20).min()
    )

    direnc = float(
        yuksek.tail(20).max()
    )

    # ------------------------------------------------
    # TREND
    # ------------------------------------------------

    if (
        son_fiyat > son_ma20
        and son_ma20 > son_ma50
    ):

        trend_puani = 100

        trend_durumu = (
            "🟢 Güçlü Yükseliş"
        )

    elif son_fiyat > son_ma20:

        trend_puani = 70

        trend_durumu = (
            "🟩 Yükseliş"
        )

    elif son_fiyat > son_ma50:

        trend_puani = 45

        trend_durumu = (
            "🟡 Yatay / Kararsız"
        )

    else:

        trend_puani = 20

        trend_durumu = (
            "🔴 Düşüş"
        )

    # ------------------------------------------------
    # HACİM PUANI
    # ------------------------------------------------

    if hacim_orani >= 2:

        hacim_puani = 100

    elif hacim_orani >= 1.5:

        hacim_puani = 80

    elif hacim_orani >= 1:

        hacim_puani = 55

    else:

        hacim_puani = 25

    # ------------------------------------------------
    # PARA PUANI
    # ------------------------------------------------

    if son_cmf >= 0.20:

        para_puani = 100

    elif son_cmf >= 0.10:

        para_puani = 80

    elif son_cmf > 0:

        para_puani = 60

    elif son_cmf >= -0.10:

        para_puani = 35

    else:

        para_puani = 10

    # ------------------------------------------------
    # MOMENTUM
    # ------------------------------------------------

    momentum_puani = 0

    if (
        52 <= son_rsi <= 68
    ):

        momentum_puani += 60

    elif (
        45 <= son_rsi < 52
    ):

        momentum_puani += 35

    elif son_rsi > 68:

        momentum_puani += 40

    else:

        momentum_puani += 15

    if (
        son_macd
        > son_macd_sinyal
    ):

        momentum_puani += 40

    # ------------------------------------------------
    # KIRILIM
    # ------------------------------------------------

    onceki_direnc = float(

        yuksek
        .iloc[-21:-1]
        .max()

    )

    uzaklik = (

        (
            son_fiyat
            - onceki_direnc
        )

        / onceki_direnc

        * 100

    )

    if son_fiyat > onceki_direnc:

        kirilim_puani = 100

    elif uzaklik >= -2:

        kirilim_puani = 75

    elif uzaklik >= -5:

        kirilim_puani = 45

    else:

        kirilim_puani = 20

    # ------------------------------------------------
    # TOPLAMA PUANI
    # ------------------------------------------------

    toplama_puani = round(

        para_puani * 0.40

        + hacim_puani * 0.25

        + trend_puani * 0.20

        + momentum_puani * 0.15

    )

    # ------------------------------------------------
    # RİSK
    # ------------------------------------------------

    risk_puani = 0

    if son_rsi > 75:

        risk_puani += 35

    if hacim_orani < 0.70:

        risk_puani += 20

    if son_fiyat < son_ma20:

        risk_puani += 25

    if son_cmf < 0:

        risk_puani += 20

    risk_puani = min(
        risk_puani,
        100
    )

    # ------------------------------------------------
    # SPEK PUANI
    # ------------------------------------------------

    spek_puani = round(

        trend_puani * 0.25

        + hacim_puani * 0.20

        + para_puani * 0.25

        + momentum_puani * 0.15

        + kirilim_puani * 0.15

        - risk_puani * 0.10

    )

    spek_puani = max(
        0,
        min(
            spek_puani,
            100
        )
    )

    # ------------------------------------------------
    # ÖNCEKİ GÜN PUANI
    # ------------------------------------------------

    onceki_trend = 70

    if (
        kapanis.iloc[-2]
        > ma20.iloc[-2]
        and ma20.iloc[-2]
        > ma50.iloc[-2]
    ):

        onceki_trend = 100

    elif (
        kapanis.iloc[-2]
        > ma20.iloc[-2]
    ):

        onceki_trend = 70

    elif (
        kapanis.iloc[-2]
        > ma50.iloc[-2]
    ):

        onceki_trend = 45

    else:

        onceki_trend = 20

    onceki_para = 60

    if onceki_cmf >= 0.20:

        onceki_para = 100

    elif onceki_cmf >= 0.10:

        onceki_para = 80

    elif onceki_cmf > 0:

        onceki_para = 60

    elif onceki_cmf >= -0.10:

        onceki_para = 35

    else:

        onceki_para = 10

    onceki_puan = round(

        onceki_trend * 0.45

        + onceki_para * 0.35

        + momentum_puani * 0.20

    )

    puan_degisim = (
        spek_puani
        - onceki_puan
    )

    # ------------------------------------------------
    # SİNYAL
    # ------------------------------------------------

    if (
        spek_puani >= 75
        and risk_puani <= 30
    ):

        sinyal = (
            "🟢 GÜÇLÜ AL"
        )

    elif spek_puani >= 60:

        sinyal = (
            "🟩 AL / İZLE"
        )

    elif spek_puani >= 40:

        sinyal = (
            "🟡 BEKLE"
        )

    else:

        sinyal = (
            "🔴 KAÇIN"
        )

    # ------------------------------------------------
    # PARA YÖNÜ
    # ------------------------------------------------

    if (
        son_cmf > 0.10
        and son_cmf > onceki_cmf
    ):

        para_yonu = (
            "💰 Güçlü para girişi"
        )

    elif son_cmf > 0:

        para_yonu = (
            "🟢 Pozitif para akışı"
        )

    elif son_cmf < -0.10:

        para_yonu = (
            "🔴 Güçlü para çıkışı"
        )

    else:

        para_yonu = (
            "🟡 Para akışı zayıf"
        )

    # ------------------------------------------------
    # TOPLAMA - DAĞITIM
    # ------------------------------------------------

    if (
        son_cmf > 0.10
        and hacim_orani > 1
        and son_fiyat >= son_ma20
    ):

        tahta_durumu = (
            "🧲 Toplama ihtimali"
        )

    elif (
        son_cmf < 0
        and son_fiyat < son_ma20
    ):

        tahta_durumu = (
            "📤 Dağıtım ihtimali"
        )

    else:

        tahta_durumu = (
            "⚖️ Net yön yok"
        )

    # ------------------------------------------------
    # HACİM UYARISI
    # ------------------------------------------------

    if hacim_orani >= 2.5:

        hacim_uyari = (
            "🐋 Çok güçlü olağandışı hacim"
        )

    elif hacim_orani >= 1.5:

        hacim_uyari = (
            "🔥 Belirgin hacim artışı"
        )

    elif hacim_orani < 0.70:

        hacim_uyari = (
            "⚠️ Hacim zayıf"
        )

    else:

        hacim_uyari = (
            "✅ Hacim normal"
        )

    # ------------------------------------------------
    # DAĞITIM RİSKİ
    # ------------------------------------------------

    if (
        degisim > 1
        and son_cmf < 0
    ):

        dagitim_riski = (
            "🚨 Fiyat yükselirken para çıkışı var"
        )

    elif (
        son_rsi > 72
        and hacim_orani < 1
    ):

        dagitim_riski = (
            "⚠️ Yükseliş hacimsiz, dikkat"
        )

    else:

        dagitim_riski = (
            "✅ Belirgin dağıtım riski yok"
        )

    # ------------------------------------------------
    # HEDEFLER
    # ------------------------------------------------

    hedef_1 = direnc

    hedef_2 = (
        direnc
        + (
            direnc
            - destek
        )
    )

    zarar_kes = (
        destek * 0.98
    )

    # ------------------------------------------------
    # ISINMA
    # ------------------------------------------------

    if son_rsi >= 75:

        isinma = (
            "🔥 Aşırı alım: "
            "düzeltme riski yüksek"
        )

    elif son_rsi >= 68:

        isinma = (
            "⚠️ Isınma başladı"
        )

    else:

        isinma = (
            "✅ Aşırı ısınma yok"
        )

    # ------------------------------------------------
    # OTOMATİK YORUM
    # ------------------------------------------------

    yorum_parcalari = []

    if trend_puani >= 70:

        yorum_parcalari.append(
            "Trend pozitif"
        )

    else:

        yorum_parcalari.append(
            "Trend zayıf"
        )

    if para_puani >= 80:

        yorum_parcalari.append(
            "para girişi güçlü"
        )

    elif para_puani <= 35:

        yorum_parcalari.append(
            "para akışı zayıf"
        )

    if hacim_puani >= 80:

        yorum_parcalari.append(
            "hacim dikkat çekiyor"
        )

    if risk_puani >= 50:

        yorum_parcalari.append(
            "risk yükselmiş durumda"
        )

    kisa_yorum = (
        ". ".join(
            yorum_parcalari
        )
        + "."
    )

    # ------------------------------------------------
    # SİNYAL NEDENLERİ
    # ------------------------------------------------

    nedenler = []

    if trend_puani >= 70:

        nedenler.append(
            "Fiyat trend ortalamalarının üzerinde"
        )

    if hacim_puani >= 80:

        nedenler.append(
            "Hacimde belirgin artış var"
        )

    if para_puani >= 80:

        nedenler.append(
            "Para akışı güçlü görünüyor"
        )

    if momentum_puani >= 80:

        nedenler.append(
            "RSI ve MACD destekliyor"
        )

    if kirilim_puani >= 75:

        nedenler.append(
            "Direnç bölgesine yakın veya kırılım var"
        )

    if risk_puani >= 50:

        nedenler.append(
            "Risk göstergeleri yükselmiş durumda"
        )

    if not nedenler:

        nedenler.append(
            "Güçlü teknik uyum oluşmadı"
        )

    # ------------------------------------------------
    # VERİ TARİHİ
    # ------------------------------------------------

    veri_tarihi = str(
        veri.index[-1]
    )[:10]

    return {

        "Fiyat": son_fiyat,

        "Değişim": degisim,

        "RSI": son_rsi,

        "Hacim Oranı": hacim_orani,

        "CMF": son_cmf,

        "Destek": destek,

        "Direnç": direnc,

        "Trend": trend_puani,

        "Trend Durumu": trend_durumu,

        "Hacim Puanı": hacim_puani,

        "Para Puanı": para_puani,

        "Momentum": momentum_puani,

        "Kırılım": kirilim_puani,

        "Toplama": toplama_puani,

        "Risk": risk_puani,

        "Spek Puanı": spek_puani,

        "Puan Değişimi": puan_degisim,

        "Sinyal": sinyal,

        "Para Yönü": para_yonu,

        "Tahta Durumu": tahta_durumu,

        "Hacim Uyarısı": hacim_uyari,

        "Dağıtım Riski": dagitim_riski,

        "Hedef 1": hedef_1,

        "Hedef 2": hedef_2,

        "Zarar Kes": zarar_kes,

        "Isınma": isinma,

        "Kısa Yorum": kisa_yorum,

        "Nedenler": nedenler,

        "Veri Tarihi": veri_tarihi,

        "MA20": ma20,

        "MA50": ma50

    }


# ==================================================
# ANA EKRAN
# ==================================================

sekme1, sekme2, sekme3 = st.tabs([

    "🔎 Tek Hisse",

    "📡 BIST Tarayıcı",

    "⭐ Favoriler"

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

        "🦅 DETAYLI ANALİZ ET",

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
                "Hisse bulunamadı."
            )

        else:

            sonuc = analiz_et(
                veri
            )


            st.success(

                f"{hisse} analizi tamamlandı"

            )


            st.caption(

                f"Son veri tarihi: "
                f"{sonuc['Veri Tarihi']}"

            )


            c1, c2, c3, c4 = (
                st.columns(4)
            )


            c1.metric(

                "Son Fiyat",

                f"{sonuc['Fiyat']:.2f} TL",

                f"%{sonuc['Değişim']:.2f}"

            )


            c2.metric(

                "Spek İz Puanı",

                f"{sonuc['Spek Puanı']}/100",

                f"{sonuc['Puan Değişimi']:+.0f}"

            )


            c3.metric(

                "Toplama",

                f"{sonuc['Toplama']}/100"

            )


            c4.metric(

                "Risk",

                f"{sonuc['Risk']}/100"

            )


            st.subheader(

                f"🚦 {sonuc['Sinyal']}"

            )


            st.subheader(

                "🧠 Otomatik Yorum"

            )


            st.write(

                sonuc["Kısa Yorum"]

            )


            st.subheader(

                "🐋 Tahta İzi"

            )


            a1, a2, a3 = (
                st.columns(3)
            )


            a1.write(

                sonuc["Para Yönü"]

            )


            a2.write(

                sonuc["Tahta Durumu"]

            )


            a3.write(

                sonuc["Hacim Uyarısı"]

            )


            st.write(

                sonuc["Dağıtım Riski"]

            )


            st.subheader(

                "🧠 Sinyal Nedenleri"

            )


            for neden in sonuc[
                "Nedenler"
            ]:

                st.write(
                    "• " + neden
                )


            st.subheader(

                "📊 Güç Haritası"

            )


            p1, p2, p3, p4, p5 = (
                st.columns(5)
            )


            p1.metric(

                "Trend",

                sonuc["Trend"]

            )


            p2.metric(

                "Hacim",

                sonuc["Hacim Puanı"]

            )


            p3.metric(

                "Para Girişi",

                sonuc["Para Puanı"]

            )


            p4.metric(

                "Momentum",

                sonuc["Momentum"]

            )


            p5.metric(

                "Kırılım",

                sonuc["Kırılım"]

            )


            st.subheader(

                "🧭 Trend ve İşlem Bölgeleri"

            )


            t1, t2, t3 = (
                st.columns(3)
            )


            t1.metric(

                "Trend",

                sonuc["Trend Durumu"]

            )


            t2.metric(

                "Hedef 1",

                f"{sonuc['Hedef 1']:.2f} TL"

            )


            t3.metric(

                "Hedef 2",

                f"{sonuc['Hedef 2']:.2f} TL"

            )


            r1, r2 = (
                st.columns(2)
            )


            r1.metric(

                "🛡️ Teknik Zarar Kes",

                f"{sonuc['Zarar Kes']:.2f} TL"

            )


            r2.write(

                sonuc["Isınma"]

            )


            st.subheader(

                "🧱 Destek ve Direnç"

            )


            d1, d2 = (
                st.columns(2)
            )


            d1.metric(

                "Destek",

                f"{sonuc['Destek']:.2f} TL"

            )


            d2.metric(

                "Direnç",

                f"{sonuc['Direnç']:.2f} TL"

            )


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


# ==================================================
# BIST TARAMA
# ==================================================

with sekme2:

    st.subheader(

        "📡 BIST Akıllı Tarama"

    )


    hisseler = [

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

        "🦅 AKILLI TARAMAYI BAŞLAT",

        use_container_width=True

    ):


        ilerleme = st.progress(0)

        sonuclar = []


        for i, hisse_kodu in enumerate(

            hisseler

        ):


            try:


                veri = veri_al(

                    hisse_kodu

                )


                if veri is not None:


                    sonuc = analiz_et(

                        veri

                    )


                    sonuclar.append({


                        "Hisse":
                        hisse_kodu,


                        "Fiyat":
                        round(

                            sonuc["Fiyat"],

                            2

                        ),


                        "Spek Puanı":
                        sonuc[
                            "Spek Puanı"
                        ],


                        "Değişim":
                        round(

                            sonuc[
                                "Puan Değişimi"
                            ],

                            1

                        ),


                        "Toplama":
                        sonuc[
                            "Toplama"
                        ],


                        "Risk":
                        sonuc[
                            "Risk"
                        ],


                        "Tahta":
                        sonuc[
                            "Tahta Durumu"
                        ],


                        "Sinyal":
                        sonuc[
                            "Sinyal"
                        ]

                    })


            except Exception:

                pass


            ilerleme.progress(

                int(

                    (
                        i + 1
                    )

                    /

                    len(hisseler)

                    *

                    100

                )

            )


            time.sleep(0.1)


        if sonuclar:


            tablo = pd.DataFrame(

                sonuclar

            )


            tablo = tablo.sort_values(

                "Spek Puanı",

                ascending=False

            )


            st.success(

                "Tarama tamamlandı"

            )


            st.subheader(

                "🔔 Güçlü Sinyaller"

            )


            guclu = tablo[

                tablo[
                    "Spek Puanı"
                ] >= 60

            ]


            if not guclu.empty:


                st.dataframe(

                    guclu,

                    use_container_width=True

                )


            else:


                st.info(

                    "Şu an güçlü sinyal yok."

                )


            st.subheader(

                "🏆 En Güçlü 5 Hisse"

            )


            st.dataframe(

                tablo.head(5),

                use_container_width=True

            )


            st.subheader(

                "📋 Tüm Sonuçlar"

            )


            st.dataframe(

                tablo,

                use_container_width=True

            )


        else:


            st.error(

                "Veri alınamadı."

            )


# ==================================================
# FAVORİLER
# ==================================================

with sekme3:

    st.subheader(

        "⭐ Favori Hisseler"

    )


    favoriler = [

        "THYAO",

        "ASELS",

        "TUPRS",

        "EREGL",

        "KCHOL"

    ]


    st.write(

        "Takip listesi: "

        + ", ".join(

            favoriler

        )

    )


    if st.button(

        "⭐ FAVORİLERİ TARA",

        use_container_width=True

    ):


        favori_sonuclari = []


        ilerleme2 = st.progress(0)


        for i, hisse_kodu in enumerate(

            favoriler

        ):


            try:


                veri = veri_al(

                    hisse_kodu

                )


                if veri is not None:


                    sonuc = analiz_et(

                        veri

                    )


                    favori_sonuclari.append({


                        "Hisse":
                        hisse_kodu,


                        "Fiyat":
                        round(

                            sonuc[
                                "Fiyat"
                            ],

                            2

                        ),


                        "Spek":
                        sonuc[
                            "Spek Puanı"
                        ],


                        "Puan Δ":
                        round(

                            sonuc[
                                "Puan Değişimi"
                            ],

                            1

                        ),


                        "Tahta":
                        sonuc[
                            "Tahta Durumu"
                        ],


                        "Sinyal":
                        sonuc[
                            "Sinyal"
                        ]

                    })


            except Exception:

                pass


            ilerleme2.progress(

                int(

                    (
                        i + 1
                    )

                    /

                    len(favoriler)

                    *

                    100

                )

            )


        if favori_sonuclari:


            favori_tablosu = (

                pd.DataFrame(

                    favori_sonuclari

                )

                .sort_values(

                    "Spek",

                    ascending=False

                )

            )


            st.dataframe(

                favori_tablosu,

                use_container_width=True

            )


# ==================================================
# UYARI
# ==================================================

st.info(

    "Spek Avcısı V15; fiyat, hacim, "
    "trend ve para akışı verilerinden "
    "teknik olasılık üretir. "
    "Gerçek emir defteri, kurum takası "
    "veya spekülatör kimliği göstermez. "
    "Kesin alım-satım garantisi vermez."

)
