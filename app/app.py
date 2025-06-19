import pandas as pd
import numpy as np
import streamlit as st

def run_forecast(kpis_df: pd.DataFrame, assumptions: dict, nbm_targets: dict) -> pd.DataFrame:
    base = kpis_df.pivot(index="metric_name", columns="window", values="value")
    ttm = base.get("TTM")
    if ttm is None:
        st.error("TTM values required in KPI csv")
        return pd.DataFrame()

    effective = ttm.combine_first(pd.Series(assumptions))

    conv_chain = (
        effective.get("conversion_MQL_to_NBM", 0) *
        effective.get("conversion_NBM_to_Deal", 0) *
        effective.get("conversion_Deal_to_Won", 0) *
        effective.get("win_rate", 0) *
        effective.get("NBM_show_rate", 0)
    )

    acv = effective.get("ACV", 0)
    lag = np.array(assumptions.get("lag_matrix", [1.0]))

    outputs = []
    for period, nbm in nbm_targets.items():
        wins = nbm * conv_chain
        arr = wins * acv
        for i, weight in enumerate(lag):
            month = pd.Period(period, "M") + i
            outputs.append({"month": month.to_timestamp(), "ARR": arr * weight})

    df = pd.DataFrame(outputs)
    df = df.groupby("month", as_index=False)["ARR"].sum()
    return df

st.title("Lite Forecast App")

st.header("1. Upload KPI CSV")
kpi_file = st.file_uploader("KPI CSV", type="csv")
if kpi_file:
    kpis_df = pd.read_csv(kpi_file)
else:
    st.info("Using sample KPI data")
    kpis_df = pd.read_csv("sample_kpi.csv")

st.dataframe(kpis_df)

st.header("2. Enter Assumption Overrides")
assumptions = {}
for metric in [
    "conversion_MQL_to_NBM",
    "conversion_NBM_to_Deal",
    "conversion_Deal_to_Won",
    "win_rate",
    "NBM_show_rate",
    "ACV",
]:
    if metric in kpis_df.metric_name.values:
        default = float(kpis_df.loc[kpis_df.metric_name == metric, "value"].iloc[0])
    else:
        default = 0.0
    val = st.number_input(metric, value=default)
    assumptions[metric] = val

lag_matrix = st.text_input("Lag matrix (comma separated weights, len=12)", "1.0")
assumptions["lag_matrix"] = [float(x) for x in lag_matrix.split(',')]

st.header("3. NBM Targets")
nbm_file = st.file_uploader("NBM target CSV", type="csv", key="nbm")
if nbm_file:
    nbm_df = pd.read_csv(nbm_file)
else:
    st.info("Using sample NBM data")
    nbm_df = pd.read_csv("sample_nbm.csv")

st.dataframe(nbm_df)
nbm_targets = dict(zip(nbm_df['month'], nbm_df['NBM']))

if st.button("Run forecast"):
    output_df = run_forecast(kpis_df, assumptions, nbm_targets)
    st.subheader("ARR Forecast")
    st.dataframe(output_df)
    st.line_chart(output_df.set_index('month'))
    csv = output_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "forecast.csv", "text/csv")
