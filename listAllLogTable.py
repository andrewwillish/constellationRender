import sqlite3
import os

rootPathVar=os.path.dirname(os.path.realpath(__file__)).replace('\\','/')

con=sqlite3.connect(rootPathVar+'/constellationDatabase.db')

prt=con.execute("SELECT * FROM constellationLogTable").fetchall()
for chk in prt:
    print chk