import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="CashRaaga – Bank Statement Analyzer",
    page_icon="💰",
    layout="wide"
)

# ---------- GLOBAL STYLES ----------
st.markdown(
    """
    <style>
    /* Base – dark minimal */
    .stApp {
        background: radial-gradient(circle at top, #020617 0, #020617 40%, #020617 100%);
        color: #e5e7eb;
    }

    [data-testid="stSidebar"] {
        background-color: #020617;
        border-right: 1px solid #111827;
    }

    /* Top bar */
    .cr-topbar {
        max-width: 1120px;
        margin: 10px auto 4px auto;
        padding: 8px 12px 4px 12px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        color: #e5e7eb;
    }
    .cr-left {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .cr-logo {
        width: 30px;
        height: 30px;
        border-radius: 10px;
        background: rgba(34,197,94,0.10);
        border: 1px solid rgba(34,197,94,0.55);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        color: #4ade80;
        font-size: 16px;
    }
    .cr-title {
        font-weight: 700;
        font-size: 1.05rem;
        color: #f9fafb;
    }
    .cr-tagline {
        font-size: 0.8rem;
        color: #9ca3af;
    }
    .cr-chip {
        font-size: 0.75rem;
        padding: 4px 9px;
        border-radius: 999px;
        border: 1px solid #1f2937;
        background-color: #020617;
        color: #9ca3af;
    }

    /* Content wrapper */
    .cr-wrapper {
        max-width: 1120px;
        margin: 0 auto 40px auto;
        padding: 6px 12px 24px 12px;
    }

    .cr-section-title {
        font-size: 0.95rem;
        font-weight: 600;
        margin-bottom: 0.15rem;
        color: #e5e7eb;
    }
    .cr-section-sub {
        font-size: 0.8rem;
        color: #9ca3af;
        margin-bottom: 0.4rem;
    }

    /* Generic card */
    .cr-card {
        background-color: #020617;
        border-radius: 12px;
        border: 1px solid #1f2937;
        padding: 12px 14px;
    }

    /* Snapshot card styles */
    .snapshot-wrapper {
        background: radial-gradient(circle at top left, #022c22 0, #020617 55%, #020617 100%);
        border-radius: 18px;
        border: 1px solid #022c22;
        padding: 14px 16px;
        box-shadow: 0 22px 46px rgba(15,23,42,0.9);
        margin-bottom: 10px;
    }
    .snapshot-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
    }
    .snapshot-title {
        font-size: 0.98rem;
        font-weight: 600;
        color: #f9fafb;
    }
    .snapshot-cards {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 10px;
        margin-bottom: 8px;
    }
    .snapshot-card {
        border-radius: 14px;
        padding: 8px 10px 10px 10px;
        background: radial-gradient(circle at top left, #22c55e30, #022c22 60%, #020617 100%);
        border: 1px solid rgba(34,197,94,0.55);
    }
    .snapshot-label {
        font-size: 0.78rem;
        color: #a5b4fc;
        margin-bottom: 2px;
    }
    .snapshot-value {
        font-size: 1.05rem;
        font-weight: 700;
        color: #f9fafb;
    }
    .snapshot-subtext {
        font-size: 0.75rem;
        color: #cbd5f5;
    }
    .snapshot-ai {
        margin-top: 4px;
        margin-bottom: 4px;
        font-size: 0.78rem;
        color: #e5e7eb;
        padding: 6px 10px;
        border-radius: 999px;
        background: rgba(15,23,42,0.9);
        border: 1px solid #1f2937;
    }
    .snapshot-ai span {
        color: #4ade80;
    }

    /* Metrics */
    .metric-card > div {
        border-radius: 10px !important;
        border: 1px solid #1f2937 !important;
        background-color: #020617 !important;
        padding: 10px 12px !important;
    }

    .small-note {
        font-size: 0.78rem;
        color: #9ca3af;
    }

    /* Tabs */
    .stTabs [role="tablist"] > div {
        gap: 6px;
    }
    .stTabs [role="tab"] {
        padding: 4px 10px;
        font-size: 0.85rem;
        color: #e5e7eb;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Helper to style bar charts consistently (green, dark theme)
def style_dark_bar(fig, height=240):
    fig.update_traces(
        marker_color="#22c55e",
        marker_line_color="#15803d",
        marker_line_width=1,
    )
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,1)",
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            title="",
            tickfont=dict(color="#9ca3af"),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#0f172a",
            zeroline=False,
            title="",
            tickfont=dict(color="#9ca3af"),
        ),
    )
    return fig

# ---------- TOP BAR ----------
st.markdown(
    """
    <div class="cr-topbar">
      <div class="cr-left">
        <div class="cr-logo">₹</div>
        <div>
          <div class="cr-title">CashRaaga</div>
          <div class="cr-tagline">See your cashflow before it happens.</div>
        </div>
      </div>
      <div class="cr-chip">Private, local analysis · No ads</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Outer wrapper
st.markdown('<div class="cr-wrapper">', unsafe_allow_html=True)

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("#### 💰 CashRaaga")
    st.caption("Bank statement → UPI, EMI & savings insights.")
    st.markdown("---")
    st.markdown("**Upload your statement**")

    uploaded_file = st.file_uploader(
        "CSV / Excel from your bank",
        type=["csv", "xlsx", "xls"],
        help="Export from net banking, then upload the CSV/Excel file here.",
    )

    st.markdown("---")
    st.caption("Files are processed in-memory. Close the tab to clear them.")

# ---------- HERO CARD ----------
st.markdown(
    """
    <div class="cr-card" style="margin-bottom:10px;">
      <div class="cr-section-title">Bank statement analyzer</div>
      <div class="cr-section-sub">
        Upload a statement once. CashRaaga shows inflows, spends, UPI flows, EMIs and monthly savings in a simple view.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if uploaded_file is None:
    st.info("Upload a CSV or Excel bank statement in the sidebar to get started.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ---------- READ FILE ----------
try:
    if uploaded_file.name.lower().endswith(".csv"):
        df_raw = pd.read_csv(uploaded_file)
    else:
        df_raw = pd.read_excel(uploaded_file)
except Exception as e:
    st.error(f"Could not read the file. Error: {e}")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

if df_raw.empty:
    st.error("The uploaded file seems to be empty.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

with st.expander("Preview raw data (first 10 rows)"):
    st.dataframe(df_raw.head(10), use_container_width=True)

# ---------- COLUMN MAPPING ----------
st.markdown('<div class="cr-section-title">Step 1 · Map your columns</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="cr-section-sub">Tell CashRaaga which columns contain Date, Description and Amount. Type (CR/DR) is optional.</div>',
    unsafe_allow_html=True,
)

columns = list(df_raw.columns)
col1, col2, col3 = st.columns(3)
with col1:
    date_col = st.selectbox("Date column", options=columns)
with col2:
    desc_col = st.selectbox("Description column", options=columns)
with col3:
    amount_col = st.selectbox("Amount column", options=columns)

use_type_col = st.checkbox(
    "My statement has a separate Credit / Debit type column", value=False
)
type_col = None
type_value_credit = None
type_value_debit = None

if use_type_col:
    type_col = st.selectbox("Type column", options=columns)
    sample_types = df_raw[type_col].dropna().astype(str).str.strip().unique()
    st.caption(f"Detected sample type values: {sample_types[:6]}")
    tc1, tc2 = st.columns(2)
    with tc1:
        type_value_credit = st.text_input("Value meaning CREDIT", value="CR")
    with tc2:
        type_value_debit = st.text_input("Value meaning DEBIT", value="DR")

st.markdown("---")

# ---------- NORMALISATION ----------
df = pd.DataFrame()
df["Date"] = df_raw[date_col]
df["Description"] = df_raw[desc_col].astype(str).fillna("")
df["Amount_raw"] = df_raw[amount_col]
df["Amount"] = pd.to_numeric(df["Amount_raw"], errors="coerce")
df = df.dropna(subset=["Amount"])

if use_type_col and type_col is not None:
    tseries = df_raw[type_col].astype(str).str.upper().str.strip()
    credit_flag = tseries == type_value_credit.strip().upper()
    debit_flag = tseries == type_value_debit.strip().upper()

    if df["Amount"].min() >= 0:
        df["SignedAmount"] = 0.0
        df.loc[credit_flag, "SignedAmount"] = df.loc[credit_flag, "Amount"]
        df.loc[debit_flag, "SignedAmount"] = -df.loc[debit_flag, "Amount"]
    else:
        df["SignedAmount"] = df["Amount"]
else:
    df["SignedAmount"] = df["Amount"]

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Date"])

if df.empty:
    st.error("No valid rows after cleaning. Check your mappings and try again.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ---------- CATEGORISATION ----------
def categorize(description: str) -> str:
    d = str(description).lower()

    if any(k in d for k in ["swiggy", "zomato", "restaurant", "food", "dining"]):
        return "Food & Dining"
    if any(k in d for k in ["amazon", "flipkart", "myntra", "ajio", "meesho"]):
        return "Shopping"
    if "rent" in d:
        return "Rent"
    if any(k in d for k in ["petrol", "fuel", "shell", "hpcl", "bpcl", "indianoil"]):
        return "Fuel & Transport"
    if any(k in d for k in ["recharge", "jio", "airtel", "vi ", "vodafone", "bsnl"]):
        return "Mobile & Internet"
    if any(k in d for k in ["electricity", "eb", "tneb", "gas bill", "power bill"]):
        return "Utilities"
    if any(k in d for k in ["salary", "payroll", "salary credit", "sal "]):
        return "Salary"
    if any(k in d for k in ["emi", "loan", "repayment"]):
        return "Loans & EMI"
    if any(k in d for k in ["hospital", "pharmacy", "medical", "clinic"]):
        return "Health & Medical"
    if any(k in d for k in ["school", "college", "fees", "tuition"]):
        return "Education"
    if any(k in d for k in ["netflix", "hotstar", "prime video", "prime ", "spotify", "wynk"]):
        return "Entertainment & Subscriptions"
    return "Others"

df["Category"] = df["Description"].apply(categorize)

# ---------- AGGREGATES ----------
total_inflow = df.loc[df["SignedAmount"] > 0, "SignedAmount"].sum()
total_outflow = df.loc[df["SignedAmount"] < 0, "SignedAmount"].sum()
savings_total = total_inflow + total_outflow

df["Month"] = df["Date"].dt.strftime("%Y-%m")

monthly_inflow = df[df["SignedAmount"] > 0].groupby("Month")["SignedAmount"].sum()
monthly_outflow = (
    df[df["SignedAmount"] < 0].groupby("Month")["SignedAmount"].sum().abs()
)

all_months = sorted(set(monthly_inflow.index) | set(monthly_outflow.index))
monthly_inflow = monthly_inflow.reindex(all_months, fill_value=0)
monthly_outflow = monthly_outflow.reindex(all_months, fill_value=0)
monthly_savings = monthly_inflow - monthly_outflow

monthly_df = pd.DataFrame(
    {
        "Month": all_months,
        "Total Inflow": monthly_inflow.values,
        "Total Outflow": monthly_outflow.values,
        "Savings": monthly_savings.values,
    }
)
monthly_series = monthly_df.set_index("Month")["Savings"]

# Common views for UPI & EMI
upi_df = df[df["Description"].str.contains("UPI", case=False, na=False)].copy()
emi_mask = df["Description"].str.contains("EMI|LOAN", case=False, na=False)
emi_df = df[(df["SignedAmount"] < 0) & emi_mask].copy()

# ---------- TABS ----------
tab_dash, tab_upi, tab_emi, tab_predict, tab_export = st.tabs(
    ["Overview", "UPI flows", "Loans / EMIs", "Savings forecast", "Download"]
)

# ===== OVERVIEW TAB =====
with tab_dash:
    # --- derive snapshot numbers ---
    if len(monthly_df) > 0:
        current_row = monthly_df.iloc[-1]
        current_month_label = current_row["Month"]
        this_savings = float(current_row["Savings"])
        prev_savings = float(monthly_df.iloc[-2]["Savings"]) if len(monthly_df) > 1 else None

        if prev_savings is not None and prev_savings != 0:
            growth_pct = (this_savings - prev_savings) / abs(prev_savings) * 100
            growth_txt = f"{growth_pct:+.0f}% vs last month"
        else:
            growth_txt = "first month in data"

        if not upi_df.empty:
            upi_current = upi_df[upi_df["Month"] == current_month_label]
            upi_net = upi_current["SignedAmount"].sum()
            upi_net_out = abs(upi_net) if upi_net < 0 else 0
        else:
            upi_net_out = 0

        if not emi_df.empty:
            emi_current = emi_df[emi_df["Month"] == current_month_label]
            emi_load = abs(emi_current["SignedAmount"].sum()) if not emi_current.empty else 0
        else:
            emi_load = 0

        safe_daily = max(this_savings, 0) / 30 if this_savings > 0 else 0
    else:
        this_savings = 0
        growth_txt = "no history"
        upi_net_out = 0
        emi_load = 0
        safe_daily = 0

    snapshot_html = f"""
    <div class="snapshot-wrapper">
      <div class="snapshot-header">
        <div class="snapshot-title">Monthly savings snapshot</div>
      </div>
      <div class="snapshot-cards">
        <div class="snapshot-card">
          <div class="snapshot-label">This month savings</div>
          <div class="snapshot-value">₹{this_savings:,.0f}</div>
          <div class="snapshot-subtext">{growth_txt}</div>
        </div>
        <div class="snapshot-card">
          <div class="snapshot-label">UPI net outflow</div>
          <div class="snapshot-value">₹{upi_net_out:,.0f}</div>
          <div class="snapshot-subtext">Top UPI spends: Swiggy · Amazon · Rent</div>
        </div>
        <div class="snapshot-card">
          <div class="snapshot-label">EMI load</div>
          <div class="snapshot-value">₹{emi_load:,.0f}</div>
          <div class="snapshot-subtext">Current month EMIs and loans</div>
        </div>
      </div>
      <div class="snapshot-ai">
        AI view: <span>you can safely spend ~₹{safe_daily:,.0f}/day for the next 30 days</span>
        &nbsp;based on this month’s savings.
      </div>
    </div>
    """
    st.markdown(snapshot_html, unsafe_allow_html=True)

    # --- Savings bar chart: last few months ---
    last_n = 4
    snapshot_hist = monthly_df.tail(last_n).copy()
    if not snapshot_hist.empty:
        fig_hist = go.Figure()
        fig_hist.add_bar(
            x=snapshot_hist["Month"],
            y=snapshot_hist["Savings"],
        )
        fig_hist = style_dark_bar(fig_hist, height=220)

        st.markdown(
            """
            <div style="font-size:0.8rem;color:#9ca3af;margin-top:2px;margin-bottom:4px;">
              Savings Raaga · last few months
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown(
        '<div class="cr-section-title" style="margin-top:10px;">Recent transactions</div>',
        unsafe_allow_html=True,
    )
    st.caption("Last 10 rows after cleaning.")
    st.dataframe(df.sort_values("Date", ascending=False).head(10), use_container_width=True)

# ===== UPI TAB =====
with tab_upi:
    st.markdown('<div class="cr-section-title">UPI money movement</div>', unsafe_allow_html=True)
    st.caption("Based on descriptions containing 'UPI'.")

    if upi_df.empty:
        st.info("No UPI transactions detected.")
    else:
        upi_in = upi_df[upi_df["SignedAmount"] > 0]["SignedAmount"].sum()
        upi_out = upi_df[upi_df["SignedAmount"] < 0]["SignedAmount"].sum()

        c1, c2, c3 = st.columns(3)
        c1.metric("UPI inflow (₹)", f"{upi_in:,.0f}")
        c2.metric("UPI outflow (₹)", f"{abs(upi_out):,.0f}")
        c3.metric("Net UPI drain (₹)", f"{(upi_in + upi_out):,.0f}")

        upi_top = (
            upi_df.groupby("Description")["SignedAmount"]
            .sum()
            .abs()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )
        upi_top.columns = ["Description", "Total Amount"]

        st.markdown("")
        st.markdown('<div class="cr-section-title">Top UPI counterparties</div>', unsafe_allow_html=True)
        col_chart, col_table = st.columns([2, 1.3])
        with col_chart:
            fig_upi = px.bar(
                upi_top,
                x="Total Amount",
                y="Description",
                orientation="h",
            )
            fig_upi = style_dark_bar(fig_upi, height=280)
            st.plotly_chart(fig_upi, use_container_width=True)
        with col_table:
            st.dataframe(
                upi_top.rename(columns={"Total Amount": "Total Amount (₹)"}),
                use_container_width=True,
            )

# ===== EMI TAB =====
with tab_emi:
    st.markdown('<div class="cr-section-title">Loans & EMIs</div>', unsafe_allow_html=True)
    st.caption("Finds debits with 'EMI' or 'LOAN' in the description.")

    if emi_df.empty:
        st.info("No EMI / loan transactions found.")
    else:
        total_emi_out = emi_df["SignedAmount"].sum()
        emi_monthly = (
            emi_df.groupby("Month")["SignedAmount"]
            .sum()
            .abs()
            .reset_index()
            .rename(columns={"SignedAmount": "Total EMI (₹)"})
        )

        c1, c2 = st.columns(2)
        c1.metric("Total EMI outflow in period (₹)", f"{abs(total_emi_out):,.0f}")
        if not emi_monthly.empty:
            avg_emi = emi_monthly["Total EMI (₹)"].mean()
            c2.metric("Average monthly EMI load (₹)", f"{avg_emi:,.0f}")

        emi_by_desc = (
            emi_df.groupby("Description")["SignedAmount"]
            .sum()
            .abs()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
            .rename(columns={"SignedAmount": "Total EMI (₹)"})
        )

        st.markdown("")
        st.markdown('<div class="cr-section-title">Top EMI sources</div>', unsafe_allow_html=True)
        col_chart, col_table = st.columns([2, 1.3])
        with col_chart:
            fig_emi_desc = px.bar(
                emi_by_desc,
                x="Total EMI (₹)",
                y="Description",
                orientation="h",
            )
            fig_emi_desc = style_dark_bar(fig_emi_desc, height=280)
            st.plotly_chart(fig_emi_desc, use_container_width=True)
        with col_table:
            st.dataframe(emi_by_desc, use_container_width=True)

        st.markdown("")
        st.markdown('<div class="cr-section-title">EMI by month</div>', unsafe_allow_html=True)
        fig_emi_month = px.bar(
            emi_monthly,
            x="Month",
            y="Total EMI (₹)",
        )
        fig_emi_month = style_dark_bar(fig_emi_month, height=260)
        st.plotly_chart(fig_emi_month, use_container_width=True)

# ===== PREDICT TAB =====
with tab_predict:
    st.markdown('<div class="cr-section-title">Savings forecast</div>', unsafe_allow_html=True)
    st.caption("Simple forecast based on past monthly savings (if at least 3 months are available).")

    if len(monthly_series) >= 3:
        try:
            from pmdarima import auto_arima

            model = auto_arima(
                monthly_series,
                seasonal=False,
                error_action="ignore",
                suppress_warnings=True,
            )

            n_future = 3
            forecast = model.predict(n_periods=n_future)
            next_month_pred = float(forecast[0])
            last_month_value = float(monthly_series.iloc[-1])
            delta_vs_last = next_month_pred - last_month_value

            st.metric(
                "Estimated savings next month (₹)",
                f"{next_month_pred:,.0f}",
                delta=f"{delta_vs_last:,.0f} vs last month",
            )

            future_labels = [f"Month +{i+1}" for i in range(n_future)]
            forecast_df = pd.DataFrame({"Month": future_labels, "Predicted Savings": forecast})

            col_chart, col_table = st.columns([2, 1.3])
            with col_chart:
                fig_forecast = go.Figure()
                fig_forecast.add_trace(
                    go.Scatter(
                        x=list(monthly_series.index),
                        y=monthly_series.values,
                        mode="lines+markers",
                        name="History",
                        line=dict(color="#22c55e"),
                    )
                )
                fig_forecast.add_trace(
                    go.Scatter(
                        x=future_labels,
                        y=forecast,
                        mode="lines+markers",
                        name="Forecast",
                        line=dict(color="#a855f7"),
                    )
                )
                fig_forecast.update_layout(
                    height=260,
                    margin=dict(l=10, r=10, t=30, b=0),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(15,23,42,1)",
                    xaxis=dict(tickfont=dict(color="#9ca3af")),
                    yaxis=dict(gridcolor="#0f172a", tickfont=dict(color="#9ca3af")),
                )
                st.plotly_chart(fig_forecast, use_container_width=True)

            with col_table:
                st.dataframe(
                    forecast_df.rename(
                        columns={"Predicted Savings": "Predicted Savings (₹)"}
                    ),
                    use_container_width=True,
                )
        except Exception as e:
            st.warning(f"Forecast not available: {e}")
    else:
        st.info("Upload at least 3 months of data to enable the forecast.")

    st.markdown("")
    st.markdown('<div class="cr-section-title">Monthly savings trend</div>', unsafe_allow_html=True)
    fig_month = px.bar(
        monthly_df,
        x="Month",
        y="Savings",
        labels={"Month": "Month", "Savings": "Savings (₹)"},
    )
    fig_month = style_dark_bar(fig_month, height=260)
    st.plotly_chart(fig_month, use_container_width=True)

    st.dataframe(
        monthly_df.rename(
            columns={
                "Total Inflow": "Total Inflow (₹)",
                "Total Outflow": "Total Outflow (₹)",
                "Savings": "Savings (₹)",
            }
        ),
        use_container_width=True,
    )

# ===== DOWNLOAD TAB =====
with tab_export:
    st.markdown('<div class="cr-section-title">Download analysed data</div>', unsafe_allow_html=True)
    st.caption("Export the cleaned & categorised statement as CSV.")

    if len(df) == 0:
        st.warning("No rows available after processing.")
    else:
        download_df = df[["Date", "Description", "SignedAmount", "Category"]].copy()
        download_df.rename(columns={"SignedAmount": "Amount"}, inplace=True)
        csv_data = download_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name="cashraaga_analysed_statement.csv",
            mime="text/csv",
        )

    st.markdown(
        '<p class="small-note">CashRaaga is an informational tool and does not provide investment, tax or legal advice.</p>',
        unsafe_allow_html=True,
    )

# Close outer wrapper
st.markdown("</div>", unsafe_allow_html=True)
