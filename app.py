import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import time

# ==================================================
# SAYFA AYARLARI
# ==================================================

st.set_page_config(
    page_title="Spek Avcısı V14",
    page_icon="🦅",
    layout="wide"
)

st.title("🦅 SPEK AVCISI V14")
st.caption(
    "BIST teknik analiz, hacim, para akışı ve sinyal paneli"
)

# ==================================================
# VERİ ALMA
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

    # Hareketli ortalamalar

    ma20 = kapanis.rolling(20).mean()
    ma50 = kapanis.rolling(50).mean()

    son_ma20 = float(ma20.iloc[-1])
    son_ma50 = float(ma50.iloc[-1])

    # RSI

    fark = kapanis.diff()

    yukselis = fark.clip(lower=0)
    dusus = -fark.clip(upper=0)

    ort_yukselis = yukselis.rolling(14).mean()
    ort_dusus = dusus.rolling(14).mean()

    rs = ort_yukselis / ort_dusus.replace(0, np.nan)

    rsi_seri = 100 - (
        100 / (1 + rs)
    )

    son_rsi = float(
        rsi_seri.iloc[-1]
    )

    # MACD

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

    # Hacim

    ort_hacim = float(
        hacim.rolling(20).mean().iloc[-1]
    )

    son_hacim = float(
        hacim.iloc[-1]
    )

    if ort_hacim > 0:
        hacim_orani = (
            son_hacim / ort_hacim
        )
    else:
        hacim_orani = 1

    # Para akışı - CMF

    fiyat_araligi = (
        yuksek - dusuk
    ).replace(0, np.nan)

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
        para_carpani * hacim
    )

    cmf = (
        para_hacmi.rolling(20).sum()
        /
        hacim.rolling(20).sum()
    )

    son_cmf = float(
        cmf.iloc[-1]
    )

    # Destek ve direnç

    destek = float(
        dusuk.tail(20).min()
    )

    direnc = float(
        yuksek.tail(20).max()
    )

    # Trend puanı

    if (
        son_fiyat > son_ma20
        and son_ma20 > son_ma50
    ):
        trend_puani = 100
        trend_durumu = "🟢 Güçlü Yükseliş"

    elif son_fiyat > son_ma20:
        trend_puani = 70
        trend_durumu = "🟩 Yükseliş"

    elif son_fiyat > son_ma50:
        trend_puani = 45
        trend_durumu = "🟡 Yatay / Kararsız"

    else:
        trend_puani = 20
        trend_durumu = "🔴 Düşüş"

    # Hacim puanı

    if hacim_orani >= 2:
        hacim_puani = 100
    elif hacim_orani >= 1.5:
        hacim_puani = 80
    elif hacim_orani >= 1:
        hacim_puani = 55
    else:
        hacim_puani = 25

    # Para girişi puanı

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

    # Momentum puanı

    momentum_puani = 0

    if 52 <= son_rsi <= 68:
        momentum_puani += 60
    elif 45 <= son_rsi < 52:
        momentum_puani += 35
    elif son_rsi > 68:
        momentum_puani += 40
    else:
        momentum_puani += 15

    if son_macd > son_macd_sinyal:
        momentum_puani += 40

    # Kırılım puanı

    onceki_direnc = float(
        yuksek.iloc[-21:-1].max()
    )

    if son_fiyat > onceki_direnc:
        kirilim_puani = 100
    else:
        uzaklik = (
            (son_fiyat - onceki_direnc)
            / onceki_direnc
            * 100
        )

        if uzaklik >= -2:
            kirilim_puani = 75
        elif uzaklik >= -5:
            kirilim_puani = 45
        else:
            kirilim_puani = 20

    # Toplama puanı

    toplama_puani = round(
        para_puani * 0.40
        + hacim_puani * 0.25
        + trend_puani * 0.20
        + momentum_puani * 0.15
    )

    # Risk puanı

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

    # Spek İz puanı

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
        min(spek_puani, 100)
    )

    # Sinyal

    if (
        spek_puani >= 75
        and risk_puani <= 30
    ):
        sinyal = "🟢 GÜÇLÜ AL"
    elif spek_puani >= 60:
        sinyal = "🟩 AL / İZLE"
    elif spek_puani >= 40:
        sinyal = "🟡 BEKLE"
    else:
        sinyal = "🔴 KAÇIN"

    # Hedef ve zarar kes

    hedef_1 = direnc

    hedef_2 = (
        direnc
        + (direnc - destek)
    )

    zarar_kes = (
        destek * 0.98
    )

    # Isınma uyarısı

    if son_rsi >= 75:
        isinma = (
            "🔥 Aşırı alım: "
            "düzeltme riski yüksek"
        )
    elif son_rsi >= 68:
        isinma = (
            "⚠️ Isınma başladı: "
            "kâr satışı riski izlenmeli"
        )
    else:
        isinma = (
            "✅ Aşırı ısınma görünmüyor"
        )

    # Sinyal nedenleri

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
            "RSI ve MACD momentum destekliyor"
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
        "Sinyal": sinyal,
        "Hedef 1": hedef_1,
        "Hedef 2": hedef_2,
        "Zarar Kes": zarar_kes,
        "Isınma": isinma,
        "Nedenler": nedenler,
        "MA20": ma20,
        "MA50": ma50
    }

# ==================================================
# ANA EKRAN
# ==================================================

sekme1, sekme2 = st.tabs([
    "🔎 Tek Hisse Analizi",
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
        "🦅 DETAYLI ANALİZ ET",
        use_container_width=True
    ):

        with st.spinner(
            "Veriler analiz ediliyor..."
        ):
            veri = veri_al(hisse)

        if veri is None:
            st.error(
                "Hisse bulunamadı."
            )
        else:

            sonuc = analiz_et(veri)

            st.success(
                f"{hisse} analizi tamamlandı"
            )

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "Son Fiyat",
                f"{sonuc['Fiyat']:.2f} TL",
                f"%{sonuc['Değişim']:.2f}"
            )

            c2.metric(
                "Spek İz Puanı",
                f"{sonuc['Spek Puanı']}/100"
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
                "🧠 Sinyal Nedenleri"
            )

            for neden in sonuc["Nedenler"]:
                st.write(
                    "• " + neden
                )

            st.subheader(
                "📊 Güç Haritası"
            )

            p1, p2, p3, p4, p5 = st.columns(5)

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

            t1, t2, t3 = st.columns(3)

            t1.metric(
                "Trend Durumu",
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

            r1, r2 = st.columns(2)

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

            d1, d2 = st.columns(2)

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
                "Kapanış": veri["Close"],
                "MA20": sonuc["MA20"],
                "MA50": sonuc["MA50"]
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
                        "Hisse": hisse_kodu,
                        "Fiyat": round(
                            sonuc["Fiyat"],
                            2
                        ),
                        "Spek Puanı": sonuc[
                            "Spek Puanı"
                        ],
                        "Toplama": sonuc[
                            "Toplama"
                        ],
                        "Risk": sonuc[
                            "Risk"
                        ],
                        "Trend": sonuc[
                            "Trend"
                        ],
                        "Hacim": sonuc[
                            "Hacim Puanı"
                        ],
                        "Para": sonuc[
                            "Para Puanı"
                        ],
                        "Sinyal": sonuc[
                            "Sinyal"
                        ]
                    })

            except Exception:
                pass

            ilerleme.progress(
                int(
                    (i + 1)
                    / len(hisseler)
                    * 100
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
# UYARI
# ==================================================

st.info(
    "Bu panel teknik göstergelerden "
    "üretilen olasılık puanlarını gösterir. "
    "Kesin alım-satım garantisi vermez."
)
