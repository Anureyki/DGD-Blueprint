# Building the Decentralized Genetic Database (DGD) Prototype

## Goal
Ingest public plant/cannabis strain data into a private, decentralized database using IPFS for immutable storage and SQLite for local querying.

## Stack
- **IPFS (Kubo)** – running as a systemd service on Ubuntu (private swarm with `swarm.key`)
- **Python 3** – with pandas, requests, sqlite3
- **IPFS HTTP API** – direct `curl` or `requests.post` to `/api/v0/add` (bypasses `ipfshttpclient` version issues)
- **SQLite** – local index for fast searches

## What We Tried (and What Failed)
- `ipfshttpclient` → version mismatch (daemon 0.41.0, client expects <0.8.0)
- `orbit-db` + `helia` → native compilation errors, deprecation warnings
- Parquet datasets (`cannlytics/cannabis_results`) → 404 or missing `pyarrow`
- Hugging Face API → authentication or URL changes

## The Working Solution (Step‑by‑Step)

### 1. Environment Setup
```bash
mkdir -p ~/dgd-simple
cd ~/dgd-simple
python3 -m venv venv
source venv/bin/activate
pip install pandas requests
```

### 2. Obtain a Public CSV Dataset
Example: Kushy cannabis strains (GitHub)
```bash
curl -o real_strains.csv https://raw.githubusercontent.com/kushyapp/cannabis-dataset/master/Dataset/Strains/strains-kushy_api.2017-11-14.csv
```

Check columns: `head -1 real_strains.csv`

### 3. Create the Ingestion Script
File: `scripts/ingest.py` (full code below)

Key functions:
- `fetch_data()` – reads CSV with pandas
- `transform_row()` – maps CSV columns to JSON document
- `store_in_ipfs()` – uses `requests.post` to IPFS API (no external client)
- `store_in_sqlite()` – inserts/updates SQLite table

### 4. Run the Script
```bash
python scripts/ingest.py
```

You will see CIDs printed for each strain.

### 5. Verify
```bash
sqlite3 strains.db "SELECT name, thc, cbd FROM strains LIMIT 10;"
curl -X POST "http://127.0.0.1:5001/api/v0/cat?arg=<CID>"
```

## The Final Working Script (copy‑paste)

Save as `scripts/ingest.py`:

```python
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
    conn.execute(''CREATE TABLE IF NOT EXISTS strains (
        id TEXT PRIMARY KEY,
        cid TEXT,
        name TEXT,
        scientific_name TEXT,
        optimal_temp REAL,
        timestamp TEXT,
        thc REAL,
        cbd REAL
    )'')
    conn.close()

def fetch_data():
    return pd.read_csv("real_strains.csv")

def transform_row(row):
    name = row.get('name', 'unknown')
    if pd.isna(name):
        return None
    sid = name.lower().replace(' ', '_')
    return {
        "_id": sid,
        "name": name,
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
    for _, row in df.iterrows():
        rec = transform_row(row)
        if not rec:
            continue
        cid = store_in_ipfs(rec)
        store_in_sqlite(cid, rec)
        print(f"Stored {rec['name']} -> CID: {cid}")

if __name__ == "__main__":
    main()
```

## How to Adapt for Any Public API or Dataset

1. **Replace `fetch_data()`** – call an API (e.g., `requests.get(url).json()`) or read any CSV/Parquet.
2. **Modify `transform_row()`** – map the incoming fields to your JSON schema (`_id`, `name`, etc.).
3. **Update the SQLite table schema** – add columns that match your data.
4. **Run periodically via cron** – for automatic ingestion of fresh data.

## Lessons Learned
- **Avoid `ipfshttpclient`** – use direct HTTP requests to IPFS API (version‑proof).
- **Use local CSV for testing** – then switch to real URLs once the pipeline works.
- **Handle schema changes** – delete `strains.db` if you change the table structure.
- **Always run in a virtual environment** – prevents dependency conflicts.

## Next Steps
- Add automated ingestion from government APIs (USDA, FAO) using cron.
- Train a regression model to predict THC or CBD from other attributes.
- Build a simple web dashboard to query the DGD.

## Related Repos
- [DGD-Blueprint](https://github.com/Anureyki/DGD-Blueprint) – high‑level design
- [AgNetworking](https://github.com/Anureyki/AgNetworking) – AI ecosystem
