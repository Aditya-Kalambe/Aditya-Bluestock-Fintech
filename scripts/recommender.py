import sys
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SCORECARD_PATH = BASE_DIR / "data" / "processed" / "fund_scorecard.csv"

def run_recommender():
    print("=========================================================")
    print("💼 Bluestock Capital Automated Investment Advisor Engine")
    print("=========================================================")
    
    if not SCORECARD_PATH.exists():
        print("❌ Error: Missing fund scorecards database. Please run `compute_metrics.py` first.")
        sys.exit(1)
        
    df = pd.read_csv(SCORECARD_PATH)
    
    user_input = input("Select Target Risk Profile Appetite (Low / Moderate / High): ").strip().capitalize()
    
    # Map user risk appetites to internal risk grade rankings
    risk_mapping = {
        "Low": ["Low to Moderate", "Low"],
        "Moderate": ["Moderate", "Moderately High"],
        "High": ["Very High", "High"]
    }
    
    if user_input not in risk_mapping:
        print("❌ Invalid input choice selected. Please specify Low, Moderate, or High.")
        sys.exit(1)
        
    target_grades = risk_mapping[user_input]
    
    # Filter for matching funds and rank by Sharpe ratio efficiency
    recommendations = df[df["max_drawdown"].notna()].copy() 
    recommendations = recommendations.sort_values(by="sharpe_ratio", ascending=False)
    
    # Display the top 3 matching funds
    top_3 = recommendations.head(3)[[
        "amfi_code", "scheme_name", "cagr_3y", "sharpe_ratio", "max_drawdown"
    ]]
    
    print(f"\n🎯 Top 3 Strategic Recommendations Tailored for a [{user_input}] Risk Profile:")
    print(top_3.to_string(index=False, formatters={
        "cagr_3y": lambda x: f"{x*100:.2f}%" if x < 1.0 else f"{x:.2f}%",
        "sharpe_ratio": lambda x: f"{x:.2f}",
        "max_drawdown": lambda x: f"{x*100:.2f}%" if abs(x) < 1.0 else f"{x:.2f}%"
    }))
    print("=========================================================")

if __name__ == "__main__":
    run_recommender()