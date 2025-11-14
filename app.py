import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="CashRaaga – See Your Cashflow Before It Happens",
    page_icon="💰",
    layout="wide"
)

# ================== GLOBAL STYLE ==================
st.markdown(
    """
    <style>
    /* Base background + font */
    body {
        background: radial-gradient(circle at top, #020617 0, #020617 40%, #000 100%);
    }
    .stApp {
        background: radial-gradient(circle at top, #020617 0, #020617 40%, #000 100%);
        color: #e5e7eb;
    }
    .main-block {
        background: rgba(15,23,42,0.98);
        border-radius: 18px;
        padding: 18px 22px 20px;
        border: 1px solid rgba(31,41,55,0.9);
        box-shadow: 0 18px 45px rgba(15,23,42,0.90);
    }
    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        margin-bottom: 0.3rem;
    }
    .hero-highlight {
        background: linear-gradient(120deg,#22c55e,#a3e635);
        -webkit-background-clip: text;
        color: transparent;
    }
    .hero-sub {
        font-size: 0.95rem;
        color: #9ca3af;
        max-width: 620px;
    }
    .hero-pill-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 10px;
        margin-bottom: 10px;
    }
    .hero-pill {
        font-size: 0.72rem;
        padding: 4px 10px;
        border-radius: 999px;
        border: 1px solid rgba(148,163,184,0.4);
        background: rgba(15,23,42,0.9);
        color: #d1d5db;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .section-header {
        font-size: 1rem;
        font-weight: 600;
        margin-top: 0.25rem;
        margin-bottom: 0.15rem;
    }
    .small-note {
        font-size: 0.8rem;
        color: #9ca3af;
    }
    .metric-card > div {
        background: rgba(15,23,42,0.95) !important;
        border-radius: 14px !important;
        border: 1px solid rgba(31,41,55,0.9);
        padding: 12px !important;
    }
    /* Reduce tab label padding */
    .stTabs [role="tablist"] > div {
        gap: 12px;
    }
    .stTabs [role="tab"] {
        padding: 6px 12px;
        border-radius: 999px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ================== SIDEBAR ==================
with st.sidebar:
    st.markdown("### 💰 CashRaaga")
    st.caption("See your cashflow before it happens.")
    st.markdown("---")
    st.markdown("**Upload your statement**")

    uploaded_file = st.file_uploader(
        "CSV / Excel from your bank",
        type=["csv", "xlsx", "xls"],
        help="Export from net banking, open in Excel if needed, and save as CSV/Excel."
    )

    st.markdown("---")
    st.caption("Runs only on your data · No login · No ads.")

# ================== HERO HEADER ==================
st.markdown(
    """
    <div class="main-block">
      <div class="hero-title">
        CashRaaga · <span class="hero-highlight">personal cashflow radar</span>
      </div>
      <p class="hero-sub">
        Upload a single bank statement and CashRaaga breaks it into spends, UPI flows, EMIs and savings –
        then shows what your next few months might look like.
      </p>
      <div class="hero-pill-row">
        <div class="hero-pill">⚡ Works with CSV / Excel exports</div>
        <div class="hero-pill">🔎 Auto-categorised spends & UPI flows</div>
        <div class="hero-pill">📅 EMI & savings trend by month</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)
st.write("")  # spacing

if uploaded_file is None:
    st.info("⬅ Upload a CSV or Excel bank statement in the sidebar to get started.")
    st.stop()

# ================== READ FILE ==================
try:
    if uploaded_file.name.lower().endswith(".csv"):
        df_raw = pd.read_csv(uploaded_file)
    else:
        df_raw = pd.read_excel(uploaded_file)
except Exception as e:
    st.error(f"Could not read the file. Error: {e}")
    st.stop()

if df_raw.empty:
    st.error("The uploaded file seems to be empty.")
    st.stop()

with st.expander("🔍 Preview raw data"):
    st.dataframe(df_raw.head())

# ================== STEP 1: COLUMN MAPPING ==================
st.markdown("<div class='section-header'>Step 1 · Map your columns</div>", unsafe_allow_html=True)
st.caption("Tell CashRaaga which columns contain the date, description and amount. Type (CR/DR) is optional.")

columns = list(df_raw.columns)

col1, col2, col3 = st.columns(3)
with col1:
    date_col = st.selectbox("Date column", options=columns)
with col2:
    desc_col = st.selectbox("Description column", options=columns)
with col3:
    amount_col = st.selectbox("Amount column", options=columns)

use_type_col = st.checkbox("My statement has a Credit / Debit type column (CR / DR etc.)", value=False)
type_col = None
type_value_credit = None
type_value_debit = None

if use_type_col:
    type_col = st.selectbox("Type column", options=columns)
    sample_types = df_raw[type_col].dropna().astype(str).str.strip().unique()
    st.caption(f"Detected type values (sample): {sample_types[:6]}")
    tc1, tc2 = st.columns(2)
    with tc1:
        type_value_credit = st.text_input("Value meaning CREDIT", value="CR")
    with tc2:
        type_value_debit = st.text_input("Value meaning DEBIT", value="DR")

# ================== STEP 2: NORMALISATION ==================
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
    st.error("No valid rows left after cleaning. Check your column mapping and file format.")
    st.stop()

# ================== CATEGORISATION ==================
def categorize(description: str) -> str:
    desc = str(description).lower()

    if any(k in desc for k in ["swiggy", "zomato", "restaurant", "food", "dining"]):
        return "Food & Dining"
    if any(k in desc for k in ["amazon", "flipkart", "myntra", "ajio", "meesho"]):
        return "Shopping"
    if "rent" in desc:
        return "Rent"
    if any(k in desc for k in ["petrol", "fuel", "shell", "hpcl", "bpcl", "indianoil"]):
        return "Fuel & Transport"
    if any(k in desc for k in ["recharge", "jio", "airtel", "vi ", "vodafone", "bsnl"]):
        return "Mobile & Internet"
    if any(k in desc for k in ["electricity", "eb", "tneb", "gas bill", "power bill"]):
        return "Utilities"
    if any(k in desc for k in ["salary", "payroll", "salary credit", "sal "]):
        return "Salary"
    if any(k in desc for k in ["emi", "loan", "repayment"]):
        return "Loans & EMI"
    if any(k in desc for k in ["hospital", "pharmacy", "medical", "clinic"]):
        return "Health & Medical"
    if any(k in desc for k in ["school", "college", "fees", "tuition"]):
        return "Education"
    if any(k in desc for k in ["netflix", "hotstar", "prime video", "prime ", "spotify", "wynk"]):
        return "Entertainment & Subscriptions"
    return "Others"

df["Category"] = df["Description"].apply(categorize)

total_inflow = df.loc[df["SignedAmount"] > 0, "SignedAmount"].sum()
total_outflow = df.loc[df["SignedAmount"] < 0, "SignedAmount"].sum()
savings_total = total_inflow + total_outflow

df["Month"] = df["Date"].dt.strftime("%Y-%m")
monthly_inflow = df[df["SignedAmount"] > 0].groupby("Month")["SignedAmount"].sum()
monthly_outflow = df[df["SignedAmount"] < 0].groupby("Month")["SignedAmount"].sum().abs()

all_months = sorted(set(monthly_inflow.index) | set(monthly_outflow.index))
monthly_inflow = monthly_inflow.reindex(all_months, fill_value=0)
monthly_outflow = monthly_outflow.reindex(all_months, fill_value=0)
monthly_savings = monthly_inflow - monthly_outflow

monthly_df = pd.DataFrame({
    "Month": all_months,
    "Total Inflow": monthly_inflow.values,
    "Total Outflow": monthly_outflow.values,
    "Savings": monthly_savings.values
})
monthly_series = monthly_df.set_index("Month")["Savings"]

# ================== TABS ==================
tab_dash, tab_flow, tab_emi, tab_predict, tab_export = st.tabs(
    ["Dashboard", "RaagaFlow (UPI)", "RaagaEMI (Loans)", "RaagaPredict", "Download"]
)

# ----- DASHBOARD -----
with tab_dash:
    st.markdown("<div class='section-header'>Summary for this statement</div>", unsafe_allow_html=True)
    st.caption("High-level view of how much came in, how much went out, and what you actually kept as savings.")

    mc1, mc2, mc3 = st.columns(3)
    with mc1:
        with st.container():
            st.metric("Total Inflow (Rs)", f"{total_inflow:,.0f}")
    with mc2:
        with st.container():
            st.metric("Total Outflow (Rs)", f"{abs(total_outflow):,.0f}")
    with mc3:
        with st.container():
            st.metric("Savings (Rs)", f"{savings_total:,.0f}")

    st.markdown("<div class='section-header'>Recent transactions</div>", unsafe_allow_html=True)
    st.caption("Last 10 rows after cleaning and normalisation.")
    st.dataframe(df.sort_values("Date", ascending=False).head(10), use_container_width=True)

    st.markdown("<div class='section-header'>Spending by category</div>", unsafe_allow_html=True)
    debits = df[df["SignedAmount"] < 0].copy()
    spend_by_cat = debits.groupby("Category")["SignedAmount"].sum().sort_values()
    if spend_by_cat.empty:
        st.info("No debit transactions detected based on current mapping.")
    else:
        spend_display = spend_by_cat.abs().reset_index()
        spend_display.columns = ["Category", "Total Spent"]
        col_chart, col_table = st.columns([2, 1.3])
        with col_chart:
            fig_cat = px.pie(
                spend_display,
                names="Category",
                values="Total Spent",
                hole=0.45,
                title="Spending by Category"
            )
            st.plotly_chart(fig_cat, use_container_width=True)
        with col_table:
            st.dataframe(
                spend_display.rename(columns={"Total Spent": "Total Spent (Rs)"}),
                use_container_width=True
            )

# ----- RaagaFlow (UPI) -----
with tab_flow:
    st.markdown("<div class='section-header'>RaagaFlow · UPI money movement</div>", unsafe_allow_html=True)
    st.caption("Shows money in and out through UPI based on description patterns.")

    upi_df = df[df["Description"].str.contains("UPI", case=False, na=False)].copy()

    if upi_df.empty:
        st.info("No UPI transactions detected in this statement (based on 'UPI' keyword in description).")
    else:
        upi_in = upi_df[upi_df["SignedAmount"] > 0]["SignedAmount"].sum()
        upi_out = upi_df[upi_df["SignedAmount"] < 0]["SignedAmount"].sum()

        c1, c2, c3 = st.columns(3)
        c1.metric("UPI Inflow (Rs)", f"{upi_in:,.0f}")
        c2.metric("UPI Outflow (Rs)", f"{abs(upi_out):,.0f}")
        c3.metric("Net UPI Drain (Rs)", f"{(upi_in + upi_out):,.0f}")

        upi_top = (
            upi_df.groupby("Description")["SignedAmount"]
            .sum()
            .abs()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )
        upi_top.columns = ["Description", "Total Amount"]

        st.markdown("<div class='section-header'>Top UPI counterparties</div>", unsafe_allow_html=True)
        col_chart, col_table = st.columns([2, 1.3])
        with col_chart:
            fig_upi = px.bar(
                upi_top,
                x="Total Amount",
                y="Description",
                orientation="h",
                title="Top UPI counterparties",
            )
            st.plotly_chart(fig_upi, use_container_width=True)
        with col_table:
            st.dataframe(
                upi_top.rename(columns={"Total Amount": "Total Amount (Rs)"}),
                use_container_width=True
            )

# ----- RaagaEMI -----
with tab_emi:
    st.markdown("<div class='section-header'>RaagaEMI · Loans and EMIs</div>", unsafe_allow_html=True)
    st.caption("Detects EMI-style debits using simple description rules (EMI / LOAN etc.).")

    emi_mask = df["Description"].str.contains("EMI|LOAN", case=False, na=False)
    emi_df = df[(df["SignedAmount"] < 0) & emi_mask].copy()

    if emi_df.empty:
        st.info("No obvious EMI / loan transactions found (searching for 'EMI' or 'LOAN' in description).")
    else:
        total_emi_out = emi_df["SignedAmount"].sum()
        emi_monthly = (
            emi_df.groupby("Month")["SignedAmount"]
            .sum()
            .abs()
            .reset_index()
            .rename(columns={"SignedAmount": "Total EMI (Rs)"})
        )

        c1, c2 = st.columns(2)
        c1.metric("Total EMI Outflow in period (Rs)", f"{abs(total_emi_out):,.0f}")
        if not emi_monthly.empty:
            avg_emi = emi_monthly["Total EMI (Rs)"].mean()
            c2.metric("Average monthly EMI load (Rs)", f"{avg_emi:,.0f}")

        emi_by_desc = (
            emi_df.groupby("Description")["SignedAmount"]
            .sum()
            .abs()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
            .rename(columns={"SignedAmount": "Total EMI (Rs)"})
        )

        st.markdown("<div class='section-header'>Top EMI sources</div>", unsafe_allow_html=True)
        col_chart, col_table = st.columns([2, 1.3])
        with col_chart:
            fig_emi_desc = px.bar(
                emi_by_desc,
                x="Total EMI (Rs)",
                y="Description",
                orientation="h",
                title="Top EMI debits by description"
            )
            st.plotly_chart(fig_emi_desc, use_container_width=True)
        with col_table:
            st.dataframe(emi_by_desc, use_container_width=True)

        st.markdown("<div class='section-header'>EMI load by month</div>", unsafe_allow_html=True)
        fig_emi_month = px.bar(
            emi_monthly,
            x="Month",
            y="Total EMI (Rs)",
            title="Monthly EMI outflow"
        )
        st.plotly_chart(fig_emi_month, use_container_width=True)

# ----- RaagaPredict -----
with tab_predict:
    st.markdown("<div class='section-header'>RaagaPredict · Future savings view</div>", unsafe_allow_html=True)
    st.caption("Uses your past monthly savings pattern to estimate the next few months.")

    if len(monthly_series) >= 3:
        try:
            from pmdarima import auto_arima

            model = auto_arima(
                monthly_series,
                seasonal=False,
                error_action="ignore",
                suppress_warnings=True
            )

            n_future = 3
            forecast = model.predict(n_periods=n_future)
            next_month_pred = float(forecast[0])
            last_month_value = float(monthly_series.iloc[-1])
            delta_vs_last = next_month_pred - last_month_value

            st.metric(
                "Estimated savings next month (Rs)",
                f"{next_month_pred:,.0f}",
                delta=f"{delta_vs_last:,.0f} vs last month"
            )

            future_labels = [f"Month +{i+1}" for i in range(n_future)]
            forecast_df = pd.DataFrame(
                {"Month": future_labels, "Predicted Savings": forecast}
            )

            col_chart, col_table = st.columns([2, 1.3])
            with col_chart:
                fig_forecast = go.Figure()
                fig_forecast.add_trace(go.Scatter(
                    x=list(monthly_series.index),
                    y=monthly_series.values,
                    mode="lines+markers",
                    name="Historical savings"
                ))
                fig_forecast.add_trace(go.Scatter(
                    x=future_labels,
                    y=forecast,
                    mode="lines+markers",
                    name="Forecast"
                ))
                fig_forecast.update_layout(title="Savings: history and short-term forecast")
                st.plotly_chart(fig_forecast, use_container_width=True)

            with col_table:
                st.dataframe(
                    forecast_df.rename(
                        columns={"Predicted Savings": "Predicted Savings (Rs)"}
                    ),
                    use_container_width=True
                )

        except Exception as e:
            st.warning(f"Forecast not available: {e}")
    else:
        st.info("Upload at least 3 months of data to enable the savings forecast.")

    st.markdown("<div class='section-header'>Monthly savings trend</div>", unsafe_allow_html=True)
    fig_month = px.bar(
        monthly_df,
        x="Month",
        y="Savings",
        title="Monthly Savings",
        labels={"Month": "Month", "Savings": "Savings (Rs)"}
    )
    st.plotly_chart(fig_month, use_container_width=True)

    st.dataframe(
        monthly_df.rename(
            columns={
                "Total Inflow": "Total Inflow (Rs)",
                "Total Outflow": "Total Outflow (Rs)",
                "Savings": "Savings (Rs)"
            }
        ),
        use_container_width=True
    )

# ----- DOWNLOAD -----
with tab_export:
    st.markdown("<div class='section-header'>Download analysed data</div>", unsafe_allow_html=True)
    st.caption("Export the cleaned & categorised statement for your own records.")

    if len(df) == 0:
        st.warning("No rows available after processing. Check column mapping and amount/type settings above.")
    else:
        download_df = df[["Date", "Description", "SignedAmount", "Category"]].copy()
        download_df.rename(columns={"SignedAmount": "Amount"}, inplace=True)
        csv_data = download_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download analysed data as CSV",
            data=csv_data,
            file_name="cashraaga_analysed_statement.csv",
            mime="text/csv"
        )

    st.markdown(
        "<p class='small-note'>CashRaaga is an informational tool and does not provide investment, tax or legal advice.</p>",
        unsafe_allow_html=True
    )
