import sqlite3
import lib.sql_interface
from lib.constants import *
connection = None

for i in range(len(lib.sql_interface.SQL.TABLE_NAMES)):
    print '%d\t%s' % (i, lib.sql_interface.SQL.TABLE_NAMES[i])
print '-1\tExit'

alive = True
while alive:
    _input = raw_input('table: ')
    try:
        _input = int(_input)
        alive = _input != -1
        if not alive:
            break
        connection = sqlite3.connect(DATABASE_PATH)
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM %s' %
                       lib.sql_interface.SQL.TABLE_NAMES[_input])
        for result in cursor.fetchall():
            print '\t%s' % str(result)
        connection.close()
    except ValueError, IndexError:
        print '\tInvalid input.'
        if connection:
            connection.close()
