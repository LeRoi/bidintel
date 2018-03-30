import flask, json, os
from flask import jsonify, Flask, Response, request, render_template

import lib.structure, lib.sql_interface
from lib.constants import *

app = Flask(__name__)
debug = True

def setup_server():
    first_run = False
    if not os.path.exists(DATABASE_PATH):
        first_run = True

    db = lib.sql_interface.sql_connect(DATABASE_PATH)
    if first_run:
        lib.sql_interface.create_tables(db)

    cursor = db.cursor()
    cursor.execute(lib.sql_interface.SQL.SELECT_ALL % 'fullCourses')
    _maxRow = 0
    for r in cursor.fetchall():
        _maxRow = max(_maxRow, r[0])
    lib.sql_interface.insert_row(db, lib.sql_interface.Tables.FULL_COURSES,
                             lib.structure.FullCourse(_maxRow + 1, 1, 2))
    db.close()

def add_row(table, data):
    db = lib.sql_interface.sql_connect(DATABASE_PATH)
    lib.sql_interface.insert_row(db, table, data)
    db.close()

def to_ascii(form):
    result = {}
    for k in form:
        result[k] = str(form[k].decode('utf-8').encode('ascii'))
    return result

def format_data(table, form, next_id):
    if table == lib.sql_interface.Tables.PROFESSORS:
        return lib.structure.Professor(next_id, form['professor'])
    elif table == lib.sql_interface.Tables.COURSES:
        return lib.structure.Course(next_id, form['course_name'],
                                    int(form['course_type']))
    elif table == lib.sql_interface.Tables.FULL_COURSES:
        return lib.structure.FullCourse(next_id, int(form['course_id']),
                                        int(form['professor_id']))
    elif table == lib.sql_interface.Tables.USERS:
        return lib.structure.User(next_id, bid_string=form['bids'])
    elif table == lib.sql_interface.Tables.BIDS:
        return lib.structure.Bid(next_id, int(form['term']),
                                 int(form['year']), int(form['position']))
  
@app.route('/')
def home():
    return Response(render_template('main.html'))

@app.route('/bid')
def bid():
    return Response(render_template('bid.html'))

@app.route('/submitbids', methods=['POST'])
def submit_bids():
    print request.form
    form = to_ascii(request.form)
    table = int(form['table'])
    db = lib.sql_interface.sql_connect(DATABASE_PATH)
    next_id = lib.sql_interface.get_next_id(db, table)
    lib.sql_interface.update_next_id(db, table, next_id + 1)
    db.close()
    add_row(table, format_data(table, form, next_id))
    return json.dumps({'status':'OK'})

@app.route('/drag')
def drag():
    return Response(render_template('drag.html'))

setup_server()
if __name__ == '__main_':
    port = int(os.envion.get('PORT', Server.PORT))
    app.run(host=Server.HOST, port=port, debug=debug)

    
