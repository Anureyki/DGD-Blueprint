#!/home/anureyki/AgTechAI/venv/bin/python3
import json
import sqlite3
import os
import pandas as pd
import requests

DB_PATH = os.getenv("DGD_DB_PATH", "./strains.db")
IPFS_API_URL = "http://127.0.0.1:5001/api/v0/add"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS strains (
        id TEXT PRIMARY KEY,
        cid TEXT,
        name TEXT,
        scientific_name TEXT,
        optimal_temp REAL,
        timestamp TEXT,
        thc REAL,
        cbd REAL
    )''')
    conn.close()

def fetch_data():
    return pd.read_csv("real_strains.csv")

def transform_row(row):
    strain_name = row.get('name', 'unknown')
    if pd.isna(strain_name):
        return None
    strain_id = strain_name.lower().replace(' ', '_')
    return {
        "_id": strain_id,
        "name": strain_name,
        "scientific_name": "Cannabis sativa",
        "optimal_temp": 24.0,
        "thc": row.get('thc', 0.0),
        "cbd": row.get('cbd', 0.0),
    }

def store_in_ipfs(data):
    files = {'file': json.dumps(data)}
    resp = requests.post(IPFS_API_URL, files=files)
    resp.raise_for_status()
    return resp.json()['Hash']

def store_in_sqlite(cid, record):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO strains (id, cid, name, scientific_name, optimal_temp, timestamp, thc, cbd) VALUES (?,?,?,?,?,?,?,?)",
                (record["_id"], cid, record["name"], record["scientific_name"], record["optimal_temp"], "", record.get("thc", 0.0), record.get("cbd", 0.0)))
    conn.commit()
    conn.close()

def main():
    init_db()
    df = fetch_data()
    # Limit to first 100 rows for testing (remove the slice later)
    for _, row in df.iterrows():
        record = transform_row(row)
        if record is None:
            continue
        cid = store_in_ipfs(record)
        store_in_sqlite(cid, record)
        print(f"Stored {record['name']} -> CID: {cid}")

if __name__ == "__main__":
    main()
