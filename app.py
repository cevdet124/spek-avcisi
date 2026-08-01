import streamlit as st
import pandas as pd
import yfinance as yf

from engine import analyze_frame, download_one, scan_universe
from backtest import BacktestConfig, run_backtest
from universe import BIST_SYMBOLS

st.set_page_config(
    page_title="Spek Avcısı V20 Pro",
    page_icon="🦅",
    layout="wide",
)

st.title("🦅 Spek Avcısı V20 Pro")
st.caption(
    "Çok katmanlı teknik karar destek sistemi: trend, kurumsal para, "
    "hareket hazırlığı, sahte hareket, risk ve işlem kalitesi."
)

@st.cache_data(ttl=600, max_entries=600)
def cached_one(symbol: str):
    return download_one(symbol)

@st.cache_data(ttl=900, max_entries=8)
def cached_scan(symbols: tuple[str, ...], market_score: int):
    return scan_universe(list(symbols), market_score=market_score)

def market_filter():
    try:
        data = yf.download(
            "XU100.IS", period="1y", interval="1d",
            auto_adjust=True, progress=False, timeout=15
        )
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        data = data.dropna()
        if len(data) < 60:
            return 55, "🟡 BIST verisi yetersiz"
        close = data["Close"]
        ma20 = close.rolling(20).mean().iloc[-1]
        ma50 = close.rolling(50).mean().iloc[-1]
        price = close.iloc[-1]
        if price > ma20 > ma50:
            return 90, "🟢 BIST trend pozitif"
        if price > ma50:
            return 65, "🟡 BIST kararsız"
        return 35, "🔴 BIST trend zayıf"
    except Exception:
        return 55, "🟡 BIST filtresi alınamadı"

market_score, market_text = market_filter()
st.info(f"Piyasa filtresi: {market_text}")

tab1, tab2, tab3, tab4 = st.tabs([
    "🔎 Tek Hisse",
    "📡 BIST Tarayıcı",
    "🧪 Backtest",
    "ℹ️ Model ve Sınırlar",
])

with tab1:
    symbol = st.text_input("Hisse kodu", value="THYAO").strip().upper()

    if st.button("🦅 PROFESYONEL ANALİZ", use_container_width=True):
        with st.spinner("Veriler analiz ediliyor..."):
            frame = cached_one(symbol)
            result = analyze_frame(frame, market_score=market_score) if frame is not None else None

        if result is None:
            st.error("Yeterli veya geçerli veri bulunamadı.")
        else:
            st.subheader(f"{symbol} — {result['Karar']}")
            st.caption(f"Veri tarihi: {result['Veri Tarihi']}")

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Son Fiyat", f"{result['Fiyat']:.2f} TL", f"%{result['Günlük %']:.2f}")
            c2.metric("Spek İz", f"{result['Spek İz']}/100")
            c3.metric("Güven", f"{result['Güven']}/100")
            c4.metric("İşlem Kalitesi", f"{result['İşlem Kalitesi']}/100")
            c5.metric("Risk", f"{result['Risk']}/100")

            st.subheader("🧠 Karar Motoru")
            st.success(result["Senaryo"])
            for reason in result["Olumlu Nedenler"]:
                st.write("✅", reason)
            for warning in result["Uyarılar"]:
                st.write("⚠️", warning)

            st.subheader("📊 Güç Haritası")
            cols = st.columns(6)
            labels = [
                ("Trend", "Trend Gücü"),
                ("Kurumsal Para", "Kurumsal Para"),
                ("Hareket Hazırlığı", "Hareket Hazırlığı"),
                ("Momentum", "Momentum"),
                ("Likidite", "Likidite"),
                ("Spekülatif Risk", "Spekülatif Risk"),
            ]
            for col, (label, key) in zip(cols, labels):
                col.metric(label, f"{result[key]}/100")

            st.subheader("🐋 Tahta İzi ve Hareket Kalitesi")
            t1, t2, t3, t4 = st.columns(4)
            t1.write(result["Para Yönü"])
            t2.write(result["Toplama/Dağıtım"])
            t3.write(result["Sahte Hareket"])
            t4.write(result["Trend Değişimi"])

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
    st.subheader("📡 Aşamalı BIST Taraması")
    st.caption(
        "Tarama önce bütün hisseleri hızlı ölçer, sonra en yüksek puanlı adayları "
        "kalite ve risk filtreleriyle sıralar."
    )

    scope = st.selectbox(
        "Tarama kapsamı",
        [50, 100, 200, "TÜM LİSTE"],
        index=0,
    )

    uploaded = st.file_uploader(
        "İsteğe bağlı güncel sembol CSV'si yükle (tek sütun: Hisse)",
        type=["csv"],
    )

    symbols = BIST_SYMBOLS
    if uploaded is not None:
        try:
            uploaded_df = pd.read_csv(uploaded)
            col = "Hisse" if "Hisse" in uploaded_df.columns else uploaded_df.columns[0]
            symbols = sorted(
                set(uploaded_df[col].astype(str).str.strip().str.upper().tolist())
            )
            st.success(f"Yüklenen listede {len(symbols)} sembol var.")
        except Exception as exc:
            st.warning(f"CSV okunamadı: {exc}")

    selected = symbols if scope == "TÜM LİSTE" else symbols[:int(scope)]

    if st.button("🦅 PRO TARAMAYI BAŞLAT", use_container_width=True):
        with st.spinner(f"{len(selected)} hisse taranıyor..."):
            table = cached_scan(tuple(selected), market_score)

        if table.empty:
            st.error("Tarama sonucu üretilemedi.")
        else:
            st.success(f"{len(table)} hisse analiz edildi.")

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("A Sınıfı", int((table["Sınıf"] == "A").sum()))
            m2.metric("Yeni Güçlenen", int((table["Yeni Güç"] >= 60).sum()))
            m3.metric("Yüksek Hazırlık", int((table["Hareket Hazırlığı"] >= 70).sum()))
            m4.metric("Yüksek Risk", int((table["Risk"] >= 60).sum()))

            st.subheader("🏆 En Kaliteli 20")
            st.dataframe(table.head(20), use_container_width=True, hide_index=True)

            st.subheader("🆕 Bugün Yeni Güçlenenler")
            new_strength = table[
                (table["Yeni Güç"] >= 60)
                & (table["Risk"] <= 45)
                & (table["Güven"] >= 60)
            ]
            st.dataframe(new_strength, use_container_width=True, hide_index=True)

            st.subheader("🚀 Hareket Hazırlığı Yüksek")
            preparation = table[
                (table["Hareket Hazırlığı"] >= 70)
                & (table["Risk"] <= 50)
            ]
            st.dataframe(preparation, use_container_width=True, hide_index=True)

            st.subheader("🚨 Sahte Hareket / Dağıtım Uyarıları")
            warnings = table[
                table["Sahte Hareket"].str.contains("Şüphe|Risk", na=False)
                | table["Toplama/Dağıtım"].str.contains("Dağıtım", na=False)
            ]
            st.dataframe(warnings, use_container_width=True, hide_index=True)

            st.subheader("🔎 Tüm Sonuçlar")
            query = st.text_input("Sonuçlarda hisse ara").strip().upper()
            shown = table[table["Hisse"].str.contains(query, na=False)] if query else table
            st.dataframe(shown, use_container_width=True, hide_index=True)

            csv = table.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "📥 TARAMA SONUÇLARINI İNDİR",
                data=csv,
                file_name="spek_avcisi_v18_pro.csv",
                mime="text/csv",
                use_container_width=True,
            )


with tab3:
    st.subheader("🧪 Dinamik Giriş / Çıkış Backtesti")
    st.caption(
        "Backtest yalnızca o tarihe kadar bilinen verileri kullanır; "
        "gelecek fiyatlar sadece sonucu ölçmek için kullanılır."
    )

    bt_symbol = st.text_input(
        "Backtest hissesi",
        value="THYAO",
        key="bt_symbol",
    ).strip().upper()

    b1, b2, b3 = st.columns(3)
    horizon = b1.selectbox(
        "Maksimum taşıma süresi",
        [10, 20, 30],
        index=1,
        format_func=lambda x: f"{x} işlem günü",
    )
    min_score = b2.slider("Minimum Spek İz", 40, 85, 60, 5)
    max_risk = b3.slider("Maksimum Risk", 20, 80, 55, 5)

    b4, b5, b6 = st.columns(3)
    min_confidence = b4.slider("Minimum Güven", 40, 85, 55, 5)
    atr_stop = b5.selectbox("ATR zarar kes", [1.5, 2.0, 2.5, 3.0], index=1)
    trailing_atr = b6.selectbox("ATR hareketli stop", [1.5, 2.0, 2.5, 3.0], index=1)

    b7, b8, b9 = st.columns(3)
    target1 = b7.selectbox("1. hedef ATR", [1.5, 2.0, 2.5], index=1)
    target2 = b8.selectbox("2. hedef ATR", [2.5, 3.5, 4.5], index=1)
    fee_bps = b9.number_input(
        "Toplam işlem maliyeti (baz puan)",
        min_value=0.0, max_value=200.0, value=20.0, step=5.0,
    )
    step = 3

    if st.button("🧪 DİNAMİK BACKTESTİ BAŞLAT", use_container_width=True):
        with st.spinner("Dinamik çıkış kuralları test ediliyor..."):
            bt_frame = cached_one(bt_symbol)
            config = BacktestConfig(
                horizon=int(horizon),
                step=int(step),
                min_score=int(min_score),
                max_risk=int(max_risk),
                min_confidence=int(min_confidence),
                fee_bps=float(fee_bps),
                atr_stop=float(atr_stop),
                atr_target_1=float(target1),
                atr_target_2=float(target2),
                trailing_atr=float(trailing_atr),
            )
            bt_result = (
                run_backtest(bt_frame, market_score=market_score, config=config)
                if bt_frame is not None
                else {"summary": {}, "trades": pd.DataFrame(), "equity": pd.DataFrame()}
            )

        summary = bt_result["summary"]
        trades = bt_result["trades"]
        equity = bt_result["equity"]

        if not summary:
            st.warning("Bu ayarlarla yeterli geçmiş sinyal bulunamadı.")
        else:
            st.success(f"{bt_symbol} backtest tamamlandı.")

            metric_items = list(summary.items())
            first = st.columns(5)
            for col, (label, value) in zip(first, metric_items[:5]):
                col.metric(label, value)

            second = st.columns(4)
            for col, (label, value) in zip(second, metric_items[5:9]):
                col.metric(label, value)

            st.subheader("📈 Strateji Bileşik Getiri Eğrisi")
            st.line_chart(equity)

            st.subheader("📋 Geçmiş Sinyaller")
            st.dataframe(
                trades.sort_values("Tarih", ascending=False),
                use_container_width=True,
                hide_index=True,
            )

            csv = trades.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "📥 BACKTEST İŞLEMLERİNİ İNDİR",
                data=csv,
                file_name=f"{bt_symbol}_v19_backtest.csv",
                mime="text/csv",
                use_container_width=True,
            )

            st.info(
                "Başarı oranı tek başına yeterli değildir. İşlem sayısı, ortalama getiri, "
                "maksimum düşüş, kâr faktörü ve farklı dönemlerde tutarlılık birlikte değerlendirilmelidir."
            )

with tab4:
    st.subheader("V20 Pro ne yapar?")
    st.write(
        "Model; günlük ve haftalık trend, RSI, MACD, CMF, MFI, OBV, A/D Line, "
        "hacim devamlılığı, ATR, likidite, sıkışma, kırılım ve BIST piyasa "
        "filtresini birlikte değerlendirir."
    )
    st.warning(
        "Kurumsal para, toplama, dağıtım ve sahte hareket ifadeleri fiyat-hacim "
        "verilerinden türetilmiş olasılık göstergeleridir. Gerçek emir defterini, "
        "kurum takasını veya belirli bir yatırımcıyı doğrudan göstermez."
    )
    st.error(
        "Bu uygulama yatırım tavsiyesi değildir. Üretilen puanlar ve seviyeler "
        "kesin kazanç ya da kesin alım-satım garantisi sunmaz."
    )
