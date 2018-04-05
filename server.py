import flask, json, os
from flask import jsonify, Flask, Response, request, render_template

import lib.structure as struct
import lib.sql_interface as sql
from lib.constants import *
from lib.logic import *

app = Flask(__name__)
debug = True

def setup_server():
    first_run = not os.path.exists(DATABASE_PATH)
    db = sql.sql_connect(DATABASE_PATH)
    if first_run:
        sql.create_tables(db)
    db.close()

def add_row(table, data):
    db = sql.sql_connect(DATABASE_PATH)
    sql.insert_row(db, table, data)
    db.close()

## Move this to another file
def format_data(table, form, next_id):
    print '\tFormatting (ID=%d) %s for Table %s' % (next_id, str(form), str(sql.Tables(table)))
    if table == sql.Tables.PROFESSORS:
        return struct.Professor(next_id, form['professor'])
    elif table == sql.Tables.COURSES:
        return struct.Course(next_id, form['course_name'],
                                    int(form['course_type']))
    elif table == sql.Tables.FULL_COURSES:
        return struct.FullCourse(next_id, int(form['course_id']),
                                        csv_to_ids(form['professor_ids']))
    elif table == sql.Tables.USERS:
        return struct.User(next_id, csv_to_ids(['bids']))
    elif table == sql.Tables.BIDS:
        return struct.Bid(next_id, int(form['term']),
                                 int(form['year']), int(form['position']))
  
@app.route('/')
def home():
    return Response(render_template('main.html'))

## Should pre-process some of this.
@app.route('/data/professors')
def professors():
    professors = []
    for result in sql.fetch_table(sql.Tables.PROFESSORS):
        professors.append({'id': result[0],
                           'name': result[1]})
    return json.dumps({'professors': professors})

@app.route('/data/courses')
def courses():
    courses = []
    for result in sql.fetch_table(sql.Tables.COURSES):
        courses.append({'id': result[0],
                        'type': result[1],
                        'name': result[2]})
    return json.dumps({'courses': courses})

@app.route('/data/fullcourses')
def fullcourses():
    fullcourses = []
    for result in sql.fetch_table(sql.Tables.FULL_COURSES):
        fullcourses.append({'id': result[0],
                        'cid': result[1],
                        'pids': csv_to_ids(result[2])})
    return json.dumps({'fullcourses': fullcourses})

## Clean this up later
@app.route('/ngtest')
def ngtest():
    return Response(render_template('ng.html'))

@app.route('/bid')
def bid():
    return Response(render_template('bid.html'))

@app.route('/bid/text_entry')
def bid_text_entry():
    return Response(render_template('bid_text_entry.html'))

@app.route('/update')
def update_db():
    return Response(render_template('update_db.html'))

@app.route('/submit_rows', methods=['POST'])
def submit_rows():
    form = json.loads(request.data)
    table = form['table']
    db = sql.sql_connect(DATABASE_PATH)
    next_id = sql.get_next_id(db, table)
    sql.update_next_id(db, table, next_id + 1)
    db.close()
    add_row(table, format_data(table, form, next_id))
    return json.dumps({'status':'OK'})

@app.route('/submit_bids', methods=['POST'])
def submit_bids():
    print 'Received data: %s' % str(request.data)
    return json.dumps({'status':'OK'})

@app.route('/submit_bid_text', methods=['POST'])
def submit_bid_text():
    print 'Received data for bid text: %s' % str(request.data)
    print 'Understood as %s' % str(struct.email_to_bid_data(to_ascii_simple(request.data)))
    return json.dumps({'status':'OK'})

setup_server()
if __name__ == '__main_':
    port = int(os.envion.get('PORT', Server.PORT))
    app.run(host=Server.HOST, port=port, debug=debug)

    
