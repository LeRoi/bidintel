import flask, json, os
from flask import jsonify, Flask, Response, request, render_template

import lib.structure as struct
import lib.sql_interface as sql
from lib.constants import *
from lib.logic import *

app = Flask(__name__)
debug = True
database_src = 'dev/data/bidintel_dev.db'
#database_src = DATABASE_PATH

full_course_reference = {}
for result in sql.fetch_table(database_src, sql.Tables.FULL_COURSES):
    full_course_reference[result[0]] = {
        'c_id': result[1],
        'p_ids': csv_to_ids(result[2])}
full_course_reference_json = json.dumps({'fullcourses':
    [{'id': key,
      'cid': full_course_reference[key]['c_id'],
      'pids': full_course_reference[key]['p_ids']} \
     for key in full_course_reference]})

professors_reference = []
for result in sql.fetch_table(database_src, sql.Tables.PROFESSORS):
    professors_reference.append({'id': result[0],
                                 'name': result[1]})
professors_reference_json = json.dumps({'professors': professors_reference})

course_reference = {}
for result in sql.fetch_table(database_src, sql.Tables.COURSES):
    course_reference[result[0]] = {
        'type': result[1],
        'name': result[2]}
course_reference_json = json.dumps({'courses':
    [{'id': key,
      'type': course_reference[key]['type'],
      'name': course_reference[key]['name']} \
     for key in course_reference]})

def add_row(table, data):
    db = sql.sql_connect(database_src)
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
    return professors_reference_json

@app.route('/data/courses')
def courses():
    return course_reference_json

@app.route('/data/fullcourses')
def fullcourses():
    return full_course_reference_json

@app.route('/bid')
def bid():
    return Response(render_template('bid.html'))

@app.route('/stats')
def stats():
    return Response(render_template('stats.html'))

@app.route('/submit_rows', methods=['POST'])
def submit_rows():
    form = json.loads(request.data)
    table = form['table']
    db = sql.sql_connect(database_src)
    next_id = sql.get_next_id(db, table)
    sql.update_next_id(db, table, next_id + 1)
    db.close()
    add_row(table, format_data(table, form, next_id))
    return json.dumps({'status':'OK'})

@app.route('/get_bid_stats', methods=['GET', 'POST'])
def get_bid_stats():
    ## TODO: (P1) Segment only by included items.
    form = json.loads(request.data)
    #print form

    startDate = date_to_int(form['startTerm'], form['startYear'])
    endDate = date_to_int(form['endTerm'], form['endYear'])

    c_id = form['course']['id'] if form['course'] else None
    p_id = form['professor']['id'] if form['professor'] else None
    c_type = form['courseType'] # Could be -1 or a real value.
    
    full_ids = []
    for k in full_course_reference:
        v = full_course_reference[k]
        valid_term = c_type == -1 or \
                     course_reference[v['c_id']]['type'] == c_type
        valid_course = not c_id or v['c_id'] == c_id
        valid_professor = not p_id or p_id in v['p_ids']
        if valid_term and valid_course and valid_professor:
            full_ids.append(k)

    results = {}
    for result in sql.fetch_table(database_src, sql.Tables.BIDS):
        bidDate = date_to_int(result[2], result[3])
        #print 'Comparing start: %d\tend: %d\tvalue: %d' % (startDate, endDate, bidDate)
        if result[1] in full_ids and bidDate >= startDate and \
           bidDate <= endDate:
            #print '\tbidDate is within range!'
            #print 'Start: %d\tEnd: %d\tActual: %d' % (startDate, endDate, bidDate)
            if result[4] not in results:
                results[result[4]] = 0
            results[result[4]] += 1
    #print results
    return json.dumps(results)

@app.route('/submit_bids', methods=['POST'])
def submit_bids():
    #print 'Received data: %s' % str(request.data)
    form = json.loads(request.data)
    bid_data = form['bids']
    user_id = 3
    db = sql.sql_connect(database_src)
    cursor = db.cursor()
    next_bid_id = sql.get_next_id(db, sql.Tables.BIDS)
    for i in range(len(bid_data)):
        bid = bid_data[i]
        #print bid
        ## May need to add bid batch concept for retrieval
        ## Or just have different columns in user tables...
        course_id = bid['selectedCourse']['id']
        prof_id = bid['selectedProfessor']['id']
        full_id = -1
        for k in full_course_reference:
            v = full_course_reference[k]
            if v['c_id'] == course_id and prof_id in v['p_ids']:
                full_id = k
        got_in = int(bid['gotIn'] if 'gotIn' in bid else False)
        sql.query(cursor, sql.SQL.INSERT.INSERT_BID %
                  (next_bid_id, full_id, bid['term'],
                   form['year'] + (0 if bid['term'] == struct.Term.FALL else 1),
                   i + 1, got_in, -1))
        next_bid_id += 1
    sql.query(cursor, 'UPDATE nextIds SET nextId = %d WHERE id = %d' %
          (next_bid_id, sql.Tables.BIDS))
    db.commit()
    db.close()
    return json.dumps({'status':'OK'})

## The database should always already exist.
## setup_server()
if __name__ == '__main_':
    port = int(os.envion.get('PORT', Server.PORT))
    app.run(host=Server.HOST, port=port, debug=debug)

    
