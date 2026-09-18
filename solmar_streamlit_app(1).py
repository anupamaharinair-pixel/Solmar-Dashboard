import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="Solmar Eyewear — DTC Dashboard", layout="wide")

# -------------------------------------------------------------
# 1. LOAD & CLEAN DATA
# -------------------------------------------------------------
st.title("Solmar Eyewear — DTC Executive Performance Dashboard")
st.caption("109-week view of revenue, paid media, and promotional performance")

# Path to the case study file on your machine — update this if you move the file.
excel_path = r"C:\Users\Anupama\Downloads\Solmar_Eyewear_Case_Study.xlsx"


@st.cache_data
def load_data(file):
    df = pd.read_excel(file, sheet_name="Master data")
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    spend_cols = [
        "spend_Meta_Asc_Retargeting",
        "spend_Meta_Asc",
        "spend_Meta_Retargeting_Manual",
        "spend_Meta_Broad_Manual",
        "spend_Meta_Non_Sales",
        "spend_google_PMAX_Exist",
        "spend_google_Search_Non_Brand",
        "spend_google_PMAX_New",
        "spend_google_Search_Brand",
        "spend_google_Shopping",
        "spend_snapchat",
        "spend_Youtube",
        "Tiktok_DTC_Spends",
    ]
    df["total_spend"] = df[spend_cols].sum(axis=1)
    df["blended_mer"] = df["total_revenue"] / df["total_spend"]

    meta_cols = [
        "spend_Meta_Asc_Retargeting",
        "spend_Meta_Asc",
        "spend_Meta_Retargeting_Manual",
        "spend_Meta_Broad_Manual",
        "spend_Meta_Non_Sales",
    ]
    google_cols = [
        "spend_google_PMAX_Exist",
        "spend_google_Search_Non_Brand",
        "spend_google_PMAX_New",
        "spend_google_Search_Brand",
        "spend_google_Shopping",
    ]
    video_cols = ["spend_snapchat", "spend_Youtube", "Tiktok_DTC_Spends"]

    df["spend_meta"] = df[meta_cols].sum(axis=1)
    df["spend_google"] = df[google_cols].sum(axis=1)
    df["spend_video"] = df[video_cols].sum(axis=1)

    df["rev_ma4"] = df["total_revenue"].rolling(window=4).mean()
    df["rev_ma12"] = df["total_revenue"].rolling(window=12).mean()

    return df


df = load_data(excel_path)

# -------------------------------------------------------------
# 2. SHARED METRICS (used across tabs)
# -------------------------------------------------------------
tot_rev = df["total_revenue"].sum()
tot_spend = df["total_spend"].sum()
new_rev = df["new_customer_revenue"].sum()
rep_rev = df["repeat_customer_revenue"].sum()
new_pct = new_rev / tot_rev * 100
rep_pct = rep_rev / tot_rev * 100
meta_pct = df["spend_meta"].sum() / df["total_spend"].sum() * 100
google_pct = df["spend_google"].sum() / df["total_spend"].sum() * 100
video_pct = df["spend_video"].sum() / df["total_spend"].sum() * 100

bfcm_n = df.groupby("BFCM_promo").size()
bfcm_avg = df.groupby("BFCM_promo")[["total_revenue", "total_spend"]].mean() / 1e6
bfcm_mer = bfcm_avg["total_revenue"] / bfcm_avg["total_spend"]
bfcm_lift_pct = (bfcm_avg.loc[1, "total_revenue"] / bfcm_avg.loc[0, "total_revenue"] - 1) * 100

before = df[df["date"] < "2026-01-04"]
after = df[df["date"] >= "2026-01-04"]
mer_before = before["total_revenue"].sum() / before["total_spend"].sum()
mer_after = after["total_revenue"].sum() / after["total_spend"].sum()

# -------------------------------------------------------------
# 3. PAGES (TABS)
# -------------------------------------------------------------
tab_dashboard, tab_interpretation, tab_recommendations = st.tabs(
    ["📊 Dashboard", "🔍 Interpretation", "✅ Recommendations"]
)

# ---------------- TAB 1: DASHBOARD ----------------
with tab_dashboard:
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Revenue", f"${tot_rev/1e6:,.1f}M")
    c2.metric("Total Ad Spend", f"${tot_spend/1e6:,.1f}M")
    c3.metric("Blended MER", f"{tot_rev/tot_spend:.2f}x")
    c4.metric("New Customer Rev", f"{new_pct:.1f}%")
    c5.metric("Repeat Customer Rev", f"{rep_pct:.1f}%")

    st.divider()

    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle(
        "Solmar Eyewear — DTC Executive Performance Dashboard (109 Weeks)",
        fontsize=16, weight="bold", y=0.98,
    )

    # Panel 1: Trajectory & Seasonality
    ax1 = axes[0, 0]
    ax1.plot(df["date"], df["total_revenue"] / 1e6, label="Weekly Net Revenue", color="#1f77b4", alpha=0.35, lw=1.2)
    ax1.plot(df["date"], df["rev_ma4"] / 1e6, label="4-Week Moving Avg (Momentum)", color="#1f77b4", lw=2)
    ax1.plot(df["date"], df["rev_ma12"] / 1e6, label="12-Week Moving Avg (Trend)", color="#ff7f0e", lw=2.2, linestyle="--")
    for i, (start, end) in enumerate([("2025-05-01", "2025-07-31"), ("2026-05-01", "2026-07-31")]):
        ax1.axvspan(
            pd.to_datetime(start), pd.to_datetime(end), color="gold", alpha=0.2,
            label="Summer Peak Window" if i == 0 else None,
        )
    ax1.axvline(pd.to_datetime("2026-01-04"), color="red", linestyle=":", label="8% Tariff Price Hike")
    ax1.set_title("1. Weekly Revenue Trajectory & Seasonal Cycles", fontsize=12, weight="bold")
    ax1.set_ylabel("Revenue ($ Millions)")
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax1.legend(loc="upper left", fontsize=8.5)
    ax1.tick_params(axis="x", rotation=30)

    # Panel 2: Paid Media Share
    ax2 = axes[0, 1]
    spend_share = df[["spend_meta", "spend_google", "spend_video"]].div(df["total_spend"], axis=0) * 100
    ax2.stackplot(
        df["date"], spend_share["spend_meta"], spend_share["spend_google"], spend_share["spend_video"],
        labels=[f"Meta ({meta_pct:.1f}%)", f"Google ({google_pct:.1f}%)", f"Social Video ({video_pct:.1f}%)"],
        colors=["#4267B2", "#34A853", "#EA4335"], alpha=0.85,
    )
    ax2.set_title("2. Paid Media Channel Spend Distribution", fontsize=12, weight="bold")
    ax2.set_ylabel("Spend Share (%)")
    ax2.set_ylim(0, 100)
    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax2.legend(loc="lower left", fontsize=9)
    ax2.tick_params(axis="x", rotation=30)

    # Panel 3: Acquisition vs. Retention
    ax3 = axes[1, 0]
    ax3.stackplot(
        df["date"], df["repeat_customer_revenue"] / 1e6, df["new_customer_revenue"] / 1e6,
        labels=[f"Repeat Customer ({rep_pct:.1f}%)", f"New Customer ({new_pct:.1f}%)"],
        colors=["#2ca02c", "#98df8a"], alpha=0.85,
    )
    ax3.set_title("3. Revenue Composition: Acquisition vs. Retention", fontsize=12, weight="bold")
    ax3.set_ylabel("Net Revenue ($ Millions)")
    ax3.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax3.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax3.legend(loc="upper left", fontsize=9)
    ax3.tick_params(axis="x", rotation=30)

    # Panel 4: Regular vs. BFCM Event Comparison
    ax4 = axes[1, 1]
    labels = ["Non-BFCM Weeks", "BFCM Weeks"]
    bars = ax4.bar(labels, bfcm_avg["total_revenue"], color=["#98df8a", "#d62728"], width=0.5)
    for bar, m, n in zip(bars, bfcm_mer, bfcm_n):
        h = bar.get_height()
        ax4.text(
            bar.get_x() + bar.get_width() / 2, h + 0.05,
            f"${h:.2f}M\n({m:.1f}x MER, n={n})", ha="center", weight="bold",
        )
    ax4.set_title("4. Avg Weekly Revenue: Regular vs. BFCM", fontsize=12, weight="bold")
    ax4.set_ylabel("Revenue ($ Millions)")
    ax4.set_ylim(0, bfcm_avg["total_revenue"].max() * 1.3)
    ax4.grid(axis="y", alpha=0.3)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    st.pyplot(fig)

# ---------------- TAB 2: INTERPRETATION ----------------
with tab_interpretation:
    st.subheader("Panel 1 — Revenue Trajectory")
    st.write(
        "Revenue is highly seasonal, not flat. There are two recurring high points each year — "
        "a summer peak (May–Jul) and a November spike tied to BFCM — separated by softer stretches "
        "in winter and early autumn. The pattern repeats across both years in the data, so it's "
        "structural rather than a one-off. The tariff-driven price hike (Jan 2026) doesn't visibly "
        "break the cycle — revenue keeps moving the same seasonal way after it."
    )

    st.subheader("Panel 2 — Channel Mix")
    st.write(
        f"Spend is Meta-heavy ({meta_pct:.0f}%) with Google second ({google_pct:.0f}%) and video "
        f"platforms a distant third ({video_pct:.0f}%). Meta's share has grown over time — the "
        "business has leaned harder into Meta rather than diversifying, even though that doesn't "
        "necessarily mean Meta is the most efficient channel on a blended basis."
    )

    st.subheader("Panel 3 — Acquisition vs. Retention")
    st.write(
        f"Repeat customers contribute slightly more revenue overall ({rep_pct:.0f}% vs. "
        f"{new_pct:.0f}% new), and that split holds fairly steady through the seasonal spikes — "
        "both new and repeat revenue surge together during peaks, rather than one driving the other. "
        "Peak periods appear to pull in new buyers and reactivate existing ones at the same time."
    )

    st.subheader("Panel 4 — BFCM Effect")
    st.write(
        f"This is the sharpest finding on the dashboard. BFCM weeks average "
        f"${bfcm_avg.loc[1,'total_revenue']:.2f}M vs. ${bfcm_avg.loc[0,'total_revenue']:.2f}M for a "
        f"normal week — a {bfcm_lift_pct:.0f}% lift — and they do it at a *better* MER "
        f"({bfcm_mer.loc[1]:.1f}x vs. {bfcm_mer.loc[0]:.1f}x), meaning the extra revenue isn't coming "
        f"from spending less efficiently. Worth noting: this is based on only {bfcm_n.loc[1]} BFCM "
        "weeks, so treat the exact numbers as directional rather than precise."
    )

    st.subheader("Additional pattern — Price hike vs. spend efficiency")
    st.write(
        f"Blended MER was {mer_before:.2f}x before the Jan 2026 price hike and {mer_after:.2f}x after "
        "— average revenue rose slightly, but spend rose faster, so overall efficiency slipped even "
        "though the price hike itself was meant to protect margin."
    )

# ---------------- TAB 3: RECOMMENDATIONS ----------------
with tab_recommendations:
    st.subheader("What to do with this")
    st.markdown(
        f"""
1. **Test extending BFCM-style promo mechanics into the summer peak window.**
   BFCM already proves Solmar can grow revenue {bfcm_lift_pct:.0f}% without hurting efficiency
   ({bfcm_mer.loc[1]:.1f}x vs. {bfcm_mer.loc[0]:.1f}x MER). The summer peak already exists organically
   — pairing it with BFCM-level promo intensity (discount depth, urgency messaging, bundling) is a
   low-risk way to test whether that lift is repeatable outside November.

2. **Re-examine the Meta-heavy spend mix.**
   Meta's share of spend has grown to {meta_pct:.0f}% over time, but that growth wasn't shown to be
   driven by superior efficiency. Worth running a modest reallocation test toward Google or video to
   see if marginal returns hold up — right now the mix looks more like habit than validated ROI.

3. **Investigate the post-price-hike efficiency drop.**
   MER fell from {mer_before:.2f}x to {mer_after:.2f}x after the Jan 2026 hike, even as revenue rose.
   That's worth digging into directly — is spend being pushed harder to defend volume after the price
   increase, or did acquisition simply get more expensive? Either answer changes what to do next.

4. **Don't over-read thin-sample promo segments.**
   Some promo-mechanic groupings in the data are based on only 1–3 weeks. Any recommendation drawn
   from those bins should be flagged as low-confidence rather than presented with the same weight as
   the BFCM finding, which has clearer support in the data.

5. **Keep repeat-customer revenue steady while testing acquisition levers.**
   Repeat customers already contribute {rep_pct:.0f}% of revenue and move in lockstep with new-customer
   revenue during peaks — any new promo push (recommendation #1) should be checked that it isn't just
   pulling forward repeat-customer spend rather than genuinely growing the new-customer base.
"""
    )
