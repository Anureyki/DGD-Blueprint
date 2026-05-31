const sqlite3 = require('sqlite3').verbose()
const db = new sqlite3.Database('./strains.db')

db.all("SELECT * FROM strains WHERE name LIKE '%Oyster%'", (err, rows) => {
  if (err) console.error(err)
  else console.log(rows)
})
