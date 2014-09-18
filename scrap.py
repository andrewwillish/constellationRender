import sqlite3
import os

rootPathVar=os.path.dirname(os.path.realpath(__file__)).replace('\\','/')

con=sqlite3.connect(rootPathVar+'/constellationDatabase.db')

prt=con.execute("UPDATE constellationClientTable SET clientMemory='0', clientThread='0', clientWorkMemory='0', clientWorkThread='0' WHERE clientId='1'")
con.commit()