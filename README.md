# 🌍 Carbon Footprint Calculator

## ℹ️ About this Project

This Carbon Footprint Calculator is designed as an **educational and awareness tool** for individuals.  
It helps users estimate their annual carbon footprint across transport, electricity, diet, and shopping, and provides suggestions for greener living.

⚠️ Important note:  
This app is **not a formal sustainability reporting framework** (such as GRI, SASB, CDP, or the GHG Protocol).  
Instead, it is **inspired by the United Nations Sustainable Development Goals (UN SDGs)** and aims to make climate awareness accessible at the personal level.

The goal is to encourage individuals to take **first steps toward climate action**, complementing — but not replacing — organizational reporting standards.


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
