import pandas as pd
import streamlit as st

from config import DEFAULT_FAVORITES, DEFAULT_PORTFOLIO
from dashboard import show_daily_summary, show_market_header, show_portfolio_health
from data import download_market, download_symbol
from engine import analyze, market_score
from portfolio import (
    create_alerts,
    export_lists,
    import_lists,
    normalize_symbols,
    portfolio_health,
    portfolio_table,
)
from scanner import scan
from universe import BIST_SYMBOLS


APP_TITLE = "Spek Avcısı V23 Intelligence"

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🦅",
    layout="wide",
)

st.title(f"🦅 {APP_TITLE}")
st.caption(
    "Trend evresi, para akışı yönü, parçalı risk motoru, karar güveni ve AI Koçu."
)


@st.cache_data(ttl=600, max_entries=600)
def cached_symbol(symbol: str):
    return download_symbol(symbol)


@st.cache_data(ttl=900, max_entries=12)
def cached_scan(symbols: tuple[str, ...], market: int):
    return scan(list(symbols), market)


@st.cache_data(ttl=600, max_entries=30)
def cached_portfolio(symbols: tuple[str, ...], market: int):
    return portfolio_table(list(symbols), market)


if "portfolio_symbols" not in st.session_state:
    st.session_state.portfolio_symbols = DEFAULT_PORTFOLIO.copy()

if "favorite_symbols" not in st.session_state:
    st.session_state.favorite_symbols = DEFAULT_FAVORITES.copy()

if "portfolio_result" not in st.session_state:
    st.session_state.portfolio_result = pd.DataFrame()


market_value, market_text = market_score(download_market())
show_market_header(market_text)


tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Dashboard",
    "🧠 Intelligence",
    "📂 Portföyüm",
    "⭐ Favoriler",
    "📡 BIST Tarayıcı",
])


with tab1:
    if st.button("🔄 DASHBOARD'U GÜNCELLE", use_container_width=True):
        with st.spinner("Portföy ve alarmlar güncelleniyor..."):
            st.session_state.portfolio_result = cached_portfolio(
                tuple(st.session_state.portfolio_symbols),
                market_value,
            )

    health = portfolio_health(st.session_state.portfolio_result)
    alerts = create_alerts(st.session_state.portfolio_result)

    show_portfolio_health(health)
    show_daily_summary(
        market_text,
        st.session_state.portfolio_result,
        alerts,
    )


with tab2:
    symbol = st.text_input(
        "Hisse kodu",
        value="THYAO",
        key="intelligence_symbol",
    ).strip().upper()

    if st.button("🧠 INTELLIGENCE ANALİZİ", use_container_width=True):
        frame = cached_symbol(symbol)
        result = analyze(frame, market=market_value) if frame is not None else None

        if result is None:
            st.error("Yeterli veri bulunamadı.")
        else:
            st.subheader(f"{symbol} — {result['Karar']}")
            st.caption(f"Veri tarihi: {result['Veri Tarihi']}")

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric(
                "Son Fiyat",
                f"{result['Fiyat']:.2f} TL",
                f"%{result['Günlük %']:.2f}",
            )
            c2.metric("Güven", f"{result['Güven']}/100")
            c3.metric("Güvenilirlik", result["Güven Yıldızı"])
            c4.metric("İşlem Kalitesi", f"{result['İşlem Kalitesi']}/100")
            c5.metric("Toplam Risk", f"{result['Risk']}/100")

            st.subheader("🧬 Trend DNA")
            t1, t2, t3 = st.columns(3)
            t1.metric("Trend Evresi", result["Trend Evresi"])
            t2.metric("Trend Gücü", f"{result['Trend Gücü']}/100")
            t3.metric("Hareket Hazırlığı", f"{result['Hareket Hazırlığı']}/100")

            st.subheader("💰 Para Akışı")
            p1, p2 = st.columns(2)
            p1.metric("Para Akışı Yönü", result["Para Akışı Yönü"])
            p2.metric("Para Akışı Puanı", f"{result['Para Akışı Puanı']}/100")

            para_df = pd.DataFrame(
                {
                    "Bileşen": list(result["Para Bileşenleri"].keys()),
                    "Puan": list(result["Para Bileşenleri"].values()),
                }
            )
            st.dataframe(para_df, use_container_width=True, hide_index=True)

            st.subheader("🛡️ Risk Motoru")
            risk_df = pd.DataFrame(
                {
                    "Risk Kaynağı": list(result["Risk Bileşenleri"].keys()),
                    "Puan": list(result["Risk Bileşenleri"].values()),
                }
            )
            st.dataframe(risk_df, use_container_width=True, hide_index=True)

            st.subheader("🤖 AI Koçu")
            st.info(result["AI Koçu"])

            st.subheader("✅ Kanıtlar")
            for item in result["Olumlu Nedenler"]:
                st.write("✅", item)

            st.subheader("⚠️ Dikkat")
            for item in result["Uyarılar"]:
                st.write("⚠️", item)

            z1, z2, z3, z4 = st.columns(4)
            z1.metric("Destek", f"{result['Destek']:.2f} TL")
            z2.metric("Direnç", f"{result['Direnç']:.2f} TL")
            z3.metric(
                "Hedef Bölgesi",
                f"{result['Hedef Alt']:.2f}–{result['Hedef Üst']:.2f} TL",
            )
            z4.metric("Kontrol", f"{result['Kontrol']:.2f} TL")

            chart = pd.DataFrame(
                {
                    "Kapanış": frame["Close"],
                    "MA20": frame["Close"].rolling(20).mean(),
                    "MA50": frame["Close"].rolling(50).mean(),
                }
            ).tail(180)
            st.line_chart(chart)


with tab3:
    st.subheader("📂 Portföy Yönetimi")

    portfolio_text = st.text_area(
        "Portföy hisseleri — virgülle ayır",
        value=", ".join(st.session_state.portfolio_symbols),
        height=90,
    )

    p1, p2 = st.columns(2)

    if p1.button("💾 PORTFÖYÜ UYGULA", use_container_width=True):
        st.session_state.portfolio_symbols = normalize_symbols(portfolio_text)
        st.session_state.portfolio_result = pd.DataFrame()
        st.success("Portföy listesi güncellendi.")

    if p2.button("📊 PORTFÖYÜ ANALİZ ET", use_container_width=True):
        with st.spinner("Portföy analiz ediliyor..."):
            st.session_state.portfolio_result = cached_portfolio(
                tuple(st.session_state.portfolio_symbols),
                market_value,
            )

    table = st.session_state.portfolio_result

    if not table.empty:
        show_portfolio_health(portfolio_health(table))

        st.subheader("📋 Portföy Intelligence Tablosu")
        st.dataframe(table, use_container_width=True, hide_index=True)

        st.subheader("🔔 Alarm Merkezi")
        alerts = create_alerts(table)
        if alerts.empty:
            st.success("Aktif alarm bulunmuyor.")
        else:
            st.dataframe(alerts, use_container_width=True, hide_index=True)


with tab4:
    st.subheader("⭐ Favori Hisseler")

    favorite_text = st.text_area(
        "Favoriler — virgülle ayır",
        value=", ".join(st.session_state.favorite_symbols),
        height=90,
    )

    f1, f2 = st.columns(2)

    if f1.button("💾 FAVORİLERİ UYGULA", use_container_width=True):
        st.session_state.favorite_symbols = normalize_symbols(favorite_text)
        st.success("Favori listesi güncellendi.")

    if f2.button("⭐ FAVORİLERİ TARA", use_container_width=True):
        with st.spinner("Favoriler analiz ediliyor..."):
            favorite_table = cached_scan(
                tuple(st.session_state.favorite_symbols),
                market_value,
            )

        if favorite_table.empty:
            st.warning("Favorilerden sonuç üretilemedi.")
        else:
            st.dataframe(favorite_table, use_container_width=True, hide_index=True)

    backup = export_lists(
        st.session_state.portfolio_symbols,
        st.session_state.favorite_symbols,
    )

    st.download_button(
        "📥 LİSTELERİ YEDEKLE",
        data=backup.encode("utf-8"),
        file_name="spek_avcisi_v23_listeler.json",
        mime="application/json",
        use_container_width=True,
    )

    uploaded = st.file_uploader("Liste JSON dosyasını geri yükle", type=["json"])
    if uploaded is not None:
        try:
            p, f = import_lists(uploaded.getvalue().decode("utf-8"))
            st.session_state.portfolio_symbols = p
            st.session_state.favorite_symbols = f
            st.success("Listeler geri yüklendi.")
        except Exception as exc:
            st.error(f"Dosya okunamadı: {exc}")


with tab5:
    scope = st.selectbox(
        "Tarama kapsamı",
        [50, 100, 200, "TÜM LİSTE"],
        index=0,
    )

    selected = BIST_SYMBOLS if scope == "TÜM LİSTE" else BIST_SYMBOLS[:int(scope)]

    if st.button("🦅 INTELLIGENCE TARAMASINI BAŞLAT", use_container_width=True):
        with st.spinner(f"{len(selected)} hisse taranıyor..."):
            result_table = cached_scan(tuple(selected), market_value)

        if result_table.empty:
            st.error("Tarama sonucu üretilemedi.")
        else:
            st.success(f"{len(result_table)} hisse analiz edildi.")

            st.subheader("🏆 En Kaliteli 10")
            st.dataframe(result_table.head(10), use_container_width=True, hide_index=True)

            st.subheader("🆕 Yeni Güçlenenler")
            new_strength = result_table[
                (result_table["Yeni Güç"] >= 60)
                & (result_table["Risk"] <= 45)
                & (result_table["Güven"] >= 60)
            ]
            st.dataframe(new_strength, use_container_width=True, hide_index=True)

            st.subheader("🚨 Sahte Hareket / Dağıtım")
            alert_table = result_table[
                result_table["Sahte Hareket"].str.contains(
                    "Şüphe|zayıf",
                    case=False,
                    na=False,
                )
                | result_table["Toplama/Dağıtım"].str.contains("Dağıtım", na=False)
            ]
            st.dataframe(alert_table, use_container_width=True, hide_index=True)

            csv = result_table.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "📥 TARAMA SONUÇLARINI İNDİR",
                data=csv,
                file_name="spek_avcisi_v23_scan.csv",
                mime="text/csv",
                use_container_width=True,
            )


st.warning(
    "Bu sistem fiyat ve hacim verilerinden olasılık üretir. "
    "Gerçek emir defteri, kurum takası veya belirli yatırımcı işlemlerini doğrudan göstermez."
)
