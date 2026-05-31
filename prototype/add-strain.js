const IPFS = require('ipfs-http-client')
const sqlite3 = require('sqlite3').verbose()

// Connect to your running IPFS daemon (default port 5001)
const ipfs = IPFS.create({ url: 'http://localhost:5001' })
const db = new sqlite3.Database('./strains.db')

// Initialize table
db.run(`CREATE TABLE IF NOT EXISTS strains (
  id TEXT PRIMARY KEY,
  cid TEXT NOT NULL,
  name TEXT,
  scientific_name TEXT,
  optimal_temp REAL,
  timestamp TEXT
)`)

async function addStrain(strain) {
  const data = JSON.stringify(strain)
  const { cid } = await ipfs.add(data)
  const cidStr = cid.toString()
  const stmt = db.prepare(`INSERT OR REPLACE INTO strains (id, cid, name, scientific_name, optimal_temp, timestamp) VALUES (?, ?, ?, ?, ?, ?)`)
  stmt.run(strain._id, cidStr, strain.name, strain.scientific_name, strain.optimal_temp, new Date().toISOString())
  stmt.finalize()
  console.log(`✅ Stored ${strain._id} -> IPFS CID: ${cidStr}`)
}

// Test strain
addStrain({
  _id: 'oyster1',
  name: 'King Oyster',
  scientific_name: 'Pleurotus eryngii',
  optimal_temp: 24
}).catch(console.error)
