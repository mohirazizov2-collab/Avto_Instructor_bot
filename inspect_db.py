import sqlite3

con = sqlite3.connect("avtomaktab.db")
cur = con.cursor()

for row in cur.execute("SELECT sql FROM sqlite_master WHERE type='table'"):
    print(row[0])
    print("-" * 60)