import sqlite3

connection_object = sqlite3.connect('Data/myTest.db')

cursor = connection_object.cursor()

insertScript = """insert	into	users(username, password_hash, role)
		values('commonDoe', '123456789', 'user')"""

cursor.execute(insertScript)
connection_object.commit()