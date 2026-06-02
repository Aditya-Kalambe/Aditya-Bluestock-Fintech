import os
import sqlite3
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = os.path.join(BASE_DIR, "data", "db", "bluestock_mf.db")
REPORT_OUTPUT = os.path.join(BASE_DIR, "reports", "performance_summary.html")

def generate_html_report():
    conn = sqlite3.connect(DB_PATH)
    
    # Extract current snapshot statuses
    query = """
        SELECT m.scheme_name, MIN(n.nav_date) as inception, MAX(n.nav_date) as latest_date,
               COUNT(*) as tracking_days, SUM(n.is_forward_filled) as adjusted_holidays
        FROM fund_master m
        JOIN nav_history n ON m.scheme_code = n.scheme_code
        GROUP BY m.scheme_name
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Generate HTML styling template mapping
    table_rows = ""
    for _, row in df.iterrows():
        table_rows += f"""
        <tr>
            <td style='padding: 12px; border-bottom: 1px solid #ddd;'>{row['scheme_name']}</td>
            <td style='padding: 12px; border-bottom: 1px solid #ddd; text-align: center;'>{row['inception']}</td>
            <td style='padding: 12px; border-bottom: 1px solid #ddd; text-align: center;'>{row['latest_date']}</td>
            <td style='padding: 12px; border-bottom: 1px solid #ddd; text-align: right;'>{row['tracking_days']}</td>
            <td style='padding: 12px; border-bottom: 1px solid #ddd; text-align: right; color: #e67e22;'>{row['adjusted_holidays']}</td>
        </tr>
        """

    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; margin: 40px;">
        <h2 style="color: #2c3e50; border-bottom: 2px solid #34495e; padding-bottom: 10px;">Bluestock Mutual Fund Analytics Ingestion Report</h2>
        <p>Hello Team,</p>
        <p>The automated ETL ingestion cycle ran completely. Here is your operational data quality summary:</p>
        <table style="width: 100%; border-collapse: collapse; margin-top: 20px; box-shadow: 0 2px 3px rgba(0,0,0,0.1);">
            <thead>
                <tr style="background-color: #34495e; color: white; text-align: left;">
                    <th style="padding: 12px;">Scheme Name</th>
                    <th style="padding: 12px; text-align: center;">Data Start</th>
                    <th style="padding: 12px; text-align: center;">Data End</th>
                    <th style="padding: 12px; text-align: right;">Total Tracked Days</th>
                    <th style="padding: 12px; text-align: right;">Holiday Patches (ffill)</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
        <br>
        <p style="font-size: 0.85em; color: #7f8c8d;">Status: Operational | Server Location: Local Production Node Pipeline</p>
    </body>
    </html>
    """
    
    with open(REPORT_OUTPUT, "w") as f:
        f.write(html_content)
    print(f"🏆 Production HTML Executive Summary generated at: {REPORT_OUTPUT}")
    return html_content

def dispatch_production_email(html_body):
    """
    Optional live dispatcher framework. 
    To activate live emails: populate real production SMTP credentials.
    """
    sender = "your_alerts_email@gmail.com"
    receiver = "aditya.kalambe@tiss.edu"
    password = "your_app_password"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "🚀 Operational Notification: Ingestion Integrity Pipeline Report"
    msg["From"] = sender
    msg["To"] = receiver
    msg.attach(MIMEText(html_body, "html"))

    # Left commented deliberately so script doesn't fail out due to missing credentials
    # try:
    #     with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    #         server.login(sender, password)
    #         server.sendmail(sender, receiver, msg.as_string())
    #     print("Email dispatched dynamically to target production endpoint.")
    # except Exception as e:
    #     print(f"Email skip triggered: {e}")

if __name__ == "__main__":
    body = generate_html_report()
    dispatch_production_email(body)