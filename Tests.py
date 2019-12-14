import pymorphy2
import psycopg2
from Types import *
from Functions import *
from dbFunctions import *

morph = pymorphy2.MorphAnalyzer()
con = psycopg2.connect(dbname='gpatterns', user='postgres', 
                        password='postgres', host='localhost')
cursor = con.cursor()

m = parseToMorph("дождинка", morph.parse("дождинка")[0])
a = dbInsertMorph(con, m)
print(a)

m = parseToMorph("дождинка", morph.parse("дождинка")[0])
a = dbFindMorph(con, m)
print(a)

w = 'лето'
dbInsertWord(con, w)
print(w)

a = dbFindWord(con, 'сон')
print(a)
con.close()