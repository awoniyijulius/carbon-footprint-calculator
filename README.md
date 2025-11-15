# 🌍 Carbon Footprint Calculator

An interactive web app built with **Streamlit** to estimate your annual carbon footprint across transport, electricity, diet, and shopping.  
It features sustainability‑themed visuals, local options for Nigeria, history tracking, downloads, and suggestions for greener living.

---

## ✨ Features
- 🚗 Transport: car, flights, bus
- ⚡ Electricity: country‑specific grid factors (Nigeria, global average, or custom)
- 🥩 Diet: beef and chicken consumption
- 🛒 Shopping: monthly spend in USD or NGN
- 📊 Interactive charts with Plotly
- 💡 Suggestions for reducing emissions
- 📜 History tracking and CSV downloads
- 🌱 Sustainability‑themed background and sidebar styling

---

## 🛠️ Requirements
The app depends on:
- `streamlit`
- `plotly`
- `pandas`

These are listed in `requirements.txt`.

---

## 🚀 Run Locally
Clone the repo and install dependencies:

```bash
git clone https://github.com/awoniyijulius/carbon-footprint-calculator.git
cd carbon-footprint-calculator
pip install -r requirements.txt
streamlit run app.py
