__author__ = 'andrew.willis'

#import module
import sqlite3
import os

rootPathVar = os.path.dirname(os.path.realpath(__file__)).replace('\\','/')
con = sqlite3.connect(rootPathVar+'/constellationDatabase.db')

os.system('cls')

prt = con.execute("SELECT * FROM constellationLogTable").fetchall()
for chk in prt:
    print chk[0], '\t', chk[1], '\t', chk[2], '\t', chk[3].replace('\n', ''), '\t', chk[4]