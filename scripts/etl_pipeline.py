import os
import glob
import pandas as pd
import sqlite3
from pathlib import Path

# Absolute/Relative path safety (Avoids hardcoding)
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
DB_DIR = os.path.join(BASE_DIR, "data", "db")
SQL_DIR = os.path.join(BASE_DIR, "sql")

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(DB_DIR, exist_ok=True)

DB_PATH = os.path.join(DB_DIR, "bluestock_mf.db")
SCHEMA_PATH = os.path.join(SQL_DIR, "schema.sql")

def init_database():
    """Initializes the SQLite schema using the schema.sql template."""
    print("Initializing Database with Schema...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    with open(SCHEMA_PATH, "r") as f:
        cursor.executescript(f.read())
    conn.commit()
    conn.close()
    print("Database schema built successfully.")

def build_mock_fund_master():
    """Fallback generator for fund_master if it wasn't provided locally."""
    master_file = os.path.join(RAW_DIR, "fund_master.csv")
    if not os.path.exists(master_file):
        print("Generating a reference fund_master.csv template...")
        data = {
            "scheme_code": [125497, 119551, 120503, 118632, 119092, 120841],
            "fund_house": ["HDFC Mutual Fund", "SBI Mutual Fund", "ICICI Prudential MF", "Nippon India MF", "Axis Mutual Fund", "Kotak Mutual Fund"],
            "category": ["Equity", "Equity", "Equity", "Equity", "Equity", "Equity"],
            "sub_category": ["Large Cap", "Large Cap", "Large Cap", "Large Cap", "Large Cap", "Large Cap"],
            "scheme_name": ["HDFC Top 100 Direct", "SBI Bluechip", "ICICI Bluechip", "Nippon Large Cap", "Axis Bluechip", "Kotak Bluechip"],
            "risk_grade": ["Very High", "Very High", "Very High", "Very High", "Very High", "Very High"],
            "aum_crore": [32450.50, 41200.20, 52110.80, 24600.15, 31900.40, 18450.90]
        }
        pd.DataFrame(data).to_csv(master_file, index=False)

def transform_and_load_nav():
    """Transforms raw NAV history files, tracking and filling gaps seamlessly."""
    nav_files = glob.glob(os.path.join(RAW_DIR, "*_nav.csv"))
    if not nav_files:
        print("No raw NAV data found. Run live_nav_fetch.py first!")
        return

    conn = sqlite3.connect(DB_PATH)
    all_processed_data = []

    for file in nav_files:
        print(f"Processing time-series transformations for: {os.path.basename(file)}")
        df = pd.read_csv(file)
        
        # Format columns cleanly
        df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")
        df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
        df["scheme_code"] = df["scheme_code"].astype(int)
        
        # Sort values ascending to support chronological forward fills
        df = df.sort_values("date").set_index("date")
        
        # Capture context metrics before modifications
        scheme_code = int(df["scheme_code"].iloc[0])
        
        # Remedy Weekend/Holiday gaps using chronological reindexing
        full_date_range = pd.date_range(start=df.index.min(), end=df.index.max(), freq="D")
        
        # Tag entries before filling to trace data quality lineage
        df_clean = df.reindex(full_date_range)
        df_clean["is_forward_filled"] = df_clean["nav"].isna().astype(int)
        
        # Forward fill empty values across gaps
        df_clean["nav"] = df_clean["nav"].ffill()
        df_clean["scheme_code"] = df_clean["scheme_code"].ffill().astype(int)
        
        # Re-extract date as clean string format
        df_clean = df_clean.reset_index().rename(columns={"index": "nav_date"})
        df_clean["nav_date"] = df_clean["nav_date"].dt.strftime("%Y-%m-%d")
        
        # Select target columns mapping to DB schema
        db_ready_df = df_clean[["scheme_code", "nav_date", "nav", "is_forward_filled"]]
        all_processed_data.append(db_ready_df)
        
        # Append target to local staging area
        processed_file_path = os.path.join(PROCESSED_DIR, f"cleaned_{os.path.basename(file)}")
        df_clean.to_csv(processed_file_path, index=False)

    # Concat and load into SQLite
    if all_processed_data:
        final_nav_df = pd.concat(all_processed_data, ignore_index=True)
        final_nav_df.to_sql("nav_history", conn, if_exists="append", index=False)
        print(f"Loaded {len(final_nav_df)} rows into table 'nav_history'.")

    # Load Fund Master
    master_path = os.path.join(RAW_DIR, "fund_master.csv")
    if os.path.exists(master_path):
        master_df = pd.read_csv(master_path)
        master_df.to_sql("fund_master", conn, if_exists="append", index=False)
        print(f"Loaded {len(master_df)} records into table 'fund_master'.")

    conn.close()
    print("ETL pipeline executed completely without manual steps.")

if __name__ == "__main__":
    init_database()
    build_mock_fund_master()
    transform_and_load_nav()