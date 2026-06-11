#!/bin/bash
# ============================================================================
# BLUESTOCK MF PLATFORM — SYSTEM PRODUCTION DEPLOYMENT & EXECUTION PIPELINE
# ============================================================================

set -e # Terminate script execution immediately if any sub-command records an error
export RUN_ENV="PRODUCTION"

clear
echo "========================================================================="
echo "⚙️  Initializing Bluestock Mutual Fund Analytics Platform Production Build"
echo "========================================================================="
echo "⏱️  Deployment Timestamp: $(date)"

# Step 1: Audit and verify environmental workspace requirements
echo -e "\n📁 Step 1: Auditing system directory paths..."
mkdir -p data/raw data/processed data/db sql reports/charts scripts notebooks

# Step 2: Validate the python package dependencies distribution matrix
echo -e "\n📦 Step 2: Syncing system runtime package arrays..."
pip install -q numpy pandas matplotlib seaborn scipy sqlalchemy plotly kaleido

# Step 3: Run the core ETL data cleaning and pipeline ingestion module
echo -e "\n🧼 Step 3: Executing End-to-End Ingestion Engine (etl_pipeline.py)..."
if [ -f "scripts/etl_pipeline.py" ]; then
    python scripts/etl_pipeline.py
else
    echo "❌ Error: etl_pipeline.py not located inside the scripts directory."
    exit 1
fi

# Step 4: Run the quantitative performance risk calculation metrics model
echo -e "\n📈 Step 4: Computing portfolio performance scorecards (compute_metrics.py)..."
if [ -f "scripts/compute_metrics.py" ]; then
    python scripts/compute_metrics.py
else
    echo "❌ Error: compute_metrics.py not located inside the scripts directory."
    exit 1
fi

# Step 5: Execute advanced tail-risk and investor cohort analytics
echo -e "\n🧬 Step 5: Running advanced risk & continuity analyses (advanced_analytics.py)..."
if [ -f "scripts/advanced_analytics.py" ]; then
    python scripts/advanced_analytics.py
else
    echo "❌ Error: advanced_analytics.py not located inside the scripts directory."
    exit 1
fi

# Step 6: Verify output integrity across the target processing directories
echo -e "\n🔍 Step 6: Executing final pipeline asset validation audits..."
REQUIRED_ASSETS=(
    "data/db/bluestock_mf.db"
    "data/processed/fund_scorecard.csv"
    "data/processed/var_cvar_report.csv"
    "reports/charts/benchmark_comparison_chart.png"
    "reports/charts/rolling_sharpe_chart.png"
)

for asset in "${REQUIRED_ASSETS[@]}"; do
    if [ -f "$asset" ]; then
        echo "  ✅ Production verification successful: $asset located."
    else
        echo "  ❌ Critical Failure: Production output asset $asset is missing."
        exit 1
    fi
done

echo -e "\n========================================================================="
echo "🏆 Platform Deployment Completed Successfully. System Status: ACTIVE"
echo "========================================================================="