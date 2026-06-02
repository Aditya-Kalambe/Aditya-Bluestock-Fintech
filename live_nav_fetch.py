import os
import requests
import pandas as pd

RAW_DATA_DIR = "data/raw"
os.makedirs(RAW_DATA_DIR, exist_ok=True)

# Scheme codes mapping
schemes = {
    "125497": "hdfc_top_100_direct",
    "119551": "sbi_bluechip",
    "120503": "icici_bluechip",
    "118632": "nippon_large_cap",
    "119092": "axis_bluechip",
    "120841": "kotak_bluechip"
}

def fetch_and_save_nav(scheme_code, scheme_name):
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    print(f"Fetching data for {scheme_name} ({scheme_code})...")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extract NAV history
        if "data" in data and data["data"]:
            df = pd.DataFrame(data["data"])
            df["scheme_code"] = scheme_code
            df["scheme_name"] = data.get("meta", {}).get("scheme_name", scheme_name)
            
            # Save to CSV
            output_path = os.path.join(RAW_DATA_DIR, f"{scheme_name}_nav.csv")
            df.to_csv(output_path, index=False)
            print(f"Saved to {output_path}")
        else:
            print(f"Warning: No data found for code {scheme_code}")
            
    except Exception as e:
        print(f"Failed to fetch {scheme_code}: {e}")

if __name__ == "__main__":
    for code, name in schemes.items():
        fetch_and_save_nav(code, name)