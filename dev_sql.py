import sqlite3
from lib.constants import *
connection = None

alive = True
while alive:
    _input = raw_input('> ')
    if _input == 'exit':
        break
    try:
        connection = sqlite3.connect(DATABASE_PATH)
        cursor = connection.cursor()
        cursor.execute(_input)
        for result in cursor.fetchall():
            print '\t%s' % str(result)
        connection.close()
    except:
        print '\tInvalid input.'
        if connection:
            connection.close()
