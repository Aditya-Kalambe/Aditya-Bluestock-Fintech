# Bluestock Mutual Fund Analytics & Performance Platform

An institutional-grade data engineering and quantitative risk analytics ecosystem. This platform handles unstructured historical mutual fund time-series valuations and complex operational investor ledgers, transforming them into an optimized Kimball Star Schema architecture inside an analytical SQLite engine.

---

## 🚀 1. Key System Architectural Milestones
* **Time-Series Gap Remediation:** Programmatically processed daily historical values across 40 distinct fund tracks, applying vectorized forward-fill patches (`.ffill()`) to resolve holiday and weekend timeline gaps.
* **Risk-Adjusted Performance Scoring:** Engineered specialized mathematical pipelines calculating annualized multi-horizon CAGR, Sharpe and Sortino ratios, and CAPM alpha/beta coefficients via Ordinary Least Squares linear regressions.
* **Tail-Risk Vulnerability Identification:** Implemented advanced downside risk parameters, tracking historical Value at Risk (**95%** VaR) and Conditional Value at Risk (**95%** CVaR) alongside sector Herfindahl-Hirschman Indices (HHI).
* **Model Design Automation:** Scripted the entire relational star schema deployment and custom DAX currency-measure injections natively using Tabular Editor 2.28 Advanced C# scripting vectors.

---

## 📦 2. Source Dataset Ledger Specifications

The platform pipeline ingests and cleans the following operational raw data tracking tables:
* `nav_history.csv`: Fragmented time-series log entries containing daily Net Asset Value pricing benchmarks.
* `investor_transactions.csv`: High-volume operational ledger tracking user ID fields, localized geographic transaction states, compliance status vectors, and transaction execution formats.
* `scheme_performance.csv`: Performance tracking metrics detailing historical multi-year returns paired with structural AMC operating cost dimensions (Expense Ratios).
* `portfolio_holdings.csv`: Portfolio asset mapping indices showing sector allocation percentage weights for equity configurations.

---

## ⚙️ 3. Installation, Environment Setup & Deployment

### Step 1: Clone the Platform Repository Workspace
```bash
git clone [https://github.com/your-username/Aditya-Bluestock-Fintech.git](https://github.com/your-username/Aditya-Bluestock-Fintech.git)
cd Aditya-Bluestock-Fintech