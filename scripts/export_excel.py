import requests
import sqlite3
import pandas as pd
import os

OWNER = os.environ["OWNER"]
REPO = os.environ["REPO"]

print("Fetching latest release info...")

url = f"https://api.github.com/repos/{OWNER}/{REPO}/releases/latest"
release = requests.get(url).json()

download_url = None

for asset in release["assets"]:
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

print("Exporting to Excel...")
df.to_excel("mf_data.xlsx", index=False)

print("✅ Excel file created")
