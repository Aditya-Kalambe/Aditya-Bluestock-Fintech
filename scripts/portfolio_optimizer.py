import sqlite3
import os
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = os.path.join(BASE_DIR, "data", "db", "bluestock_mf.db")

def load_historical_returns():
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT n.nav_date, m.scheme_name, n.nav 
        FROM nav_history n
        JOIN fund_master m ON n.scheme_code = m.scheme_code
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Pivot to create a clean time-series matrix of price indices
    pivot_df = df.pivot(index="nav_date", columns="scheme_name", values="nav").sort_index()
    
    # Compute standard financial log returns
    return np.log(pivot_df / pivot_df.shift(1)).dropna()

def optimize_portfolio():
    returns_df = load_historical_returns()
    num_assets = len(returns_df.columns)
    
    # Calculate annualized mean returns and covariance matrix (252 trading days)
    ann_returns = returns_df.mean() * 252
    cov_matrix = returns_df.cov() * 252
    risk_free_rate = 0.065  # Set at standard 6.5% standard baseline
    
    def portfolio_stats(weights):
        weights = np.array(weights)
        p_return = np.sum(ann_returns * weights)
        p_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe_ratio = (p_return - risk_free_rate) / p_volatility
        return p_return, p_volatility, sharpe_ratio

    # Define objective function to minimize negative Sharpe Ratio
    def min_neg_sharpe(weights):
        return -portfolio_stats(weights)[2]

    # Portfolio optimization parameters: Weights must sum up exactly to 1.0 (100%)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0, 1) for _ in range(num_assets))
    initial_weights = num_assets * [1. / num_assets]

    # Run Sequential Least Squares Programming (SLSQP)
    result = minimize(min_neg_sharpe, initial_weights, method='SLSQP', bounds=bounds, constraints=constraints)
    
    if not result.success:
        raise BaseException("Optimization execution sequence failed.")
        
    optimal_weights = result.x
    p_ret, p_vol, p_sharpe = portfolio_stats(optimal_weights)
    
    print("\n🎯 === MARKOWITZ EFFICIENT FRONTIER OPTIMIZATION ===")
    print(f"Optimal Portfolio Return: {p_ret:.2%}")
    print(f"Optimal Portfolio Risk (Volatility): {p_vol:.2%}")
    print(f"Maximized Sharpe Ratio: {p_sharpe:.4f}\n")
    print("--- Target Asset Allocations ---")
    
    allocation_summary = []
    for asset, weight in zip(returns_df.columns, optimal_weights):
        if weight > 0.001:  # Filter out trivial residual weights
            print(f"- {asset}: {weight:.2%}")
            allocation_summary.append({"Fund": asset, "Weight": f"{weight:.2%}"})
            
    return allocation_summary, p_ret, p_vol, p_sharpe

if __name__ == "__main__":
    optimize_portfolio()