# DGD Prototype – IPFS + SQLite

## What This Is

A working proof‑of‑concept for the Decentralized Genetic Database. Plant/fungal strain data is stored as JSON on IPFS, while a local SQLite index keeps searchable metadata.

## The Tech Stack

- `ipfs-http-client@55.0.0` – last CommonJS version, works with `require()`
- `sqlite3` – local index for fast queries
- Your existing IPFS daemon (running as systemd service)

## How It Works

1. `add-strain.js` – reads a JSON object, stores it on IPFS, records the CID and metadata in SQLite.
2. `query.js` – searches the SQLite index by name.

## Why This Works (After Many Circles)

We tried multiple approaches that failed:

- `orbit-db` + `ipfs-core` → `ERR_PACKAGE_PATH_NOT_EXPORTED`
- `helia` + `@orbitdb/core` → native compilation errors
- Newer `ipfs-http-client` → ESM/CommonJS mismatch

**The solution:** Use `ipfs-http-client@55.0.0` (CommonJS) and talk to your existing IPFS daemon. No embedded IPFS, no native nightmares.

## Files

- `add-strain.js` – add a strain to the DGD
- `query.js` – query strains by name
- `strains.db` – SQLite database (created automatically)

## Example Output

```
[{
  id: 'oyster1',
  cid: 'QmRrQjrBA6HUJXMtummUdrraek7oi1SrzMvig7A45fUPWL',
  name: 'King Oyster',
  scientific_name: 'Pleurotus eryngii',
  optimal_temp: 24,
  timestamp: '2026-05-31T00:38:37.786Z' 
}]
```

## Next Steps

- Add more fields (substrate, light cycle, etc.)
- Integrate with your AgTech AI (RAG pipeline)
- Later, replace SQLite with a decentralized index (OrbitDB / DHT) when the ecosystem stabilises

## Related

- [DGD Blueprint (parent folder)](..)
- [AgNetworking Ecosystem](https://github.com/Anureyki/AgNetworking)

---
*This is the working foundation. The circles are over.*
