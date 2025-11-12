import sqlite3

connection_object = sqlite3.connect('Data/myTest.db')

cursor = connection_object.cursor()

createScript = """ create table if not exists users(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	username TEXT NOT NULL UNIQUE,
	password_hash TEXT NOT NULL,
	role TEXT DEFAULT 'user'
)"""

cursor.execute(createScript)
connection_object.commit()