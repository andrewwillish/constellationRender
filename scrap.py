import sqlite3
import os

rootPathVar=os.path.dirname(os.path.realpath(__file__)).replace('\\','/')

con=sqlite3.connect(rootPathVar+'/constellationDatabase.db')

prt=con.execute("UPDATE constellationClientTable SET clientJob='199' WHERE clientId='2'")
con.commit()