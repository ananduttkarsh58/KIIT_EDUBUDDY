const sqlite3 = require('sqlite3').verbose();

const db = new sqlite3.Database('./database.sqlite');

db.serialize(() => {
    console.log("🔹 Setting up the database...");
    db.run(`CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password TEXT
    )`, (err) => {
        if (err) console.error("❌ Error creating users table:", err);
        else console.log("✅ Users table created successfully!");
    });
});

db.close(() => console.log("🔹 Database setup complete!"));







