import sqlite3

connection_object = sqlite3.connect('Data/myTest.db')

cursor = connection_object.cursor()

userid = "JohnDoe"
DeleteScript = f""" delete from users where username = '{userid}' """

cursor.execute(DeleteScript)
connection_object.commit()
connection_object.close()