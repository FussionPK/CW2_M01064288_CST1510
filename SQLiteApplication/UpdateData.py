import sqlite3

connection_object = sqlite3.connect('Data/myTest.db')

cursor = connection_object.cursor()


userid = "commonDoe"
UpdateScript = f""" update users 
                        set role = 'admin'
                        where username = ? """


print(UpdateScript)

cursor.execute(UpdateScript, (userid,))
connection_object.commit()


