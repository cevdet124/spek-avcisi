import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import time

# ==================================================
# SPEK AVCISI V16 - GENİŞ BIST TARAMA
# ==================================================

st.set_page_config(
    page_title="Spek Avcısı V16",
    page_icon="🦅",
    layout="wide"
)

st.title("🦅 SPEK AVCISI V16")
st.caption(
    "Geniş BIST tarama | Trend | Hacim | Para akışı | "
    "Toplama-dağıtım olasılığı"
)

# ==================================================
# GENİŞ HİSSE LİSTESİ
# ==================================================

BIST_HISSELERI = [
    "A1CAP", "ACSEL", "ADEL", "ADESE", "ADGYO",
    "AEFES", "AFYON", "AGESA", "AGHOL", "AGROT",
    "AGYO", "AHGAZ", "AKBNK", "AKCNS", "AKENR",
    "AKFGY", "AKFYE", "AKGRT", "AKMGY", "AKSA",
    "AKSEN", "AKSGY", "AKSUE", "AKYHO", "ALARK",
    "ALBRK", "ALCAR", "ALCTL", "ALFAS", "ALGYO",
    "ALKA", "ALKIM", "ALMAD", "ALTNY", "ANSGR",
    "ARCLK", "ARDYZ", "ARENA", "ARMGD", "ARSAN",
    "ARTMS", "ARZUM", "ASELS", "ASGYO", "ASTOR",
    "ASUZU", "ATAGY", "ATAKP", "ATATP", "AVGYO",
    "AVHOL", "AVOD", "AVPGY", "AYCES", "AYDEM",
    "AYEN", "AYGAZ", "BAGFS", "BAKAB", "BALAT",
    "BASCM", "BAYRK", "BEGYO", "BERA", "BESLR",
    "BETA", "BFREN", "BIENY", "BIGCH", "BIGEN",
    "BIMAS", "BINHO", "BIOEN", "BIZIM", "BJKAS",
    "BLCYT", "BMSCH", "BMSTL", "BNTAS", "BOSSA",
    "BRISA", "BRKSN", "BRLSM", "BRMEN", "BRSAN",
    "BRYAT", "BSOKE", "BTCIM", "BUCIM", "BURCE",
    "BVSAN", "CANTE", "CCOLA", "CELHA", "CEMAS",
    "CEMTS", "CEOEM", "CIMSA", "CLEBI", "CMBTN",
    "CMENT", "CONSE", "COSMO", "CRDFA", "CRFSA",
    "CUSAN", "CVKMD", "CWENE", "DAGHL", "DAGI",
    "DAPGM", "DARDL", "DENGE", "DERHL", "DERIM",
    "DESA", "DESPC", "DEVA", "DGATE", "DGGYO",
    "DGNMO", "DIRIT", "DITAS", "DMRGD", "DMSAS",
    "DNISI", "DOAS", "DOBUR", "DOCO", "DOFER",
    "DOGUB", "DOHOL", "DOKTA", "DURDO", "DYOBY",
    "DZGYO", "EBEBK", "ECILC", "ECZYT", "EDATA",
    "EDIP", "EGEEN", "EGEPO", "EGGUB", "EGPRO",
    "EGSER", "EKGYO", "EKOS", "EKSUN", "ELITE",
    "EMKEL", "EMNIS", "ENDAE", "ENERY", "ENJSA",
    "ENKAI", "EPLAS", "ERBOS", "EREGL", "ERSU",
    "ESCAR", "ESCOM", "ESEN", "ETILR", "ETYAT",
    "EUHOL", "EUKYO", "EUPWR", "EUREN", "EUYO",
    "EYGYO", "FADE", "FENER", "FLAP", "FMIZP",
    "FONET", "FORTE", "FRIGO", "FROTO", "FZLGY",
    "GARAN", "GARFA", "GEDIK", "GEDZA", "GENIL",
    "GENTS", "GEREL", "GESAN", "GIPTA", "GLBMD",
    "GLCVY", "GLRYH", "GLYHO", "GMTAS", "GOKNR",
    "GOLTS", "GOODY", "GOZDE", "GRNYO", "GRSEL",
    "GRTHO", "GSDDE", "GSDHO", "GSRAY", "GUBRF",
    "GWIND", "GZNMI", "HALKB", "HATEK", "HATSN",
    "HEDEF", "HEKTS", "HKTM", "HLGYO", "HOROZ",
    "HRKET", "HTTBT", "HUBVC", "HUNER", "HURGZ",
    "ICBCT", "ICUGS", "IDGYO", "IEYHO", "IHAAS",
    "IHEVA", "IHGZT", "IHLAS", "IHLGM", "IHYAY",
    "IMASM", "INDES", "INFO", "INTEM", "INVEO",
    "INVES", "IPEKE", "ISATR", "ISBTR", "ISCTR",
    "ISDMR", "ISFIN", "ISGYO", "ISGSY", "ISGYO",
    "ISMEN", "ISSEN", "ISYAT", "IZENR", "IZFAS",
    "IZMDC", "JANTS", "KAPLM", "KAREL", "KARSN",
    "KARTN", "KARYE", "KATMR", "KAYSE", "KBORU",
    "KCAER", "KCHOL", "KENT", "KERVT", "KFEIN",
    "KGYO", "KIMMR", "KLGYO", "KLKIM", "KLMSN",
    "KLRHO", "KLSER", "KLSYN", "KMPUR", "KONKA",
    "KONTR", "KONYA", "KORDS", "KOTON", "KOZAA",
    "KOZAL", "KRDMA", "KRDMB", "KRDMD", "KRGYO",
    "KRONT", "KRPLS", "KRSTL", "KRTEK", "KRVGD",
    "KSTUR", "KTLEV", "KTSKR", "KUTPO", "KUYAS",
    "KZBGY", "KZGYO", "LIDER", "LILAK", "LINK",
    "LKMNH", "LMKDC", "LOGO", "LRSHO", "LUKSK",
    "LYDHO", "MAALT", "MAGEN", "MAKIM", "MAKTK",
    "MANAS", "MARBL", "MARKA", "MARTI", "MAVI",
    "MEDTR", "MEGMT", "MEKAG", "MERCN", "MERIT",
    "MERKO", "METRO", "METUR", "MGROS", "MHRGY",
    "MIATK", "MMCAS", "MNDRS", "MOBTL", "MOGAN",
    "MPARK", "MRGYO", "MRSHL", "MSGYO", "MTRKS",
    "MTRYO", "MZHLD", "NATEN", "NETAS", "NIBAS",
    "NTHOL", "NUGYO", "NUHCM", "OBASE", "ODAS",
    "ODINE", "OFSYM", "ONCSM", "ONRYT", "ORCAY",
    "ORGE", "ORMA", "OSMEN", "OSTIM", "OTKAR",
    "OTTO", "OYAKC", "OYYAT", "OZATD", "OZGYO",
    "OZKGY", "OZSUB", "PAGYO", "PAMEL", "PAPIL",
    "PARSN", "PASEU", "PATEK", "PCILT", "PEGYO",
    "PEKGY", "PENGD", "PENTA", "PETKM", "PETUN",
    "PGSUS", "PINSU", "PKART", "PKENT", "PLTUR",
    "PNLSN", "PNSUT", "POLHO", "POLTK", "PRDGS",
    "PRKAB", "PRKME", "PRZMA", "PSDTC", "PSGYO",
    "QNBFB", "QNBFL", "QUAGR", "RALYH", "RAYSG",
    "REEDR", "RGYAS", "RNPOL", "RODRG", "ROYAL",
    "RTALB", "RUBNS", "RYGYO", "RYSAS", "SAFKR",
    "SAHOL", "SAMAT", "SANEL", "SANFM", "SANKO",
    "SARKY", "SASA", "SAYAS", "SDTTR", "SEGMN",
    "SEGYO", "SEKFK", "SEKUR", "SELEC", "SELGD",
    "SELVA", "SEYKM", "SILVR", "SISE", "SKBNK",
    "SKTAS", "SKYLP", "SKYMD", "SMART", "SMRTG",
    "SNGYO", "SNICA", "SNPAM", "SODSN", "SOKE",
    "SOKM", "SONME", "SRVGY", "SUNTK", "SURGY",
    "SUWEN", "TABGD", "TATEN", "TATGD", "TAVHL",
    "TBORG", "TCELL", "TDGYO", "TEKTU", "TERA",
    "TEZOL", "THYAO", "TKFEN", "TKNSA", "TLMAN",
    "TMPOL", "TMSN", "TOASO", "TRCAS", "TRGYO",
    "TRILC", "TSGYO", "TSKB", "TSPOR", "TTKOM",
    "TTRAK", "TUCLK", "TUKAS", "TUPRS", "TUREX",
    "TURGG", "TURSG", "UFUK", "ULAS", "ULKER",
    "ULUFA", "ULUSE", "ULUUN", "UNLU", "USAK",
    "VAKBN", "VAKFN", "VAKKO", "VANGD", "VBTYZ",
    "VERTU", "VERUS", "VESBE", "VESTL", "VKFYO",
    "VKGYO", "VKING", "VRGYO", "VSNMD", "YAPRK",
    "YATAS", "YAYLA", "YBTAS", "YEOTK", "YESIL",
    "YGGYO", "YGYO", "YIGIT", "YKBNK", "YKSLN",
    "YONGA", "YUNSA", "YYAPI", "ZEDUR", "ZOREN"
]

BIST_HISSELERI = sorted(
    list(set(BIST_HISSELERI))
)

# ==================================================
# VERİ İNDİR
# ==================================================

@st.cache_data(ttl=900)
def veri_indir(hisseler):

    semboller = [
        hisse + ".IS"
        for hisse in hisseler
    ]

    veri = yf.download(
        tickers=semboller,
        period="1y",
        interval="1d",
        group_by="ticker",
        auto_adjust=True,
        progress=False,
        threads=True
    )

    return veri


# ==================================================
# TEK HİSSE ANALİZİ
# ==================================================

def hisse_analiz(veri):

    veri = veri.dropna(
        subset=["Close"]
    )

    if len(veri) < 60:
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
        (fiyat - onceki_fiyat)
        / onceki_fiyat
        * 100
    )

    ma20 = close.rolling(20).mean()
    ma50 = close.rolling(50).mean()

    son_ma20 = float(
        ma20.iloc[-1]
    )

    son_ma50 = float(
        ma50.iloc[-1]
    )

    fark = close.diff()

    yukselis = fark.clip(
        lower=0
    )

    dusus = -fark.clip(
        upper=0
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
    )

    rs = (
        ort_yukselis
        / ort_dusus.replace(
            0,
            np.nan
        )
    )

    rsi = (
        100
        - 100 / (1 + rs)
    )

    son_rsi = float(
        rsi.iloc[-1]
    )

    ort_hacim = float(
        volume
        .rolling(20)
        .mean()
        .iloc[-1]
    )

    son_hacim = float(
        volume.iloc[-1]
    )

    if ort_hacim > 0:

        hacim_orani = (
            son_hacim
            / ort_hacim
        )

    else:

        hacim_orani = 1

    fiyat_araligi = (
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
        * volume
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

    # Trend

    if (
        fiyat > son_ma20
        and son_ma20 > son_ma50
    ):

        trend = 100

        trend_yazi = (
            "🟢 Güçlü yükseliş"
        )

    elif fiyat > son_ma20:

        trend = 70

        trend_yazi = (
            "🟩 Yükseliş"
        )

    elif fiyat > son_ma50:

        trend = 45

        trend_yazi = (
            "🟡 Kararsız"
        )

    else:

        trend = 20

        trend_yazi = (
            "🔴 Düşüş"
        )

    # Hacim

    if hacim_orani >= 2:

        hacim_puani = 100

    elif hacim_orani >= 1.5:

        hacim_puani = 80

    elif hacim_orani >= 1:

        hacim_puani = 55

    else:

        hacim_puani = 25

    # Para

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

    # Momentum

    if 50 <= son_rsi <= 68:

        momentum = 90

    elif 45 <= son_rsi < 50:

        momentum = 60

    elif son_rsi > 68:

        momentum = 50

    else:

        momentum = 25

    # Erken hareket

    son_20_yuksek = float(
        high.tail(20).max()
    )

    son_20_dusuk = float(
        low.tail(20).min()
    )

    bant_genisligi = (
        (son_20_yuksek - son_20_dusuk)
        / fiyat
        * 100
    )

    erken_hareket = 0

    if hacim_orani >= 1.3:

        erken_hareket += 35

    if 48 <= son_rsi <= 62:

        erken_hareket += 25

    if fiyat > son_ma20:

        erken_hareket += 20

    if bant_genisligi <= 15:

        erken_hareket += 20

    # Risk

    risk = 0

    if son_rsi >= 75:

        risk += 40

    if fiyat < son_ma20:

        risk += 25

    if son_cmf < 0:

        risk += 20

    if hacim_orani < 0.70:

        risk += 15

    risk = min(
        risk,
        100
    )

    # Spek puanı

    spek_puani = round(

        trend * 0.25

        + hacim_puani * 0.20

        + para_puani * 0.25

        + momentum * 0.15

        + erken_hareket * 0.15

        - risk * 0.10

    )

    spek_puani = max(
        0,
        min(
            spek_puani,
            100
        )
    )

    # Toplama

    toplama = round(

        para_puani * 0.45

        + hacim_puani * 0.25

        + trend * 0.20

        + momentum * 0.10

    )

    if toplama >= 75:

        toplama_yazi = (
            "🧲 Yüksek"
        )

    elif toplama >= 55:

        toplama_yazi = (
            "🟡 Orta"
        )

    else:

        toplama_yazi = (
            "⚪ Düşük"
        )

    # Dağıtım

    dagitim = 0

    if gunluk_degisim > 1:
        dagitim += 20

    if son_cmf < 0:
        dagitim += 40

    if son_rsi > 70:
        dagitim += 20

    if hacim_orani < 1:
        dagitim += 20

    dagitim = min(
        dagitim,
        100
    )

    # Sinyal

    if (
        spek_puani >= 75
        and risk <= 30
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

    destek = float(
        low.tail(20).min()
    )

    direnc = float(
        high.tail(20).max()
    )

    hedef_alt = direnc

    hedef_ust = (
        direnc
        + (
            direnc - destek
        )
        * 0.50
    )

    zarar_kes = (
        destek * 0.98
    )

    return {

        "Fiyat": fiyat,

        "Günlük %":
        gunluk_degisim,

        "RSI":
        son_rsi,

        "Hacim Oranı":
        hacim_orani,

        "CMF":
        son_cmf,

        "Trend":
        trend,

        "Trend Durumu":
        trend_yazi,

        "Para":
        para_puani,

        "Hacim":
        hacim_puani,

        "Momentum":
        momentum,

        "Erken Hareket":
        erken_hareket,

        "Toplama":
        toplama,

        "Toplama Durumu":
        toplama_yazi,

        "Dağıtım":
        dagitim,

        "Risk":
        risk,

        "Spek Puanı":
        spek_puani,

        "Sinyal":
        sinyal,

        "Destek":
        destek,

        "Direnç":
        direnc,

        "Hedef Alt":
        hedef_alt,

        "Hedef Üst":
        hedef_ust,

        "Zarar Kes":
        zarar_kes

    }


# ==================================================
# ANA SEKMELER
# ==================================================

sekme1, sekme2, sekme3 = st.tabs([

    "🔎 Tek Hisse",

    "📡 Geniş BIST Tarama",

    "ℹ️ Bilgi"

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
        "🦅 HİSSEYİ ANALİZ ET",
        use_container_width=True
    ):

        with st.spinner(
            "Veri alınıyor..."
        ):

            tek_veri = yf.download(
                hisse + ".IS",
                period="1y",
                interval="1d",
                auto_adjust=True,
                progress=False
            )

        if isinstance(
            tek_veri.columns,
            pd.MultiIndex
        ):

            tek_veri.columns = (
                tek_veri.columns
                .get_level_values(0)
            )

        sonuc = hisse_analiz(
            tek_veri
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
                "Spek İz",
                f"{sonuc['Spek Puanı']}/100"
            )

            c.metric(
                "Toplama",
                f"{sonuc['Toplama']}/100"
            )

            d.metric(
                "Risk",
                f"{sonuc['Risk']}/100"
            )

            st.subheader(
                sonuc["Sinyal"]
            )

            x, y, z = st.columns(3)

            x.write(
                "Trend: "
                + sonuc[
                    "Trend Durumu"
                ]
            )

            y.write(
                "Toplama: "
                + sonuc[
                    "Toplama Durumu"
                ]
            )

            z.write(
                "Erken hareket: "
                + str(
                    sonuc[
                        "Erken Hareket"
                    ]
                )
                + "/100"
            )

            st.subheader(
                "🎯 İşlem Bölgeleri"
            )

            h1, h2, h3 = st.columns(3)

            h1.metric(
                "Hedef Bölgesi",
                (
                    f"{sonuc['Hedef Alt']:.2f}"
                    " - "
                    f"{sonuc['Hedef Üst']:.2f}"
                    " TL"
                )
            )

            h2.metric(
                "Destek",
                f"{sonuc['Destek']:.2f} TL"
            )

            h3.metric(
                "Zarar Kes",
                f"{sonuc['Zarar Kes']:.2f} TL"
            )

            st.subheader(
                "📈 Fiyat Grafiği"
            )

            grafik = pd.DataFrame({

                "Kapanış":
                tek_veri["Close"],

                "MA20":
                tek_veri["Close"]
                .rolling(20)
                .mean(),

                "MA50":
                tek_veri["Close"]
                .rolling(50)
                .mean()

            })

            st.line_chart(
                grafik.tail(120)
            )


# ==================================================
# GENİŞ BIST TARAMA
# ==================================================

with sekme2:

    st.subheader(
        "📡 Geniş BIST Tarama"
    )

    st.write(
        f"Tarama listesinde "
        f"{len(BIST_HISSELERI)} "
        f"benzersiz hisse bulunuyor."
    )

    st.warning(
        "Geniş tarama birkaç dakika sürebilir. "
        "Tarama sırasında sayfayı kapatmayın."
    )

    tarama_adedi = st.selectbox(

        "Tarama kapsamı",

        [
            50,
            100,
            200,
            "TÜM LİSTE"
        ],

        index=3

    )

    if st.button(

        "🦅 GENİŞ BIST TARAMASINI BAŞLAT",

        use_container_width=True

    ):

        if tarama_adedi == "TÜM LİSTE":

            secilenler = (
                BIST_HISSELERI
            )

        else:

            secilenler = (
                BIST_HISSELERI[
                    :tarama_adedi
                ]
            )

        baslangic = time.time()

        ilerleme = st.progress(0)

        durum = st.empty()

        sonuclar = []

        toplam = len(
            secilenler
        )

        for i, kod in enumerate(
            secilenler
        ):

            durum.write(
                f"Taranıyor: {kod} "
                f"({i + 1}/{toplam})"
            )

            try:

                veri = yf.download(

                    kod + ".IS",

                    period="1y",

                    interval="1d",

                    auto_adjust=True,

                    progress=False

                )

                if isinstance(
                    veri.columns,
                    pd.MultiIndex
                ):

                    veri.columns = (
                        veri.columns
                        .get_level_values(0)
                    )

                sonuc = hisse_analiz(
                    veri
                )

                if sonuc is not None:

                    sonuclar.append({

                        "Hisse":
                        kod,

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

                        "Sinyal":
                        sonuc[
                            "Sinyal"
                        ],

                        "Trend":
                        sonuc[
                            "Trend Durumu"
                        ],

                        "Toplama":
                        sonuc[
                            "Toplama"
                        ],

                        "Toplama Gücü":
                        sonuc[
                            "Toplama Durumu"
                        ],

                        "Erken Hareket":
                        sonuc[
                            "Erken Hareket"
                        ],

                        "Dağıtım":
                        sonuc[
                            "Dağıtım"
                        ],

                        "Risk":
                        sonuc[
                            "Risk"
                        ],

                        "Hacim Oranı":
                        round(
                            sonuc[
                                "Hacim Oranı"
                            ],
                            2
                        ),

                        "RSI":
                        round(
                            sonuc[
                                "RSI"
                            ],
                            1
                        )

                    })

            except Exception:

                pass

            ilerleme.progress(

                int(

                    (
                        i + 1
                    )

                    / toplam

                    * 100

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
                    "Spek",
                    ascending=False
                )
                .reset_index(
                    drop=True
                )
            )

            sure = round(
                time.time()
                - baslangic,
                1
            )

            st.success(
                f"Tarama tamamlandı. "
                f"{len(tablo)} hisse analiz edildi. "
                f"Süre: {sure} saniye."
            )

            o1, o2, o3, o4 = (
                st.columns(4)
            )

            o1.metric(
                "Analiz Edilen",
                len(tablo)
            )

            o2.metric(
                "Güçlü AL",
                len(
                    tablo[
                        tablo[
                            "Sinyal"
                        ]
                        == "🟢 GÜÇLÜ AL"
                    ]
                )
            )

            o3.metric(
                "Erken Hareket",
                len(
                    tablo[
                        tablo[
                            "Erken Hareket"
                        ]
                        >= 70
                    ]
                )
            )

            o4.metric(
                "Yüksek Dağıtım",
                len(
                    tablo[
                        tablo[
                            "Dağıtım"
                        ]
                        >= 60
                    ]
                )
            )

            st.subheader(
                "🏆 En Güçlü 20"
            )

            st.dataframe(
                tablo.head(20),
                use_container_width=True,
                hide_index=True
            )

            st.subheader(
                "🟢 Güçlü AL Adayları"
            )

            guclu_al = tablo[

                tablo[
                    "Sinyal"
                ].isin([

                    "🟢 GÜÇLÜ AL",

                    "🟩 AL / İZLE"

                ])

            ]

            st.dataframe(
                guclu_al,
                use_container_width=True,
                hide_index=True
            )

            st.subheader(
                "🚀 Erken Hareket Radarı"
            )

            erken = tablo[

                tablo[
                    "Erken Hareket"
                ] >= 70

            ]

            st.dataframe(
                erken,
                use_container_width=True,
                hide_index=True
            )

            st.subheader(
                "🧲 Toplama İhtimali"
            )

            toplama = tablo[

                tablo[
                    "Toplama"
                ] >= 70

            ]

            st.dataframe(
                toplama,
                use_container_width=True,
                hide_index=True
            )

            st.subheader(
                "🚨 Dağıtım Riski"
            )

            dagitim = tablo[

                tablo[
                    "Dağıtım"
                ] >= 60

            ]

            st.dataframe(
                dagitim,
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
                    ].str.contains(
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

                "📥 SONUÇLARI CSV OLARAK İNDİR",

                data=csv,

                file_name=(
                    "spek_avcisi_v16"
                    "_bist_tarama.csv"
                ),

                mime=(
                    "text/csv"
                ),

                use_container_width=True

            )

        else:

            st.error(
                "Hiçbir hisseden "
                "yeterli veri alınamadı."
            )


# ==================================================
# BİLGİ
# ==================================================

with sekme3:

    st.subheader(
        "ℹ️ V16 Hakkında"
    )

    st.write(
        "Spek Avcısı; günlük fiyat, "
        "hacim, RSI, hareketli ortalama "
        "ve CMF verilerinden teknik "
        "olasılık puanı üretir."
    )

    st.write(
        "Toplama, dağıtım ve erken hareket "
        "ifadeleri teknik model tahminidir. "
        "Gerçek emir defteri, kademe, "
        "kurum takası veya belirli kişilerin "
        "işlemlerini doğrudan göstermez."
    )

    st.warning(
        "Bu uygulama yatırım tavsiyesi "
        "vermez ve kesin kazanç garantisi "
        "sunmaz."
    )
