import sqlite3

connection_object = sqlite3.connect('Data/myTest.db')

cursor = connection_object.cursor()

userid = "attackDoe' OR '1'='1"

SelectScript = f""" select * from users
                        where username = ? """


print(SelectScript)


cursor.execute(SelectScript, parameters=(userid,))
all_users = cursor.fetchall()
for user in all_users:
    print(user)
connection_object.commit()
