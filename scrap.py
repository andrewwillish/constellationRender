import sqlite3

con=sqlite3.connect('constellationDatabase.db')

prt=con.execute("SELECT * FROM constellationJobTable").fetchall()
for chk in prt:
    print chk