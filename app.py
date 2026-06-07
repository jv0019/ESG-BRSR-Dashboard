import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Cement ESG Dashboard (BRSR)", layout="wide")
st.title("🏭 Cement Sector ESG Performance Dashboard")
st.markdown("BRSR Principle 6 – Environmental Stewardship | Peer comparison & standard compliance")

# ---- Load data ----
df_all = pd.read_csv("data/cement_brsr_sample.csv")
df_all = df_all.sort_values(["Company", "Year"])

# ---- Helper: Calculate intensity columns ----
def add_intensities(df):
    df = df.copy()
    df["Scope1_intensity"] = df["Scope1_emissions_tCO2"] / df["Cementitious_production_tonnes"]
    df["Scope2_intensity"] = df["Scope2_emissions_tCO2"] / df["Cementitious_production_tonnes"]
    df["Energy_intensity_GJ_t"] = df["Total_energy_GJ"] / df["Cementitious_production_tonnes"]
    df["Water_intensity_KL_t"] = df["Freshwater_withdrawal_KL"] / df["Cementitious_production_tonnes"]
    # Headline: Combined Scope 1+2 intensity (GHG Protocol / BRSR focus)
    df["Total_emissions_intensity"] = (df["Scope1_emissions_tCO2"] + df["Scope2_emissions_tCO2"]) / df["Cementitious_production_tonnes"]
    return df

df_all = add_intensities(df_all)

# ---- Standard thresholds (illustrative targets) ----
STANDARDS = {
    "Total_emissions_intensity": 0.58,   # tCO₂/tonne (combined)
    "Scope1_intensity": 0.50,            # tCO₂/tonne
    "Scope2_intensity": 0.08,            # tCO₂/tonne
    "Energy_intensity": 3.0,             # GJ/tonne
    "Water_recycling_rate": 40,          # %
    "Renewable_energy_share": 30,        # %
    "AFR_rate": 15                       # % (Alternative Fuel & Raw materials)
}

# ---- Sidebar Controls ----
st.sidebar.header("⚙️ Dashboard Controls")

# Peer comparison toggle
enable_peer = st.sidebar.checkbox("Enable Peer Comparison", value=False)
if enable_peer:
    companies = st.sidebar.multiselect(
        "Select companies to compare",
        options=df_all["Company"].unique(),
        default=["UltraTech", "ACC"]
    )
else:
    company_single = st.sidebar.selectbox("Select company", df_all["Company"].unique(), index=0)
    companies = [company_single]

# Standards toggle
show_standards = st.sidebar.checkbox("Show Standard Thresholds", value=True)

# Metric selector
metric_options = {
    "Scope 1 Emissions (tCO₂)": ("Scope1_emissions_tCO2", "absolute"),
    "Scope 2 Emissions (tCO₂)": ("Scope2_emissions_tCO2", "absolute"),
    "Total Energy Consumption (GJ)": ("Total_energy_GJ", "absolute"),
    "Freshwater Withdrawal (KL)": ("Freshwater_withdrawal_KL", "absolute"),
    "Water Recycling Rate (%)": ("Water_recycling_rate_pct", "percent"),
    "Renewable Energy Share (%)": ("Renewable_energy_share_pct", "percent"),
    "AFR Usage (%)": ("Waste_used_as_AFR_pct", "percent"),
    "NOx Emissions (tonnes)": ("NOx_tonnes", "absolute"),
    "SOx Emissions (tonnes)": ("SOx_tonnes", "absolute"),
    "PM Emissions (tonnes)": ("PM_tonnes", "absolute"),
    "Scope 1 Intensity (tCO₂/t)": ("Scope1_intensity", "intensity"),
    "Scope 2 Intensity (tCO₂/t)": ("Scope2_intensity", "intensity"),
    "Total Emissions Intensity (tCO₂/t)": ("Total_emissions_intensity", "intensity"),   # NEW HEADLINE
    "Energy Intensity (GJ/t)": ("Energy_intensity_GJ_t", "intensity"),
    "Water Intensity (KL/t)": ("Water_intensity_KL_t", "intensity"),
}
selected_metric_label = st.sidebar.selectbox("Primary Metric", list(metric_options.keys()), index=12)  # default to Total Emissions Intensity
selected_col, metric_type = metric_options[selected_metric_label]

# Filter data by selected companies
df = df_all[df_all["Company"].isin(companies)].copy()

# Determine standard threshold for the selected metric
standard_val = None
if show_standards:
    std_map = {
        "Total_emissions_intensity": "Total_emissions_intensity",
        "Scope1_intensity": "Scope1_intensity",
        "Scope2_intensity": "Scope2_intensity",
        "Energy_intensity_GJ_t": "Energy_intensity",
        "Water_recycling_rate_pct": "Water_recycling_rate",
        "Renewable_energy_share_pct": "Renewable_energy_share",
        "Waste_used_as_AFR_pct": "AFR_rate",
    }
    std_key = std_map.get(selected_col)
    if std_key:
        standard_val = STANDARDS[std_key]

# ---- KPI Cards (primary company, latest year) ----
st.subheader("📊 Key Performance Indicators (Latest Year)")
primary_company = "UltraTech" if "UltraTech" in companies else companies[0]
latest_row = df[(df["Company"] == primary_company) & (df["Year"] == df["Year"].max())]
if not latest_row.empty:
    latest = latest_row.iloc[0]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total GHG Intensity", f"{latest['Total_emissions_intensity']:.3f} tCO₂/t",
                delta=f"Std: {STANDARDS['Total_emissions_intensity']:.2f}" if show_standards else None)
    col2.metric("Scope 1 Intensity", f"{latest['Scope1_intensity']:.3f} tCO₂/t",
                delta=f"Std: {STANDARDS['Scope1_intensity']:.2f}" if show_standards else None)
    col3.metric("Scope 2 Intensity", f"{latest['Scope2_intensity']:.3f} tCO₂/t",
                delta=f"Std: {STANDARDS['Scope2_intensity']:.2f}" if show_standards else None)
    col4.metric("Energy Intensity", f"{latest['Energy_intensity_GJ_t']:.2f} GJ/t",
                delta=f"Std: {STANDARDS['Energy_intensity']:.1f}" if show_standards else None)

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Water Recycling", f"{latest['Water_recycling_rate_pct']}%",
                delta=f"Std: {STANDARDS['Water_recycling_rate']}%" if show_standards else None)
    col6.metric("Renewable Energy", f"{latest['Renewable_energy_share_pct']}%",
                delta=f"Std: {STANDARDS['Renewable_energy_share']}%" if show_standards else None)
    col7.metric("AFR Usage", f"{latest['Waste_used_as_AFR_pct']}%",
                delta=f"Std: {STANDARDS['AFR_rate']}%" if show_standards else None)
    col8.metric("Water Intensity", f"{latest['Water_intensity_KL_t']:.4f} KL/t")

# ---- Main Trend Chart ----
st.subheader(f"📈 {selected_metric_label} Over Time")
fig = px.line(df, x="Year", y=selected_col, color="Company", markers=True,
              title=selected_metric_label)
if show_standards and standard_val is not None:
    fig.add_hline(y=standard_val, line_dash="dash", line_color="red",
                  annotation_text=f"Standard: {standard_val}", annotation_position="top right")
fig.update_layout(title_x=0.5)
st.plotly_chart(fig, use_container_width=True)

# ---- Compliance Gauge (if standard defined) ----
if show_standards and standard_val is not None:
    st.subheader("✅ Standard Compliance Status (Latest Year)")
    colg1, colg2 = st.columns(2)
    # Determine if lower is better for the selected metric
    better_if_lower_cols = [
        "Scope1_emissions_tCO2", "Scope2_emissions_tCO2", "Total_energy_GJ",
        "Freshwater_withdrawal_KL", "NOx_tonnes", "SOx_tonnes", "PM_tonnes",
        "Scope1_intensity", "Scope2_intensity", "Total_emissions_intensity",
        "Energy_intensity_GJ_t", "Water_intensity_KL_t"
    ]
    is_lower_better = selected_col in better_if_lower_cols

    for idx, comp in enumerate(companies):
        comp_data = df[(df["Company"] == comp) & (df["Year"] == df["Year"].max())]
        if comp_data.empty:
            continue
        current_val = comp_data.iloc[0][selected_col]
        if is_lower_better:
            compliant = current_val <= standard_val
            status = "✅ Below/at threshold" if compliant else "❌ Exceeds threshold"
        else:
            compliant = current_val >= standard_val
            status = "✅ Above/at target" if compliant else "❌ Below target"
        color = "green" if compliant else "red"
        with colg1 if idx % 2 == 0 else colg2:
            st.markdown(f"**{comp}**: {current_val:.3f}")
            st.markdown(f"Standard: {standard_val}")
            st.markdown(f'<span style="color:{color}; font-weight:bold;">{status}</span>', unsafe_allow_html=True)

# ---- Peer Comparison: Total GHG Intensity (headline) ----
if enable_peer and len(companies) > 1:
    st.subheader("🔍 Peer Comparison – Total GHG Intensity (tCO₂/tonne)")
    latest_year = df["Year"].max()
    peer_df = df[df["Year"] == latest_year]
    fig_peer = px.bar(peer_df, x="Company", y="Total_emissions_intensity", color="Company",
                      text_auto=".3f", title=f"Total Scope 1+2 Intensity ({latest_year})")
    fig_peer.update_layout(title_x=0.5, showlegend=False)
    st.plotly_chart(fig_peer, use_container_width=True)

# ---- Raw Data (expandable) ----
with st.expander("📋 View Raw Data"):
    st.dataframe(df, use_container_width=True)

st.caption("Data source: Simulated BRSR disclosures based on public cement sector reports. Replace with extracted PDF data for actual analysis.")