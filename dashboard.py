from __future__ import annotations

import pandas as pd
import streamlit as st


def show_market_header(market_text: str) -> None:
    st.info(f"Piyasa filtresi: {market_text}")


def show_portfolio_health(health: dict) -> None:
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Portföy Gücü", f"{health['Güç']}/100")
    c2.metric("Ortalama Risk", f"{health['Risk']}/100")
    c3.metric("Ortalama Güven", f"{health['Güven']}/100")
    c4.metric("Olumlu Hisse", health["Olumlu"])
    c5.metric("Risk Uyarısı", health["Uyarı"])


def show_daily_summary(
    market_text: str,
    portfolio_table: pd.DataFrame,
    alerts: pd.DataFrame,
) -> None:
    st.subheader("☀️ Günlük Açılış Özeti")
    st.write(f"**Piyasa:** {market_text}")

    if portfolio_table.empty:
        st.warning("Portföy analizi henüz yapılmadı.")
        return

    best = portfolio_table.sort_values(
        ["İşlem Kalitesi", "Risk"],
        ascending=[False, True],
    ).head(3)

    risky = portfolio_table.sort_values(
        "Risk",
        ascending=False,
    ).head(3)

    left, right = st.columns(2)

    with left:
        st.markdown("### 🏆 Portföyde en güçlüler")
        st.dataframe(
            best[["Hisse", "Durum", "İşlem Kalitesi", "Güven", "Risk"]],
            use_container_width=True,
            hide_index=True,
        )

    with right:
        st.markdown("### 🚨 Öncelikli riskler")
        st.dataframe(
            risky[["Hisse", "Durum", "Risk", "Kontrol"]],
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("### 🔔 Aktif alarmlar")
    if alerts.empty:
        st.success("Aktif alarm bulunmuyor.")
    else:
        st.dataframe(alerts, use_container_width=True, hide_index=True)
