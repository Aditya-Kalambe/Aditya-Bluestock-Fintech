# Bluestock Mutual Fund Platform — Production Data Dictionary

## 1. Dimension Tables

### `dim_fund`
Main entity descriptor map for mutual fund assets under analysis.
*Source Reference: fund_master.csv / scheme_performance.csv*

| Column Name | Data Type | Key Constraints | Business Definition |
| :--- | :--- | :--- | :--- |
| `fund_key` | INTEGER | PRIMARY KEY (Auto) | Internal surrogate sequence tracking. |
| `amfi_code` | INTEGER | UNIQUE INDEX | Unique 6-digit reference allocated by AMFI India. |
| `scheme_name`| TEXT | Not Null | Complete official market name of asset scheme. |
| `fund_house` | TEXT | Not Null | Asset Management Company (AMC) managing portfolio. |
| `category` | TEXT | Not Null | Primary asset structure classification (e.g., Equity).|
| `sub_category`| TEXT | Not Null | Specific mandate sub-slice (e.g., Large Cap, Mid Cap).|
| `risk_grade` | TEXT | Not Null | Regulatory risk classification flag. |

### `dim_date`
Converts complex standard timestamps into clean structured business horizons.
*Source Reference: Generated Programmatically*

| Column Name | Data Type | Key Constraints | Business Definition |
| :--- | :--- | :--- | :--- |
| `date_key` | TEXT | PRIMARY KEY | Standard ISO-8601 date string (`YYYY-MM-DD`). |
| `calendar_year`| INTEGER | Not Null | Calendar year component value. |
| `calendar_month`| INTEGER| Not Null | Numerical month sequence positioning (1–12). |
| `month_name` | TEXT | Not Null | Alphabetical month identity representation. |
| `day_of_week` | TEXT | Not Null | String weekday name assignment. |
| `is_weekend` | INTEGER | Check (0, 1) | Binary flag indicating if date falls on a weekend. |

---

## 2. Fact Tables

### `fact_nav`
Time-series tracking historical daily movements of underlying fund valuations.
*Source Reference: nav_history.csv*

| Column Name | Data Type | Key Constraints | Business Definition |
| :--- | :--- | :--- | :--- |
| `nav_id` | INTEGER | PRIMARY KEY (Auto) | Unique log serial identifier row. |
| `amfi_code` | INTEGER | FOREIGN KEY | Parent target link pointer matching `dim_fund`. |
| `nav_date` | TEXT | FOREIGN KEY | Target operational date pointing to `dim_date`. |
| `nav` | REAL | Check (> 0) | Clean Net Asset Value currency evaluation unit. |
| `is_forward_filled`| INTEGER| Check (0, 1) | Tracks if row was forward-filled due to a holiday.|

### `fact_transactions`
Audits systematic and one-off execution flows across regional user portfolios.
*Source Reference: investor_transactions.csv*

| Column Name | Data Type | Key Constraints | Business Definition |
| :--- | :--- | :--- | :--- |
| `transaction_id`| INTEGER| PRIMARY KEY (Auto) | Unique ledger sequence reference key. |
| `investor_id` | TEXT | Not Null | Anonymized unique user tracking signature hash. |
| `amfi_code` | INTEGER | FOREIGN KEY | Target investment scheme link matched to `dim_fund`.|
| `transaction_date`| TEXT | FOREIGN KEY | Chronological execution map index to `dim_date`. |
| `transaction_type`| TEXT | Check (Enum) | Transaction class constraint: SIP, Lumpsum, Redemption. |
| `amount` | REAL | Check (> 0) | Monetary liquidity volume value in INR. |
| `state` | TEXT | Not Null | Indian state where the transaction originated. |
| `kyc_status` | TEXT | Check (Enum) | Compliance standing validation: Verified, Pending, Failed. |