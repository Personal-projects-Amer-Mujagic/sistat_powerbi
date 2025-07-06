# Imports
import pandas as pd
import sys, json, requests, logging
from pathlib import Path


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logfile.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

url = r"https://pxweb.stat.si:443/SiStatData/api/v1/sl/Data/0701015S.px"
request_json_path = Path("json_requests") / "sistat_gross_net_pay_monthly_request.json"
write_excel_path = Path("files") / "sistat_gross_net_pay_monthly.xlsx"

# Load request JSON
try:
    with request_json_path.open("r") as f:
        request_json = json.load(f)
except FileNotFoundError as e:
    logging.error(f"JSON file not found: {e}")
    sys.exit(1)
except json.JSONDecodeError as e:
    logging.error(f"Malformed JSON: {e}")
    sys.exit(1)

# Send POST request
try:
    response = requests.post(url, json=request_json, timeout=10)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    logging.error(f"Request failed: {e}")
    sys.exit(1)

rows = response.text.split("\r\n")
rows = [row.split(",") for row in rows if row.strip()]
header = [cell.strip('"') for cell in rows[0]]
df = pd.DataFrame(rows[1:], columns=header)

df["SEKTOR"] = df["SEKTOR"].str.strip('"')
df["MESEC"] = df["MESEC"].str.strip('"')
df[["LETO", "MESEC"]] = df["MESEC"].str.split("M", expand=True)

# Write to Excel
try:
    df.to_excel(write_excel_path, index=False)
except Exception as e:
    logging.error(f"Failed to write Excel file: {e}")
    sys.exit(1)
