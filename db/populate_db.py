import sqlite3

db = sqlite3.connect("db/mealtime.sqlite", isolation_level=None)
c = db.cursor()

sql = "INSERT INTO Users (first_name, last_name, email, password) VALUES (?, ?, ?, ?)"
values = [("Justin", "Wong", "justin.wong.17@ucl.ac.uk")]
c.executemany(sql, values)