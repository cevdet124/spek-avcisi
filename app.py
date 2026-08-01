import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import time

# ==================================================
# SPEK AVCISI V17
# GELİŞMİŞ BIST RADARI
# ==================================================

st.set_page_config(
    page_title="Spek Avcısı V17",
    page_icon="🦅",
    layout="wide"
)

st.title("🦅 SPEK AVCISI V17")
st.caption(
    "Geniş BIST tarama | Akıllı risk filtresi | "
    "Hacim devamlılığı | Haftalık trend | "
    "Yeni güçlenen hisseler"
)

# ==================================================
# BIST HİSSE LİSTESİ
# ==================================================

BIST_HISSELERI = [
    "A1CAP", "ACSEL", "ADEL", "ADESE", "ADGYO",
    "AEFES", "AFYON", "AGESA", "AGHOL", "AGROT",
    "AHGAZ", "AKBNK", "AKCNS", "AKENR", "AKFGY",
    "AKFYE", "AKGRT", "AKMGY", "AKSA", "AKSEN",
    "AKSGY", "AKSUE", "AKYHO", "ALARK", "ALBRK",
    "ALCAR", "ALCTL", "ALFAS", "ALGYO", "ALKA",
    "ALKIM", "ALMAD", "ALTNY", "ANSGR", "ARCLK",
    "ARDYZ", "ARENA", "ARSAN", "ASELS", "ASTOR",
    "ASUZU", "ATAGY", "ATAKP", "ATATP", "AVGYO",
    "AVHOL", "AVOD", "AVPGY", "AYCES", "AYDEM",
    "AYEN", "AYGAZ", "BAGFS", "BAKAB", "BALAT",
    "BASCM", "BAYRK", "BEGYO", "BERA", "BESLR",
    "BFREN", "BIENY", "BIGCH", "BIMAS", "BINHO",
    "BIOEN", "BIZIM", "BJKAS", "BLCYT", "BMSCH",
    "BMSTL", "BNTAS", "BOSSA", "BRISA", "BRKSN",
    "BRLSM", "BRMEN", "BRSAN", "BRYAT", "BSOKE",
    "BTCIM", "BUCIM", "BURCE", "BVSAN", "CANTE",
    "CCOLA", "CELHA", "CEMAS", "CEMTS", "CEOEM",
    "CIMSA", "CLEBI", "CMBTN", "CMENT", "CONSE",
    "CRFSA", "CVKMD", "CWENE", "DAGHL", "DAGI",
    "DAPGM", "DARDL", "DESA", "DESPC", "DEVA",
    "DGATE", "DGNMO", "DOAS", "DOHOL", "DYOBY",
    "EBEBK", "ECILC", "ECZYT", "EDATA", "EDIP",
    "EGEEN", "EGSER", "EKGYO", "EKOS", "EKSUN",
    "ELITE", "EMKEL", "ENERY", "ENJSA", "ENKAI",
    "EREGL", "ESCOM", "ESEN", "EUPWR", "EUREN",
    "FENER", "FONET", "FORTE", "FROTO", "GARAN",
    "GEDIK", "GESAN", "GLYHO", "GOKNR", "GOODY",
    "GOZDE", "GRSEL", "GSDHO", "GSRAY", "GUBRF",
    "GWIND", "HALKB", "HATSN", "HEDEF", "HEKTS",
    "HKTM", "HLGYO", "HOROZ", "HRKET", "HTTBT",
    "HUBVC", "ICBCT", "IDGYO", "IEYHO", "IHAAS",
    "IHLAS", "IHLGM", "IMASM", "INDES", "INFO",
    "INVEO", "INVES", "IPEKE", "ISCTR", "ISDMR",
    "ISFIN", "ISGYO", "ISMEN", "ISSEN", "IZENR",
    "IZMDC", "JANTS", "KAREL", "KARSN", "KATMR",
    "KAYSE", "KBORU", "KCAER", "KCHOL", "KERVT",
    "KFEIN", "KIMMR", "KLGYO", "KLKIM", "KLSER",
    "KMPUR", "KONTR", "KONYA", "KORDS", "KOTON",
    "KOZAA", "KOZAL", "KRDMD", "KRONT", "KRVGD",
    "KUTPO", "KUYAS", "LIDER", "LILAK", "LKMNH",
    "LOGO", "MAVI", "MEDTR", "MEGMT", "MERIT",
    "METRO", "MGROS", "MIATK", "MOBTL", "MPARK",
    "MTRKS", "NATEN", "NETAS", "NTHOL", "NUHCM",
    "ODAS", "ODINE", "OFSYM", "ONCSM", "ORCAY",
    "ORGE", "OTKAR", "OYAKC", "OZGYO", "OZKGY",
    "PASEU", "PATEK", "PCILT", "PEGYO", "PEKGY",
    "PENTA", "PETKM", "PGSUS", "PINSU", "PNLSN",
    "PNSUT", "POLHO", "PRKME", "PSGYO", "RALYH",
    "RAYSG", "REEDR", "RGYAS", "RODRG", "RTALB",
    "RUBNS", "RYGYO", "RYSAS", "SAHOL", "SASA",
    "SAYAS", "SDTTR", "SEKUR", "SELEC", "SELVA",
    "SISE", "SKBNK", "SKTAS", "SMART", "SMRTG",
    "SNGYO", "SOKE", "SOKM", "SRVGY", "SUWEN",
    "TABGD", "TATGD", "TAVHL", "TCELL", "TEKTU",
    "THYAO", "TKFEN", "TKNSA", "TMSN", "TOASO",
    "TRCAS", "TRGYO", "TRILC", "TSKB", "TSPOR",
    "TTKOM", "TTRAK", "TUKAS", "TUPRS", "TUREX",
    "TURSG", "ULKER", "ULUUN", "VAKBN", "VAKFN",
    "VBTYZ", "VERUS", "VESBE", "VESTL", "YATAS",
    "YEOTK", "YIGIT", "YKBNK", "YKSLN", "YUNSA",
    "ZOREN", "UFUK", "AKSUE", "AVHOL", "CRFSA"
]

BIST_HISSELERI = sorted(
    list(set(BIST_HISSELERI))
)

# ==================================================
# YARDIMCI FONKSİYONLAR
# ==================================================

def tek_seviye(veri):

    if isinstance(
        veri.columns,
        pd.MultiIndex
    ):

        veri.columns = (
            veri.columns
            .get_level_values(0)
        )

    return veri


def hesapla_rsi(close):

    fark = close.diff()

    yukari = (
        fark.clip(lower=0)
    )

    asagi = (
        -fark.clip(upper=0)
    )

    ort_yukari = (
        yukari
        .ewm(
            alpha=1 / 14,
            adjust=False
        )
        .mean()
    )

    ort_asagi = (
        asagi
        .ewm(
            alpha=1 / 14,
            adjust=False
        )
        .mean()
    )

    rs = (
        ort_yukari
        /
        ort_asagi.replace(
            0,
            np.nan
        )
    )

    return (
        100
        -
        100 / (1 + rs)
    )


def hesapla_atr(
    high,
    low,
    close
):

    onceki = close.shift(1)

    tr = pd.concat(

        [
            high - low,

            (
                high - onceki
            ).abs(),

            (
                low - onceki
            ).abs()

        ],

        axis=1

    ).max(axis=1)

    return (
        tr
        .rolling(14)
        .mean()
    )


def piyasa_durumu():

    try:

        veri = yf.download(

            "XU100.IS",

            period="1y",

            interval="1d",

            auto_adjust=True,

            progress=False

        )

        veri = tek_seviye(
            veri
        )

        if len(veri) < 60:

            return (
                "🟡 Belirsiz",
                50
            )

        close = veri["Close"]

        ma20 = (
            close
            .rolling(20)
            .mean()
            .iloc[-1]
        )

        ma50 = (
            close
            .rolling(50)
            .mean()
            .iloc[-1]
        )

        fiyat = (
            close.iloc[-1]
        )

        if (
            fiyat > ma20
            and ma20 > ma50
        ):

            return (
                "🟢 BIST Trend Pozitif",
                100
            )

        elif fiyat > ma50:

            return (
                "🟡 BIST Kararsız",
                70
            )

        else:

            return (
                "🔴 BIST Trend Zayıf",
                40
            )

    except Exception:

        return (
            "🟡 Piyasa verisi alınamadı",
            60
        )


# ==================================================
# GELİŞMİŞ HİSSE ANALİZİ
# ==================================================

def hisse_analiz(
    veri,
    piyasa_puani=60
):

    veri = veri.dropna(
        subset=[
            "Close",
            "High",
            "Low",
            "Volume"
        ]
    )

    if len(veri) < 100:

        return None

    close = veri["Close"]
    high = veri["High"]
    low = veri["Low"]
    volume = veri["Volume"]

    fiyat = float(
        close.iloc[-1]
    )

    onceki_fiyat = float(
        close.iloc[-2]
    )

    gunluk_degisim = (

        (
            fiyat
            -
            onceki_fiyat
        )

        /
        onceki_fiyat

        * 100

    )

    ma20 = (
        close
        .rolling(20)
        .mean()
    )

    ma50 = (
        close
        .rolling(50)
        .mean()
    )

    ma100 = (
        close
        .rolling(100)
        .mean()
    )

    son_ma20 = float(
        ma20.iloc[-1]
    )

    son_ma50 = float(
        ma50.iloc[-1]
    )

    son_ma100 = float(
        ma100.iloc[-1]
    )

    rsi = hesapla_rsi(
        close
    )

    son_rsi = float(
        rsi.iloc[-1]
    )

    ort_hacim20 = float(

        volume
        .rolling(20)
        .mean()
        .iloc[-1]

    )

    son_hacim = float(
        volume.iloc[-1]
    )

    hacim_orani = (

        son_hacim
        /
        ort_hacim20

        if ort_hacim20 > 0

        else 0

    )

    son5_hacim = float(

        volume
        .tail(5)
        .mean()

    )

    onceki5_hacim = float(

        volume
        .iloc[-10:-5]
        .mean()

    )

    hacim_devam = (

        son5_hacim
        /
        onceki5_hacim

        if onceki5_hacim > 0

        else 1

    )

    # İşlem değeri

    islem_degeri = (
        fiyat
        *
        son_hacim
    )

    # CMF

    aralik = (
        high - low
    ).replace(
        0,
        np.nan
    )

    para_carpani = (

        (
            (close - low)
            -
            (high - close)
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
        volume
    )

    cmf = (

        para_hacmi
        .rolling(20)
        .sum()

        /

        volume
        .rolling(20)
        .sum()

    )

    son_cmf = float(
        cmf.iloc[-1]
    )

    # ATR

    atr = hesapla_atr(
        high,
        low,
        close
    )

    atr_yuzde = (

        float(
            atr.iloc[-1]
        )

        /
        fiyat

        * 100

    )

    # Haftalık trend

    haftalik = (

        close

        .resample(
            "W-FRI"
        )

        .last()

        .dropna()

    )

    if len(haftalik) >= 20:

        hafta_ma10 = (

            haftalik

            .rolling(10)

            .mean()

            .iloc[-1]

        )

        hafta_ma20 = (

            haftalik

            .rolling(20)

            .mean()

            .iloc[-1]

        )

        if (
            haftalik.iloc[-1]
            >
            hafta_ma10
            and
            hafta_ma10
            >
            hafta_ma20
        ):

            haftalik_trend = (
                "🟢 Uyumlu"
            )

            haftalik_puan = 100

        elif (
            haftalik.iloc[-1]
            >
            hafta_ma20
        ):

            haftalik_trend = (
                "🟡 Kısmen uyumlu"
            )

            haftalik_puan = 65

        else:

            haftalik_trend = (
                "🔴 Uyumsuz"
            )

            haftalik_puan = 25

    else:

        haftalik_trend = (
            "🟡 Veri az"
        )

        haftalik_puan = 50

    # Günlük trend

    if (
        fiyat > son_ma20
        and
        son_ma20 > son_ma50
        and
        son_ma50 > son_ma100
    ):

        trend_puani = 100

        trend_yazi = (
            "🟢 Güçlü yükseliş"
        )

    elif (
        fiyat > son_ma20
        and
        son_ma20 > son_ma50
    ):

        trend_puani = 80

        trend_yazi = (
            "🟢 Yükseliş"
        )

    elif fiyat > son_ma50:

        trend_puani = 55

        trend_yazi = (
            "🟡 Kararsız"
        )

    else:

        trend_puani = 20

        trend_yazi = (
            "🔴 Düşüş"
        )

    # Hacim puanı

    if (
        hacim_orani >= 2
        and
        hacim_devam >= 1.15
    ):

        hacim_puani = 100

    elif hacim_orani >= 1.5:

        hacim_puani = 80

    elif hacim_orani >= 1.1:

        hacim_puani = 60

    else:

        hacim_puani = 25

    # Para akışı

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

    # RSI momentumu

    if 50 <= son_rsi <= 65:

        rsi_puani = 100

    elif 45 <= son_rsi < 50:

        rsi_puani = 65

    elif 65 < son_rsi <= 70:

        rsi_puani = 75

    elif 70 < son_rsi <= 75:

        rsi_puani = 45

    elif son_rsi > 75:

        rsi_puani = 15

    else:

        rsi_puani = 25

    # Dirence yakınlık

    direnç = float(
        high.tail(20).max()
    )

    destek = float(
        low.tail(20).min()
    )

    dirence_uzaklik = (

        (
            direnç
            -
            fiyat
        )

        /
        fiyat

        * 100

    )

    if dirence_uzaklik <= 1:

        kovalama = 100

    elif dirence_uzaklik <= 3:

        kovalama = 70

    elif dirence_uzaklik <= 6:

        kovalama = 35

    else:

        kovalama = 10

    # Likidite riski

    if islem_degeri >= 100_000_000:

        likidite_riski = 0

    elif islem_degeri >= 30_000_000:

        likidite_riski = 15

    elif islem_degeri >= 10_000_000:

        likidite_riski = 35

    else:

        likidite_riski = 65

    # Oynaklık riski

    if atr_yuzde >= 8:

        oynaklik_riski = 80

    elif atr_yuzde >= 5:

        oynaklik_riski = 55

    elif atr_yuzde >= 3:

        oynaklik_riski = 30

    else:

        oynaklik_riski = 10

    # RSI riski

    if son_rsi >= 85:

        rsi_riski = 100

    elif son_rsi >= 75:

        rsi_riski = 70

    elif son_rsi >= 70:

        rsi_riski = 40

    else:

        rsi_riski = 10

    # Trend riski

    trend_riski = (
        100
        -
        trend_puani
    )

    # Toplam risk

    risk = round(

        likidite_riski
        * 0.25

        +

        oynaklik_riski
        * 0.20

        +

        rsi_riski
        * 0.20

        +

        kovalama
        * 0.15

        +

        trend_riski
        * 0.20

    )

    risk = max(
        1,
        min(
            risk,
            100
        )
    )

    # Yeni güçlenme

    eski_rsi = float(
        rsi.iloc[-5]
    )

    rsi_degisim = (
        son_rsi
        -
        eski_rsi
    )

    ma20_5gun_once = float(
        ma20.iloc[-5]
    )

    yeni_guclenme = 0

    if rsi_degisim >= 5:

        yeni_guclenme += 30

    if (
        fiyat > son_ma20
        and
        close.iloc[-5]
        <= ma20_5gun_once
    ):

        yeni_guclenme += 35

    if hacim_devam >= 1.20:

        yeni_guclenme += 20

    if son_cmf > 0:

        yeni_guclenme += 15

    yeni_guclenme = min(
        yeni_guclenme,
        100
    )

    # Erken hareket

    erken_hareket = round(

        hacim_puani
        * 0.30

        +

        yeni_guclenme
        * 0.30

        +

        para_puani
        * 0.20

        +

        rsi_puani
        * 0.20

    )

    # Spek puanı

    spek_puani = round(

        trend_puani
        * 0.20

        +

        hacim_puani
        * 0.17

        +

        para_puani
        * 0.20

        +

        rsi_puani
        * 0.12

        +

        haftalik_puan
        * 0.12

        +

        yeni_guclenme
        * 0.10

        +

        piyasa_puani
        * 0.09

        -

        risk
        * 0.20

    )

    # Aşırı RSI cezası

    if son_rsi >= 85:

        spek_puani -= 25

    elif son_rsi >= 75:

        spek_puani -= 12

    spek_puani = int(

        max(
            0,
            min(
                spek_puani,
                100
            )
        )

    )

    # Güven

    if (
        haftalik_puan >= 80
        and
        hacim_devam >= 1.10
        and
        risk <= 30
    ):

        guven = (
            "🟢 Yüksek"
        )

    elif risk <= 50:

        guven = (
            "🟡 Orta"
        )

    else:

        guven = (
            "🔴 Düşük"
        )

    # Sinyal

    if son_rsi >= 85:

        sinyal = (
            "🔥 AŞIRI ISINMIŞ"
        )

    elif (
        spek_puani >= 75
        and
        risk <= 30
        and
        islem_degeri >= 30_000_000
        and
        haftalik_puan >= 65
    ):

        sinyal = (
            "🟢 GÜÇLÜ AL"
        )

    elif (
        spek_puani >= 60
        and
        risk <= 50
    ):

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

    # Hedefler

    hedef_alt = direnç

    hedef_ust = (

        direnç

        +

        (
            direnç
            -
            destek
        )

        * 0.50

    )

    zarar_kes = (

        max(

            destek * 0.98,

            fiyat
            -
            2
            *
            float(
                atr.iloc[-1]
            )

        )

    )

    return {

        "Fiyat":
        fiyat,

        "Günlük %":
        gunluk_degisim,

        "RSI":
        son_rsi,

        "Hacim Oranı":
        hacim_orani,

        "Hacim Devam":
        hacim_devam,

        "İşlem Değeri":
        islem_degeri,

        "CMF":
        son_cmf,

        "Trend":
        trend_yazi,

        "Haftalık":
        haftalik_trend,

        "Spek":
        spek_puani,

        "Risk":
        risk,

        "Güven":
        guven,

        "Sinyal":
        sinyal,

        "Yeni Güçlenme":
        yeni_guclenme,

        "Erken Hareket":
        erken_hareket,

        "ATR %":
        atr_yuzde,

        "Kovalama":
        kovalama,

        "Destek":
        destek,

        "Direnç":
        direnç,

        "Hedef Alt":
        hedef_alt,

        "Hedef Üst":
        hedef_ust,

        "Zarar Kes":
        zarar_kes

    }


# ==================================================
# PİYASA DURUMU
# ==================================================

piyasa_yazi, piyasa_puani = (
    piyasa_durumu()
)

st.info(
    f"Piyasa filtresi: "
    f"{piyasa_yazi}"
)

# ==================================================
# SEKMELER
# ==================================================

sekme1, sekme2, sekme3 = st.tabs([

    "🔎 Tek Hisse",

    "📡 BIST Tarama",

    "ℹ️ V17 Bilgi"

])


# ==================================================
# TEK HİSSE
# ==================================================

with sekme1:

    hisse = st.text_input(

        "Hisse kodu",

        value="THYAO"

    ).upper().strip()

    if st.button(

        "🦅 GELİŞMİŞ ANALİZ",

        use_container_width=True

    ):

        with st.spinner(

            "Veriler analiz ediliyor..."

        ):

            veri = yf.download(

                hisse + ".IS",

                period="2y",

                interval="1d",

                auto_adjust=True,

                progress=False

            )

        veri = tek_seviye(
            veri
        )

        sonuc = hisse_analiz(

            veri,

            piyasa_puani

        )

        if sonuc is None:

            st.error(
                "Yeterli veri bulunamadı."
            )

        else:

            a, b, c, d = st.columns(4)

            a.metric(

                "Son Fiyat",

                f"{sonuc['Fiyat']:.2f} TL",

                f"%{sonuc['Günlük %']:.2f}"

            )

            b.metric(

                "Spek Puanı",

                f"{sonuc['Spek']}/100"

            )

            c.metric(

                "Risk",

                f"{sonuc['Risk']}/100"

            )

            d.metric(

                "Güven",

                sonuc["Güven"]

            )

            st.subheader(
                sonuc["Sinyal"]
            )

            x, y, z = st.columns(3)

            x.write(
                "Trend: "
                +
                sonuc["Trend"]
            )

            y.write(
                "Haftalık: "
                +
                sonuc["Haftalık"]
            )

            z.write(
                "Yeni güçlenme: "
                +
                str(
                    sonuc[
                        "Yeni Güçlenme"
                    ]
                )
                +
                "/100"
            )

            st.subheader(
                "📊 Gelişmiş Göstergeler"
            )

            tablo = pd.DataFrame({

                "Gösterge": [

                    "RSI",

                    "Hacim Oranı",

                    "Hacim Devamlılığı",

                    "İşlem Değeri",

                    "CMF",

                    "ATR %",

                    "Kovalama Riski",

                    "Erken Hareket"

                ],

                "Değer": [

                    round(
                        sonuc["RSI"],
                        1
                    ),

                    round(
                        sonuc[
                            "Hacim Oranı"
                        ],
                        2
                    ),

                    round(
                        sonuc[
                            "Hacim Devam"
                        ],
                        2
                    ),

                    f"{sonuc['İşlem Değeri']:,.0f} TL",

                    round(
                        sonuc["CMF"],
                        3
                    ),

                    round(
                        sonuc["ATR %"],
                        2
                    ),

                    sonuc[
                        "Kovalama"
                    ],

                    sonuc[
                        "Erken Hareket"
                    ]

                ]

            })

            st.dataframe(

                tablo,

                use_container_width=True,

                hide_index=True

            )

            st.subheader(
                "🎯 Teknik Bölgeler"
            )

            h1, h2, h3 = st.columns(3)

            h1.metric(

                "Destek",

                f"{sonuc['Destek']:.2f} TL"

            )

            h2.metric(

                "Hedef Bölgesi",

                (
                    f"{sonuc['Hedef Alt']:.2f}"
                    " - "
                    f"{sonuc['Hedef Üst']:.2f}"
                    " TL"
                )

            )

            h3.metric(

                "Zarar Kes",

                f"{sonuc['Zarar Kes']:.2f} TL"

            )

            grafik = pd.DataFrame({

                "Kapanış":
                veri["Close"],

                "MA20":
                veri["Close"]
                .rolling(20)
                .mean(),

                "MA50":
                veri["Close"]
                .rolling(50)
                .mean()

            })

            st.line_chart(
                grafik.tail(150)
            )


# ==================================================
# BIST TARAMA
# ==================================================

with sekme2:

    st.subheader(
        "📡 V17 Akıllı BIST Taraması"
    )

    adet = st.selectbox(

        "Tarama kapsamı",

        [

            50,

            100,

            200,

            "TÜM LİSTE"

        ],

        index=0

    )

    if st.button(

        "🦅 AKILLI TARAMAYI BAŞLAT",

        use_container_width=True

    ):

        if adet == "TÜM LİSTE":

            secilen = (
                BIST_HISSELERI
            )

        else:

            secilen = (
                BIST_HISSELERI[
                    :adet
                ]
            )

        ilerleme = st.progress(0)

        durum = st.empty()

        sonuclar = []

        baslangic = time.time()

        toplam = len(
            secilen
        )

        for i, kod in enumerate(
            secilen
        ):

            durum.write(

                f"Analiz: {kod} "

                f"({i + 1}/{toplam})"

            )

            try:

                veri = yf.download(

                    kod + ".IS",

                    period="2y",

                    interval="1d",

                    auto_adjust=True,

                    progress=False

                )

                veri = tek_seviye(
                    veri
                )

                sonuc = hisse_analiz(

                    veri,

                    piyasa_puani

                )

                if sonuc:

                    sonuclar.append({

                        "Hisse":
                        kod,

                        "Fiyat":
                        round(
                            sonuc["Fiyat"],
                            2
                        ),

                        "Spek":
                        sonuc["Spek"],

                        "Sinyal":
                        sonuc["Sinyal"],

                        "Güven":
                        sonuc["Güven"],

                        "Trend":
                        sonuc["Trend"],

                        "Haftalık":
                        sonuc["Haftalık"],

                        "Yeni Güç":
                        sonuc[
                            "Yeni Güçlenme"
                        ],

                        "Erken":
                        sonuc[
                            "Erken Hareket"
                        ],

                        "Risk":
                        sonuc["Risk"],

                        "RSI":
                        round(
                            sonuc["RSI"],
                            1
                        ),

                        "Hacim":
                        round(
                            sonuc[
                                "Hacim Oranı"
                            ],
                            2
                        ),

                        "Hacim Devam":
                        round(
                            sonuc[
                                "Hacim Devam"
                            ],
                            2
                        ),

                        "ATR %":
                        round(
                            sonuc["ATR %"],
                            2
                        ),

                        "Kovalama":
                        sonuc[
                            "Kovalama"
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

                    toplam

                    *

                    100

                )

            )

        durum.empty()

        if sonuclar:

            tablo = pd.DataFrame(
                sonuclar
            )

            tablo = (

                tablo

                .sort_values(

                    [

                        "Spek",

                        "Risk"

                    ],

                    ascending=[

                        False,

                        True

                    ]

                )

                .reset_index(
                    drop=True
                )

            )

            sure = round(

                time.time()

                -

                baslangic,

                1

            )

            st.success(

                f"{len(tablo)} hisse "

                f"analiz edildi. "

                f"Süre: {sure} saniye."

            )

            m1, m2, m3, m4 = (
                st.columns(4)
            )

            m1.metric(

                "Güçlü AL",

                len(

                    tablo[

                        tablo[
                            "Sinyal"
                        ]

                        ==

                        "🟢 GÜÇLÜ AL"

                    ]

                )

            )

            m2.metric(

                "Yeni Güçlenen",

                len(

                    tablo[

                        tablo[
                            "Yeni Güç"
                        ]

                        >= 60

                    ]

                )

            )

            m3.metric(

                "Yüksek Güven",

                len(

                    tablo[

                        tablo[
                            "Güven"
                        ]

                        ==

                        "🟢 Yüksek"

                    ]

                )

            )

            m4.metric(

                "Aşırı Isınmış",

                len(

                    tablo[

                        tablo[
                            "Sinyal"
                        ]

                        ==

                        "🔥 AŞIRI ISINMIŞ"

                    ]

                )

            )

            st.subheader(
                "🏆 En Kaliteli 20"
            )

            st.dataframe(

                tablo.head(20),

                use_container_width=True,

                hide_index=True

            )

            st.subheader(
                "🆕 Yeni Güçlenenler"
            )

            yeni = tablo[

                (

                    tablo[
                        "Yeni Güç"
                    ]
                    >= 60

                )

                &

                (

                    tablo[
                        "Risk"
                    ]
                    <= 45

                )

            ]

            st.dataframe(

                yeni,

                use_container_width=True,

                hide_index=True

            )

            st.subheader(
                "🟢 Güçlü AL"
            )

            guclu = tablo[

                tablo[
                    "Sinyal"
                ]

                ==

                "🟢 GÜÇLÜ AL"

            ]

            st.dataframe(

                guclu,

                use_container_width=True,

                hide_index=True

            )

            st.subheader(
                "🚀 Erken Hareket"
            )

            erken = tablo[

                (

                    tablo[
                        "Erken"
                    ]
                    >= 70

                )

                &

                (

                    tablo[
                        "Risk"
                    ]
                    <= 50

                )

            ]

            st.dataframe(

                erken,

                use_container_width=True,

                hide_index=True

            )

            st.subheader(
                "🔥 Aşırı Isınmış"
            )

            isinmis = tablo[

                tablo[
                    "Sinyal"
                ]

                ==

                "🔥 AŞIRI ISINMIŞ"

            ]

            st.dataframe(

                isinmis,

                use_container_width=True,

                hide_index=True

            )

            st.subheader(
                "🔎 Tüm Sonuçlar"
            )

            arama = st.text_input(
                "Hisse ara"
            ).upper().strip()

            if arama:

                gorunen = tablo[

                    tablo[
                        "Hisse"
                    ]

                    .str.contains(

                        arama,

                        na=False

                    )

                ]

            else:

                gorunen = tablo

            st.dataframe(

                gorunen,

                use_container_width=True,

                hide_index=True

            )

            csv = (

                tablo

                .to_csv(

                    index=False

                )

                .encode(
                    "utf-8-sig"
                )

            )

            st.download_button(

                "📥 V17 SONUÇLARINI İNDİR",

                data=csv,

                file_name=(
                    "spek_avcisi_v17.csv"
                ),

                mime="text/csv",

                use_container_width=True

            )

        else:

            st.error(

                "Tarama sonucunda "

                "yeterli veri bulunamadı."

            )


# ==================================================
# BİLGİ
# ==================================================

with sekme3:

    st.subheader(
        "🧠 V17 Modeli"
    )

    st.write(
        "V17; fiyat, trend, RSI, "
        "hacim, hacim devamlılığı, "
        "para akışı, haftalık trend, "
        "işlem değeri, ATR ve piyasa "
        "trendini birlikte değerlendirir."
    )

    st.warning(
        "Sinyaller teknik olasılık "
        "hesaplarıdır. Gerçek emir defteri, "
        "kurum takası veya belirli kişilerin "
        "işlemlerini doğrudan göstermez."
    )

    st.error(
        "Bu uygulama yatırım tavsiyesi "
        "değildir. Sinyaller kesin kazanç "
        "garantisi vermez."
    )
