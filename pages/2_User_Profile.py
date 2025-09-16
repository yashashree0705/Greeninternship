# pages/2_User_Profile.py

import streamlit as st
import pandas as pd
import plotly.express as px

LOG_FILE = "logs.csv"

@st.cache_data
def load_logs():
    try:
        df = pd.read_csv(LOG_FILE)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        return df
    except Exception as e:
        st.error(f"Error loading logs: {e}")
        return pd.DataFrame()

df = load_logs()

st.title("👤 User Profile Dashboard")

if df.empty:
    st.warning("No data available. Please log entries first.")
    st.stop()

# -------------------------
# User Selection
# -------------------------
users = df["user_id"].unique().tolist()
selected_user = st.selectbox("Select User", users)

user_df = df[df["user_id"] == selected_user].sort_values("date")

st.subheader(f"Profile for {selected_user}")

# -------------------------
# Latest Metrics
# -------------------------
latest = user_df.iloc[-1]

col1, col2, col3 = st.columns(3)
col1.metric("Latest kWh", f"{latest['kwh']:.2f}")
col2.metric("Latest Cost (Rs)", f"₹ {latest['cost_rs']:.2f}")
col3.metric("Latest CO₂ (kg)", f"{latest['co2_kg']:.2f}")

# -------------------------
# Trend Over Time
# -------------------------
st.header("Energy Trend Over Time")

fig1 = px.line(
    user_df,
    x="date",
    y="kwh",
    markers=True,
    title=f"Energy Consumption Trend - {selected_user}"
)
st.plotly_chart(fig1, use_container_width=True)

# -------------------------
# Baseline vs Post (if available)
# -------------------------
st.header("⚖Baseline vs Post Comparison")

if "baseline" in user_df["period"].values and "post" in user_df["period"].values:
    baseline = user_df[user_df["period"] == "baseline"].iloc[0]
    post = user_df[user_df["period"] == "post"].iloc[-1]

    col1, col2, col3 = st.columns(3)
    col1.metric("Baseline kWh", f"{baseline['kwh']:.2f}")
    col2.metric("Post kWh", f"{post['kwh']:.2f}")
    change = ((post["kwh"] - baseline["kwh"]) / baseline["kwh"]) * 100
    col3.metric("Change (%)", f"{change:.1f}%")

    compare = pd.DataFrame({
        "Period": ["Baseline", "Post"],
        "kWh": [baseline["kwh"], post["kwh"]],
        "Cost (Rs)": [baseline["cost_rs"], post["cost_rs"]],
        "CO₂ (kg)": [baseline["co2_kg"], post["co2_kg"]]
    })
    fig2 = px.bar(
        compare.melt(id_vars="Period", var_name="Metric", value_name="Value"),
        x="Metric", y="Value", color="Period",
        barmode="group", text_auto=".2f",
        title=f"{selected_user} – Baseline vs Post"
    )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("This user doesn’t have both baseline and post data yet.")

# -------------------------
# Appliance Breakdown
# -------------------------
st.header("Appliance Usage Breakdown")

appliance_cols = ["fan_hours", "light_hours", "ac_hours", "charger_hours", "washing_cycles"]

avg_usage = user_df.groupby("period")[appliance_cols].mean().reset_index()
fig3 = px.bar(
    avg_usage.melt(id_vars="period", var_name="Appliance", value_name="Hours"),
    x="Appliance", y="Hours", color="period",
    barmode="group", text_auto=".2f",
    title=f"Average Appliance Usage - {selected_user}"
)
st.plotly_chart(fig3, use_container_width=True)

# -------------------------
# Personalized Summary
# -------------------------
st.header("Personalized Summary")

if "baseline" in user_df["period"].values and "post" in user_df["period"].values:
    saving_kwh = baseline["kwh"] - post["kwh"]
    saving_cost = baseline["cost_rs"] - post["cost_rs"]
    saving_co2 = baseline["co2_kg"] - post["co2_kg"]

    st.success(
        f"{selected_user} reduced their energy usage by **{saving_kwh:.2f} kWh**, "
        f"saving **₹{saving_cost:.2f}** and cutting **{saving_co2:.2f} kg CO₂** "
        f"since the baseline measurement. 🎉"
    )
else:
    st.info("Savings summary will be available once both baseline and post data are logged.")
