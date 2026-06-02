import time
import datetime
import os
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
FETCH_SCRIPT = os.path.join(BASE_DIR, "scripts", "live_nav_fetch.py")
ETL_SCRIPT = os.path.join(BASE_DIR, "scripts", "etl_pipeline.py")

print("⏰ Core Ingestion Cron Automation Daemon Engine Started successfully...")
print("Monitoring execution queue for targeted scheduling rules: Weekdays at 8:00 PM.")

while True:
    now = datetime.datetime.now()
    # Rule constraints: Monday=0 through Friday=4
    if now.weekday() < 5:
        if now.hour == 20 and now.minute == 0:
            print(f"🎯 Execution Target Hit: {now}. Deploying live NAV data pipelines...")
            try:
                subprocess.run(["python", FETCH_SCRIPT], check=True)
                subprocess.run(["python", ETL_SCRIPT], check=True)
                print("✅ Weekday pipeline ingestion cycle finished successfully.")
            except Exception as e:
                print(f"❌ Pipeline automated error hit: {e}")
            
            # Sleep 65 seconds to comfortably push past the 20:00 trigger target window
            time.sleep(65)
            
    # Polling frequency baseline check interval
    time.sleep(30)