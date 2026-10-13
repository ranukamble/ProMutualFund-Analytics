# 📈 Mutual Fund Portfolio Analyzer & Builder

A stunning, highly responsive web application designed for exploring, analyzing, and building mutual fund portfolios using live data from the Indian stock market. Built with a focus on premium aesthetics and real-time data accuracy.

## ✨ Key Features

- **Live Market Data:** Fetches real-time NAV, AUM, Expense Ratios, Fund Managers, and Exit Loads for thousands of Indian mutual funds.
- **Interactive Visualizations:** Beautiful, highly responsive line charts and donut charts built with Chart.js to visualize historical performance and portfolio allocations.
- **Advanced Portfolio Builder:** 
  - Mix and match multiple funds.
  - Dynamically allocate weights via SIP or Lumpsum.
  - Automatically calculates Risk Profiles, Expected Returns, and generates visual allocations.
- **Smart Analytics:** Calculates annualized returns (CAGR), period highs/lows, volatility, and provides a Scatter Plot (Risk vs. Return) for deep analysis.
- **AI Integration (Optional):** Supports Cohere AI API keys for intelligent, automated portfolio generation.
- **Premium UI/UX:**
  - Glassmorphism design system.
  - Full seamless toggle between **Dark Mode** and **Light Mode**.
  - Micro-interactions, magnetic buttons, and smooth CSS animations.
- **Export to PDF:** Download clean, formatted PDF reports of your built portfolios.

## 🛠️ Technology Stack

**Backend:**
- **Python 3.x**
- **Flask** (Web Framework)
- **mftool** (For fetching official AMFI mutual fund data)
- **BeautifulSoup4 / requests** (For live-scraping additional fund metrics like Expense Ratio & AUM from Groww)
- **Pandas & NumPy** (For data structuring and calculation)

**Frontend:**
- **HTML5 & Vanilla CSS3** (No heavy CSS frameworks, highly customized token-based design system)
- **Vanilla JavaScript** (For dynamic DOM manipulation and state management)
- **Chart.js** (For rendering complex, interactive canvas charts)

## 🚀 How to Run Locally

### 1. Prerequisites
Ensure you have Python 3.8+ installed on your machine.

### 2. Install Dependencies
Navigate to the project folder in your terminal and install the required packages:

```bash
pip install -r requirements.txt
```

*The `requirements.txt` includes:*
- `Flask==3.0.3`
- `mftool==2.5`
- `requests==2.31.0`
- `beautifulsoup4==4.12.3`
- `gunicorn==21.2.0`
- `pandas`
- `numpy`
- `cohere`
- `matplotlib`

### 3. Start the Server
Run the Flask application:

```bash
python app.py
```

### 4. Open in Browser
Visit the following URL in your web browser:
`http://127.0.0.1:5000`

## ☁️ Deployment

This project is fully configured for production deployment on platforms like **Railway**, **Render**, or **Heroku**. 
It uses `gunicorn` as the production WSGI server. 

To deploy on Railway:
1. Ensure the Railway CLI is installed.
2. Run `railway up -d`.

---
*Disclaimer: This tool is for informational and educational purposes only. Always consult with a registered financial advisor before making investment decisions.*
