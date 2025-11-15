# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import json
from datetime import datetime

# -------------------------------
# App config
# -------------------------------
st.set_page_config(page_title="Carbon Footprint Calculator", page_icon="🌍", layout="wide")

# -------------------------------
# Background image (sustainability) and initial CSS
# -------------------------------
BACKGROUND_IMAGE_URL = "https://images.unsplash.com/photo-1469474968028-56623f02e42e"  # forest canopy

# Enhanced CSS: readable sidebar widgets, visible radio/select text, main cards, overlay
custom_css_base = """
<style>
/* Background + overlay */
[data-testid="stAppViewContainer"] {
    background:
        linear-gradient(rgba(20, 60, 30, 0.42), rgba(20, 60, 30, 0.42)),
        url("{BG}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}

/* Keep header transparent */
[data-testid="stHeader"] { background: rgba(0,0,0,0); }

/* Sidebar card + readable text */
[data-testid="stSidebar"] {
    /* Deep green sidebar background for a sustainability look */
    background: linear-gradient(180deg, #064e2a 0%, #0b6623 100%);
    border-right: 1px solid rgba(0,0,0,0.06);
    color: #e6ffe6;
}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: #e6ffe6 !important;
    font-weight: 800 !important;
    font-size: 20px !important;
}

/* Make form labels, radio/checkbox text, select option text, and input labels visible */
[data-testid="stSidebar"] .stRadio,
[data-testid="stSidebar"] .stCheckbox,
[data-testid="stSidebar"] .stSelectbox,
[data-testid="stSidebar"] .stNumberInput,
[data-testid="stSidebar"] .widget-label,
[data-testid="stSidebar"] label {
    color: #e6ffe6 !important;
    opacity: 1 !important;
}

/* Force radio option text & markers visibility */
[data-testid="stSidebar"] .stRadio > div > label,
[data-testid="stSidebar"] .stRadio > div > div,
[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stNumberInput label {
    color: #e6ffe6 !important;
}

/* Make form controls (checkboxes/radios/toggles) clearly visible on dark green */
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] input[type="checkbox"],
[data-testid="stSidebar"] input[type="radio"] {
    /* modern browsers support accent-color to change the check/radio color */
    accent-color: #a5f3a5 !important;
}

/* Ensure svg icons (toggle glyphs) are light-colored */
[data-testid="stSidebar"] svg {
    fill: #e6ffe6 !important;
    color: #e6ffe6 !important;
}

/* Disabled/hover states */
[data-testid="stSidebar"] .stRadio input:disabled + label,
[data-testid="stSidebar"] .stSelectbox option:disabled {
    color: rgba(230,255,230,0.6) !important;
}

/* Main card readability */
.main-card {
    background: rgba(255,255,255,0.96);
    padding: 1.25rem;
    border-radius: 12px;
    border: 1px solid #c8e6c9;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
    margin-bottom: 1rem;
}

h1, h2, h3 { color: #1b5e20; }
</style>
""".replace("{BG}", BACKGROUND_IMAGE_URL)
st.markdown(custom_css_base, unsafe_allow_html=True)

# High contrast support (toggle overrides)
if "high_contrast" not in st.session_state:
    st.session_state.high_contrast = False

def apply_contrast_css(enabled: bool):
    if not enabled:
        return
    st.markdown("""
    <style>
    :root { --hc-bg: #0c0c0c; --hc-card: #121212; --hc-text: #e6ffe6; --hc-accent: #00c853; }
    [data-testid="stAppViewContainer"] { background: var(--hc-bg) !important; }
    .main-card { background: var(--hc-card) !important; border-color: var(--hc-accent) !important; }
    h1, h2, h3, p, span, div, label { color: var(--hc-text) !important; }
    [data-testid="stSidebar"] { background: #1a1a1a !important; }
    </style>
    """, unsafe_allow_html=True)

# -------------------------------
# Title
# -------------------------------
st.title("🌍 Carbon Footprint Calculator")
st.caption("Interactive visuals, local options, history, downloads, and inline help for every input.")

# -------------------------------
# Emission factors (kg CO₂e per unit)
# -------------------------------
EMISSION_FACTORS = {
    "mile_driven": 0.404,     # kg CO2e/mile
    "km_driven": 0.251,       # kg CO2e/km (approx)
    "beef_kg": 27.0,          # kg CO2e/kg
    "chicken_kg": 6.9,        # kg CO2e/kg
    "flight_km": 0.115,       # kg CO2e/pax-km
    "bus_km": 0.089,          # kg CO2e/pax-km
    "shopping_usd": 0.6       # kg CO2e/USD (lifecycle proxy)
}

COUNTRY_GRID_FACTORS = {
    "Global average": 0.92,
    "Nigeria": 0.80,
    "Custom…": None
}

# -------------------------------
# Sidebar inputs with tooltips
# -------------------------------
st.sidebar.header("Your inputs")

# Units pane (radio options ensured visible by CSS)
st.sidebar.subheader("Units")
distance_unit = st.sidebar.radio(
    "Distance unit",
    ["km", "miles"],
    index=0,
    help="Choose whether you prefer kilometers or miles for distance inputs."
)
currency = st.sidebar.radio(
    "Currency",
    ["NGN", "USD"],
    index=0,
    help="Select the currency you use for shopping/spend inputs."
)

# Transport
st.sidebar.subheader("Transport")
# Ensure both distance variables exist regardless of selected unit (prevents later unbound checks)
miles_per_week = 0.0
km_per_week = 0.0
if distance_unit == "miles":
    miles_per_week = st.sidebar.number_input(
        "🚗 Car distance per week (miles)",
        min_value=0.0, value=50.0, step=1.0,
        help="Total miles driven per week for all trips (commute, errands, etc.)."
    )
    car_per_week_kg = miles_per_week * EMISSION_FACTORS["mile_driven"]
else:
    km_per_week = st.sidebar.number_input(
        "🚗 Car distance per week (km)",
        min_value=0.0, value=80.0, step=1.0,
        help="Total kilometers driven per week for all trips (commute, errands, etc.)."
    )
    car_per_week_kg = km_per_week * EMISSION_FACTORS["km_driven"]

flight_km_per_year = st.sidebar.number_input(
    "✈️ Flight distance per year (km, economy)",
    min_value=0.0, value=1000.0, step=100.0,
    help="Sum of all flown distances per year (round-trip equivalents). Use economy class."
)

bus_km_per_week = st.sidebar.number_input(
    "🚌 Bus distance per week (km)",
    min_value=0.0, value=10.0, step=1.0,
    help="Total kilometers traveled by bus per week (daily commute included)."
)

# Electricity localization
st.sidebar.subheader("Electricity")
country_choice = st.sidebar.selectbox(
    "Grid emission factor",
    list(COUNTRY_GRID_FACTORS.keys()),
    help="Choose a preset kg CO₂e per kWh or select Custom to enter a local value."
)
if country_choice == "Custom…":
    selected_grid_factor = st.sidebar.number_input(
        "Custom grid factor (kg CO₂e/kWh)",
        min_value=0.0, value=0.60, step=0.01,
        help="Enter a locally sourced grid intensity value in kg CO₂e per kWh."
    )
else:
    selected_grid_factor = COUNTRY_GRID_FACTORS[country_choice]

kwh_per_month = st.sidebar.number_input(
    "⚡ Electricity per month (kWh)",
    min_value=0.0, value=150.0, step=1.0,
    help="Average household electricity consumption per month in kWh."
)

# Diet
st.sidebar.subheader("Diet")
beef_kg_per_week = st.sidebar.number_input(
    "🥩 Beef per week (kg)",
    min_value=0.0, value=0.3, step=0.1,
    help="Kilograms of beef consumed per week. Enter 0 if none."
)
chicken_kg_per_week = st.sidebar.number_input(
    "🍗 Chicken per week (kg)",
    min_value=0.0, value=0.5, step=0.1,
    help="Kilograms of chicken consumed per week."
)

# Shopping
st.sidebar.subheader("Shopping")
if currency == "USD":
    spend_usd = st.sidebar.number_input(
        "🛒 Spend per month (USD)",
        min_value=0.0, value=100.0, step=10.0,
        help="Average monthly spend on general goods in USD (proxy for product lifecycle emissions)."
    )
else:
    ngn_per_month = st.sidebar.number_input(
        "🛒 Spend per month (NGN)",
        min_value=0.0, value=150000.0, step=5000.0,
        help="Average monthly spend on general goods in NGN."
    )
    fx_rate = st.sidebar.number_input(
        "FX rate (NGN per USD)",
        min_value=1.0, value=1500.0, step=10.0,
        help="Exchange rate used to convert NGN to USD for emissions proxy."
    )
    spend_usd = ngn_per_month / fx_rate

# Accessibility and theme controls
st.sidebar.subheader("Accessibility")
st.session_state.high_contrast = st.sidebar.checkbox(
    "High contrast mode",
    value=st.session_state.high_contrast,
    help="Toggle a high-contrast theme for improved readability."
)
apply_contrast_css(st.session_state.high_contrast)

st.sidebar.subheader("Theme")
overlay_opacity = st.sidebar.slider(
    "Background overlay opacity",
    0.20, 0.60, 0.42, 0.01,
    help="Adjust how strong the dark green overlay is on the background image for readability."
)
# Apply overlay opacity live
overlay_css = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background:
        linear-gradient(rgba(20, 60, 30, {overlay_opacity}), rgba(20, 60, 30, {overlay_opacity})),
        url("{BACKGROUND_IMAGE_URL}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}}
</style>
"""
st.markdown(overlay_css, unsafe_allow_html=True)

# -------------------------------
# Calculations
# -------------------------------
transport_total = (
    car_per_week_kg * 52 +
    flight_km_per_year * EMISSION_FACTORS["flight_km"] +
    bus_km_per_week * 52 * EMISSION_FACTORS["bus_km"]
)

electricity_total = kwh_per_month * 12 * selected_grid_factor

diet_total = (
    beef_kg_per_week * 52 * EMISSION_FACTORS["beef_kg"] +
    chicken_kg_per_week * 52 * EMISSION_FACTORS["chicken_kg"]
)

shopping_total = spend_usd * 12 * EMISSION_FACTORS["shopping_usd"]

grand_total_kg = transport_total + electricity_total + diet_total + shopping_total
grand_total_t = grand_total_kg / 1000

# -------------------------------
# Outputs (summary with inline explanation)
# -------------------------------
with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("Summary")
    st.success(f"Estimated annual footprint: {grand_total_kg:,.0f} kg CO₂e ({grand_total_t:.2f} tonnes)")
    st.caption("Annual tonnes reflect an approximate estimate based on the inputs and global-average proxies. Local factors, appliance efficiency, and product lifecycles can change results.")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Daily", f"{grand_total_kg/365:.2f} kg CO₂e")
    col2.metric("Weekly", f"{grand_total_kg/52:.2f} kg CO₂e")
    col3.metric("Monthly", f"{grand_total_kg/12:.2f} kg CO₂e")
    col4.metric("Annual", f"{grand_total_kg:.0f} kg CO₂e")
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------
# Breakdown chart
# -------------------------------
with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("🌱 Breakdown by category")
    breakdown_df = pd.DataFrame({
        "Category": ["Transport", "Electricity", "Diet", "Shopping"],
        "Annual kg CO₂e": [transport_total, electricity_total, diet_total, shopping_total]
    })
    fig = px.bar(
        breakdown_df,
        x="Category", y="Annual kg CO₂e",
        color="Category", text="Annual kg CO₂e",
        title="Carbon footprint by category"
    )
    fig.update_traces(texttemplate="%{text:.0f}", textposition="outside")
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#1b5e20"),
        legend_title_text=""
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------
# History (SQLite) and downloads
# -------------------------------
DB_PATH = "footprint_history.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            inputs_json TEXT,
            totals_json TEXT
        )
    """)
    conn.commit()
    return conn

def save_run(inputs: dict, totals: dict):
    conn = init_db()
    conn.execute(
        "INSERT INTO runs (timestamp, inputs_json, totals_json) VALUES (?, ?, ?)",
        (datetime.utcnow().isoformat(), json.dumps(inputs), json.dumps(totals))
    )
    conn.commit()
    conn.close()

def load_runs():
    conn = init_db()
    df = pd.read_sql_query("SELECT * FROM runs ORDER BY id DESC", conn)
    conn.close()
    return df

inputs_payload = {
    "distance_unit": distance_unit,
    "car_per_week_kg": car_per_week_kg,
    "flight_km_per_year": flight_km_per_year,
    "bus_km_per_week": bus_km_per_week,
    "grid_factor_choice": country_choice,
    "selected_grid_factor": selected_grid_factor,
    "kwh_per_month": kwh_per_month,
    "beef_kg_per_week": beef_kg_per_week,
    "chicken_kg_per_week": chicken_kg_per_week,
    "currency": currency,
    "spend_usd": spend_usd,
}
totals_payload = {
    "transport_total": transport_total,
    "electricity_total": electricity_total,
    "diet_total": diet_total,
    "shopping_total": shopping_total,
    "grand_total_kg": grand_total_kg,
    "grand_total_t": grand_total_t,
}

with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("💾 Save & Download")
    c1, c2 = st.columns(2)
    if c1.button("Save this run"):
        save_run(inputs_payload, totals_payload)
        st.success("Saved to local history.")
    result_df = pd.DataFrame([{
        "Transport_kg": transport_total,
        "Electricity_kg": electricity_total,
        "Diet_kg": diet_total,
        "Shopping_kg": shopping_total,
        "Annual_kg": grand_total_kg,
        "Annual_tonnes": grand_total_t,
        "Daily_kg": grand_total_kg/365,
        "Weekly_kg": grand_total_kg/52,
        "Monthly_kg": grand_total_kg/12
    }])
    c2.download_button("Download results (CSV)", data=result_df.to_csv(index=False), file_name="footprint_results.csv", mime="text/csv")
    st.download_button("Download results (JSON)", data=json.dumps({"inputs": inputs_payload, "totals": totals_payload}, indent=2),
                       file_name="footprint_results.json", mime="application/json")
    st.markdown('</div>', unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("📈 History")
    history_df = load_runs()
    if not history_df.empty:
        parsed = []
        for _, row in history_df.iterrows():
            totals = json.loads(row["totals_json"])
            parsed.append({
                "timestamp": row["timestamp"],
                "annual_kg": totals["grand_total_kg"],
                "transport_kg": totals["transport_total"],
                "electricity_kg": totals["electricity_total"],
                "diet_kg": totals["diet_total"],
                "shopping_kg": totals["shopping_total"]
            })
        hist_df = pd.DataFrame(parsed)
        st.dataframe(hist_df, use_container_width=True)
        line = px.line(hist_df.sort_values("timestamp"), x="timestamp", y="annual_kg", markers=True,
                       title="Annual footprint over time")
        line.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#1b5e20"))
        st.plotly_chart(line, use_container_width=True)
    else:
        st.info("No history yet. Save a run to start tracking trends.")
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------
# Suggestions
# -------------------------------
with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("💡 Suggestions")
    suggestions = []
    if beef_kg_per_week > 0.5:
        suggestions.append("Reduce beef intake or swap with chicken/plant-based options.")
    # Determine thresholds in original distance units for recommendation
    if distance_unit == "miles":
        if miles_per_week > 100:
            suggestions.append("Combine trips, carpool, or consider public transport for some journeys.")
    else:
        if km_per_week > 160:
            suggestions.append("Combine trips, carpool, or consider public transport for some journeys.")
    if kwh_per_month > 200:
        suggestions.append("Improve home efficiency: LED bulbs, efficient appliances, and switch off standby loads.")
    if flight_km_per_year > 3000:
        suggestions.append("Consider train alternatives for short-haul or offset essential flights.")
    if not suggestions:
        suggestions.append("Nice balance of activities — keep tracking to find small improvements.")
    for s in suggestions:
        st.write(f"- {s}")
    st.markdown('</div>', unsafe_allow_html=True)
