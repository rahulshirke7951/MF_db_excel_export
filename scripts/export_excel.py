import requests
import sqlite3
import pandas as pd
import os

OWNER = os.environ["OWNER"]
REPO = os.environ["REPO"]

print("Fetching latest release info...")

url = f"https://api.github.com/repos/{OWNER}/{REPO}/releases/latest"

response = requests.get(url)
if response.status_code != 200:
    raise Exception("Failed to fetch release info")

release = response.json()

download_url = None
assets = release.get("assets", [])

for asset in assets:
    if asset["name"] == "mf.db":
        download_url = asset["browser_download_url"]
        break

if not download_url:
    raise Exception("mf.db not found in latest release")

print("Downloading mf.db...")
db_file = requests.get(download_url)

with open("mf.db", "wb") as f:
    f.write(db_file.content)

print("Reading database...")
conn = sqlite3.connect("mf.db")

df = pd.read_sql("SELECT * FROM nav_history", conn)
conn.close()

print("Rows in DB:", len(df))

# sort + format date
df["nav_date"] = pd.to_datetime(df["nav_date"], errors="coerce")
df = df.sort_values(["scheme_code", "nav_date"])

print("Exporting to Excel...")
df.to_excel("mf_data.xlsx", index=False)

print("✅ Excel file created")
