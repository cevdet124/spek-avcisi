import streamlit as st
import pandas as pd

from config import APP_TITLE
from data import download_market, download_symbol
from engine import analyze, market_score
from scanner import scan
from universe import BIST_SYMBOLS

st.set_page_config(page_title=APP_TITLE, page_icon="🦅", layout="wide")
st.title(f"🦅 {APP_TITLE}")
st.caption("Hızlı günlük kullanım, açıklanabilir kararlar ve en iyi fırsat sıralaması.")

@st.cache_data(ttl=600, max_entries=600)
def cached_symbol(symbol: str):
    return download_symbol(symbol)

@st.cache_data(ttl=900, max_entries=8)
def cached_scan(symbols: tuple[str, ...], market: int):
    return scan(list(symbols), market)

market_value, market_text = market_score(download_market())
st.info(f"Piyasa filtresi: {market_text}")

tab1, tab2, tab3 = st.tabs([
    "🔎 Tek Hisse",
    "🏆 Bugünün En İyi 10'u",
    "📡 BIST Tarayıcı",
])

with tab1:
    symbol = st.text_input("Hisse kodu", value="THYAO").strip().upper()

    if st.button("🦅 PROFESYONEL ANALİZ", use_container_width=True):
        frame = cached_symbol(symbol)
        result = analyze(frame, market=market_value) if frame is not None else None

        if result is None:
            st.error("Yeterli veri bulunamadı.")
        else:
            st.subheader(f"{symbol} — {result['Karar']}")
            st.caption(f"Veri tarihi: {result['Veri Tarihi']}")

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Son Fiyat", f"{result['Fiyat']:.2f} TL", f"%{result['Günlük %']:.2f}")
            c2.metric("Spek İz", f"{result['Spek İz']}/100")
            c3.metric("Güven", f"{result['Güven']}/100")
            c4.metric("İşlem Kalitesi", f"{result['İşlem Kalitesi']}/100")
            c5.metric("Risk", f"{result['Risk']}/100")

            st.subheader("🧠 AI Analist")
            st.success(result["AI Yorum"])

            for item in result["Olumlu Nedenler"]:
                st.write("✅", item)
            for item in result["Uyarılar"]:
                st.write("⚠️", item)

            st.subheader("📊 Güç Haritası")
            cols = st.columns(6)
            values = [
                ("Trend", result["Trend Gücü"]),
                ("Kurumsal Para", result["Kurumsal Para"]),
                ("Hareket Hazırlığı", result["Hareket Hazırlığı"]),
                ("Momentum", result["Momentum"]),
                ("Likidite", result["Likidite"]),
                ("Spekülatif Risk", result["Spekülatif Risk"]),
            ]
            for col, (label, value) in zip(cols, values):
                col.metric(label, f"{value}/100")

            st.subheader("🎯 Teknik Bölgeler")
            z1, z2, z3, z4 = st.columns(4)
            z1.metric("Destek", f"{result['Destek']:.2f} TL")
            z2.metric("Direnç", f"{result['Direnç']:.2f} TL")
            z3.metric("Hedef Bölgesi", f"{result['Hedef Alt']:.2f}–{result['Hedef Üst']:.2f} TL")
            z4.metric("Kontrol Seviyesi", f"{result['Kontrol']:.2f} TL")

            chart = pd.DataFrame({
                "Kapanış": frame["Close"],
                "MA20": frame["Close"].rolling(20).mean(),
                "MA50": frame["Close"].rolling(50).mean(),
            }).tail(180)
            st.line_chart(chart)

with tab2:
    st.subheader("🏆 Bugünün En İyi 10 Fırsatı")
    quick_scope = st.selectbox("Hızlı tarama kapsamı", [50, 100, 200], index=1)

    if st.button("🏆 EN İYİ 10'U BUL", use_container_width=True):
        table = cached_scan(tuple(BIST_SYMBOLS[:quick_scope]), market_value)

        if table.empty:
            st.error("Tarama sonucu üretilemedi.")
        else:
            top10 = table.head(10).copy()
            st.success(f"{quick_scope} hisse içinden en kaliteli 10 aday seçildi.")

            for rank, row in top10.iterrows():
                with st.container(border=True):
                    left, middle, right = st.columns([1, 3, 2])
                    left.markdown(f"## #{rank + 1}")
                    middle.markdown(f"### {row['Hisse']} — {row['Karar']}")
                    middle.write(row["AI Yorum"])
                    right.metric("Kalite", f"{row['Kalite Sırası']}")
                    right.metric("Risk", f"{row['Risk']}/100")

            st.subheader("📋 Özet Tablo")
            st.dataframe(top10, use_container_width=True, hide_index=True)

with tab3:
    scope = st.selectbox("Tarama kapsamı", [50, 100, 200, "TÜM LİSTE"], index=0)
    selected = BIST_SYMBOLS if scope == "TÜM LİSTE" else BIST_SYMBOLS[:int(scope)]

    if st.button("🦅 PRO TARAMAYI BAŞLAT", use_container_width=True):
        table = cached_scan(tuple(selected), market_value)

        if table.empty:
            st.error("Tarama sonucu üretilemedi.")
        else:
            st.success(f"{len(table)} hisse analiz edildi.")

            st.subheader("🏆 En Kaliteli 20")
            st.dataframe(table.head(20), use_container_width=True, hide_index=True)

            st.subheader("🆕 Yeni Güçlenenler")
            new_strength = table[
                (table["Yeni Güç"] >= 60)
                & (table["Risk"] <= 45)
                & (table["Güven"] >= 60)
            ]
            st.dataframe(new_strength, use_container_width=True, hide_index=True)

            st.subheader("🚨 Sahte Hareket / Dağıtım Uyarıları")
            alerts = table[
                table["Sahte Hareket"].str.contains("Şüphe|zayıf", case=False, na=False)
                | table["Toplama/Dağıtım"].str.contains("Dağıtım", na=False)
            ]
            st.dataframe(alerts, use_container_width=True, hide_index=True)

            csv = table.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "📥 TARAMA SONUÇLARINI İNDİR",
                data=csv,
                file_name="spek_avcisi_v21_daily.csv",
                mime="text/csv",
                use_container_width=True,
            )

st.info(
    "Bu uygulama fiyat, hacim ve teknik göstergelerden olasılık üretir. "
    "Gerçek emir defteri, kurum takası veya belirli yatırımcı işlemlerini doğrudan göstermez."
)
