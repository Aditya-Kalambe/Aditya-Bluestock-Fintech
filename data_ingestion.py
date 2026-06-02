import os
import glob
import pandas as pd

RAW_DATA_DIR = "data/raw"

def profile_raw_datasets():
    print("=== STEP 1: PROFILING RAW DATASETS ===")
    csv_files = glob.glob(os.path.join(RAW_DATA_DIR, "*.csv"))[:10]
    
    if not csv_files:
        print("No CSV files found in data/raw/ yet. Run live_nav_fetch.py first!")
        return
        
    for file_path in csv_files:
        print("\n" + "="*50)
        print(f"Dataset: {os.path.basename(file_path)}")
        print("="*50)
        
        try:
            df = pd.read_csv(file_path)
            print(f"Shape: {df.shape}")
            print("\nData Types:")
            print(df.dtypes)
            print("\nHead:")
            print(df.head(2))
            
            # Quick anomaly check
            missing_vals = df.isnull().sum().sum()
            duplicated_rows = df.duplicated().sum()
            if missing_vals > 0 or duplicated_rows > 0:
                print(f"\n⚠️ Anomalies Noted: {missing_vals} missing values, {duplicated_rows} duplicate rows found.")
            else:
                print("\n✅ Structure looks clean at first glance.")
                
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

def explore_fund_master(fund_master_path="data/raw/fund_master.csv"):
    print("\n=== STEP 2: FUND MASTER EXPLORATION ===")
    if not os.path.exists(fund_master_path):
        print(f"[{fund_master_path}] not found. Skipping dynamic exploration blueprint.")
        return None
        
    df = pd.read_csv(fund_master_path)
    
    # Expected columns boilerplate mapping
    cols = {c.lower(): c for c in df.columns}
    house_col = cols.get("fund_house") or cols.get("amc_name") or df.columns[0]
    cat_col = cols.get("category") or df.columns[1]
    sub_cat_col = cols.get("sub_category") or cols.get("sub_cat") or df.columns[2]
    risk_col = cols.get("risk_grade") or cols.get("riskometer") or df.columns[3]

    print(f"Unique Fund Houses: {df[house_col].nunique()}")
    print(f"Unique Categories: {df[cat_col].nunique()}")
    print(f"Unique Sub-Categories: {df[sub_cat_col].nunique()}")
    if risk_col in df.columns:
        print(f"Risk Grades: {df[risk_col].unique()}")
        
    print("\n💡 AMFI Scheme Code Structure Note:")
    print("AMFI codes are unique 6-digit identifiers assigned to mutual fund schemes in India.")
    return df

def validate_amfi_codes(fund_master_df, nav_history_path="data/raw/nav_history.csv"):
    print("\n=== STEP 3: AMFI CODE VALIDATION ===")
    if fund_master_df is None or not os.path.exists(nav_history_path):
        print("Skipping code validation: fund_master or nav_history files missing.")
        return
        
    nav_df = pd.read_csv(nav_history_path)
    
    # Look for amfi/scheme code columns
    master_codes = set(fund_master_df.iloc[:, 0].astype(str).unique())
    nav_codes = set(nav_df["scheme_code"].astype(str).unique())
    
    missing_in_nav = master_codes - nav_codes
    
    print("--- DATA QUALITY SUMMARY ---")
    if not missing_in_nav:
        print("✅ Validation Success: Every AMFI code in fund_master exists in nav_history.")
    else:
        print(f"❌ Validation Alert: {len(missing_in_nav)} codes from fund_master are missing in nav_history.")
        print(f"Sample missing codes: {list(missing_in_nav)[:5]}")

if __name__ == "__main__":
    profile_raw_datasets()
    # To execute steps 2 & 3 fully, place your local master/history files in data/raw/
    fm_df = explore_fund_master()
    validate_amfi_codes(fm_df)