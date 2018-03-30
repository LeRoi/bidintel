from enum import IntEnum
import sqlite3
import structure

class Tables(IntEnum):
    PROFESSORS = 0
    COURSES = 1
    FULL_COURSES = 2
    USERS = 3
    BIDS = 4
    NEXT_ID = 5

class SQL:
    class CREATE:
        CREATE_PROFESSORS_TABLE = '''
        CREATE TABLE professors (
            id INTEGER PRIMARY KEY,
            name TINYTEXT);'''

        CREATE_COURSES_TABLE = '''
        CREATE TABLE courses (
            id INTEGER PRIMARY KEY,
            type INTEGER,
            name TINYTEXT);'''

        CREATE_FULL_COURSES_TABLE = '''
        CREATE TABLE fullCourses (
            id INTEGER PRIMARY KEY,
            cId INTEGER,
            pId INTEGER);'''

        CREATE_USERS_TABLE = '''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            hasBid BIT,
            bids TEXT);'''

        CREATE_BIDS_TABLE = '''
        CREATE TABLE bids (
            id INTEGER PRIMARY KEY,
            fId INTEGER,
            term INTEGER,
            year INTEGER,
            rank INTEGER,
            gotIn BIT,
            waitlist INTEGER);'''

        CREATE_NEXT_IDS_TABLE = '''
        CREATE TABLE nextIds(
            id INTEGER PRIMARY KEY,
            nextId INTEGER);'''

    class INSERT:
        INSERT_PROFESSOR = 'INSERT INTO professors (id, name) VALUES (%d, "%s");'
        INSERT_COURSE = 'INSERT INTO courses (id, type, name) VALUES (%d, %d, "%s");'
        INSERT_FULL_COURSE = 'INSERT INTO fullCourses (id, cId, pId) VALUES (%d, %d, %d);'
        INSERT_USER = 'INSERT INTO users (id, hasBid, bids) VALUES (%d, %d, "%s");'
        INSERT_BID = '''
        INSERT INTO bids (id, fId, term, year, rank, gotIn, waitlist)
        VALUES (%d, %d, %d, %d, %d, %d, %d);'''
        INSERT_NEXT_ID = 'INSERT INTO nextIds (id, nextId) VALUES (%d, %d);'

    TABLE_NAMES = ['professors', 'courses', 'fullCourses',
                   'users', 'bids', 'nextIds']
    TABLE_MAP = {
        Tables.PROFESSORS: 'professors',
        Tables.COURSES: 'courses',
        Tables.FULL_COURSES: 'fullCourses',
        Tables.USERS: 'users',
        Tables.BIDS: 'bids',
        Tables.NEXT_ID: 'nextIds'
    }
    SELECT_ALL = 'SELECT * FROM %s;'
    

def sql_connect(src):
    return sqlite3.connect(src)

def sql_close(db):
    db.commit()
    db.close()

## RUN ONCE ##
def create_tables(db):
    cursor = db.cursor()
    cursor.execute(SQL.CREATE.CREATE_PROFESSORS_TABLE)
    cursor.execute(SQL.CREATE.CREATE_COURSES_TABLE)
    cursor.execute(SQL.CREATE.CREATE_FULL_COURSES_TABLE)
    cursor.execute(SQL.CREATE.CREATE_USERS_TABLE)
    cursor.execute(SQL.CREATE.CREATE_BIDS_TABLE)
    cursor.execute(SQL.CREATE.CREATE_NEXT_IDS_TABLE)

    for i in range(Tables.NEXT_ID):
        # Start ids at 1000
        cursor.execute(SQL.INSERT.INSERT_NEXT_ID % (i, 1000))
    db.commit()

####

def query(cursor, query, debug=True):
    if debug:
        print '\t%s' % query
    cursor.execute(query)

def get_next_id(db, table):
    cursor = db.cursor()
    query(cursor, 'SELECT nextId FROM nextIds WHERE id = %d' % table)
    return cursor.fetchone()[0]

def update_next_id(db, table, nextId):
    cursor = db.cursor()
    query(cursor, 'UPDATE nextIds SET nextId = %d WHERE id = %d' % (nextId, table))
    db.commit()

def insert_row(db, table, rowObject):
    cursor = db.cursor()
    if table == Tables.PROFESSORS:
        query(cursor, SQL.INSERT.INSERT_PROFESSOR % (rowObject.id, rowObject.name))
    elif table == Tables.COURSES:
        query(cursor, SQL.INSERT.INSERT_COURSE % (rowObject.id, rowObject.type, rowObject.name))
    elif table == Tables.FULL_COURSES:
        query(cursor, SQL.INSERT.INSERT_FULL_COURSE % (rowObject.id, rowObject.c_id, rowObject.p_id))
    elif table == Tables.USERS:
        query(cursor, SQL.INSERT.INSERT_USER %
                       (rowObject.id, 1 if rowObject.has_bids() else 0, rowObject.bid_string()))
    elif table == Tables.BIDS:
        query(cursor, SQL.INSERT.INSERT_BID % (
            rowObject.id, rowObject.f_id, rowObject.term,
            rowObject.year, rowObject.rank, rowObject.gotIn, rowObject.waitlist))
    db.commit()
    
