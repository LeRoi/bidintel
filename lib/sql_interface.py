from enum import IntEnum
from logic import *
import constants
import sqlite3

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
            pIds TEXT);'''

        ## Year is graduation year.
        ## isTransfer 0 -> No, 1 -> Yes
        CREATE_USERS_TABLE = '''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            email TEXT,
            year INTEGER,
            isTransfer INTEGER,
            intl_1L TEXT,
            spring_1L TEXT,
            clinic_2L TEXT,
            multisection_2L TEXT,
            fall_2L TEXT,
            winter_2L TEXT,
            spring_2L TEXT,
            clinic_3L TEXT,
            multisection_3L TEXT,
            legalprof_3L TEXT,
            fall_3L TEXT,
            winter_3L TEXT,
            spring_3L TEXT);'''

        CREATE_BIDS_TABLE = '''
        CREATE TABLE bids (
            id INTEGER PRIMARY KEY,
            fId INTEGER,
            term INTEGER,
            year INTEGER,
            rank INTEGER,
            gotIn INTEGER,
            waitlist INTEGER);'''

        CREATE_NEXT_IDS_TABLE = '''
        CREATE TABLE nextIds(
            id INTEGER PRIMARY KEY,
            nextId INTEGER);'''

    class INSERT:
        INSERT_PROFESSOR = 'INSERT INTO professors (id, name) VALUES (%d, "%s");'
        INSERT_COURSE = 'INSERT INTO courses (id, type, name) VALUES (%d, %d, "%s");'
        INSERT_FULL_COURSE = 'INSERT INTO fullCourses (id, cId, pIds) VALUES (%d, %d, "%s");'
        INSERT_USER = '''
        INSERT INTO users (id, email, year, isTransfer)
        VALUES (%d, "%s", %d, %d);'''
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

## RUN ONCE END ##

def query(cursor, query, debug=True, is_mock=False):
    if debug:
        try:
            print ('[MOCK] ' if is_mock else '') + '\t%s' % query
        except:
            print ('[MOCK] ' if is_mock else '') + \
                  '[Silently failed to print: %s]' % query.encode('ascii', 'ignore')
    if not is_mock:
        cursor.execute(query)

def get_next_id(db, table):
    cursor = db.cursor()
    query(cursor, 'SELECT nextId FROM nextIds WHERE id = %d' % table)
    return cursor.fetchone()[0]

## Should probably be linked with insert operations...
def update_next_id(db, table, nextId):
    cursor = db.cursor()
    query(cursor, 'UPDATE nextIds SET nextId = %d WHERE id = %d' % (nextId, table))
    db.commit()

def fetch_table(src, table):
    db = sql_connect(src)
    cursor = db.cursor()
    query(cursor, SQL.SELECT_ALL % SQL.TABLE_MAP[table])
    result = [line for line in cursor.fetchall()]
    db.close()
    return result

def insert_row(db, table, rowObject):
    cursor = db.cursor()
    if table == Tables.PROFESSORS:
        query(cursor, SQL.INSERT.INSERT_PROFESSOR % (rowObject.id, rowObject.name))
    elif table == Tables.COURSES:
        query(cursor, SQL.INSERT.INSERT_COURSE % (rowObject.id, rowObject.type, rowObject.name))
    elif table == Tables.FULL_COURSES:
        query(cursor, SQL.INSERT.INSERT_FULL_COURSE % (rowObject.id, rowObject.c_id, ids_to_csv(rowObject.p_ids)))
    elif table == Tables.USERS:
        query(cursor, SQL.INSERT.INSERT_USER %
                       (rowObject.id, 1 if rowObject.has_bids() else 0, ids_to_csv(rowObject.bids)))
    elif table == Tables.BIDS:
        query(cursor, SQL.INSERT.INSERT_BID % (
            rowObject.id, rowObject.f_id, rowObject.term,
            rowObject.year, rowObject.rank, rowObject.gotIn, rowObject.waitlist))
    db.commit()
    
