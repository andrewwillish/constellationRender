import sqlite3
import os

rootPathVar=os.path.dirname(os.path.realpath(__file__)).replace('\\','/')

con=sqlite3.connect(rootPathVar+'/constellationDatabase.db')

con.execute("UPDATE constellationJobTable SET jobStatus='QUEUE', jobBlocked='ENABLED', jobRenderTime=NULL")
con.commit()
