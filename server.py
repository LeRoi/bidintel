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

## Probably should move these to another file.
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

user_reference = {}
for result in sql.fetch_table(database_src, sql.Tables.USERS):
    print result, len(result)
    data_map = {'id': result[0],
                'year': result[2],
                'is_transfer': result[3]}
    bid_map = {}
    for item in BidType:
        ## 3 is the index of the first bid item.
        bid_map[item.value] = result[item.value + 4]
    data_map.update(year_to_requirements(result[2], result[3], bid_map))
    user_reference[result[1]] = data_map

##def add_row(table, data):
##    db = sql.sql_connect(database_src)
##    sql.insert_row(db, table, data)
##    db.close()

## Move this to another file - can also remove for prod
##def format_data(table, form, next_id):
##    print '\tFormatting (ID=%d) %s for Table %s' % (next_id, str(form), str(sql.Tables(table)))
##    if table == sql.Tables.PROFESSORS:
##        return struct.Professor(next_id, form['professor'])
##    elif table == sql.Tables.COURSES:
##        return struct.Course(next_id, form['course_name'],
##                                    int(form['course_type']))
##    elif table == sql.Tables.FULL_COURSES:
##        return struct.FullCourse(next_id, int(form['course_id']),
##                                        csv_to_ids(form['professor_ids']))
##    elif table == sql.Tables.USERS:
##        return struct.User(next_id, csv_to_ids(['bids']))
##    elif table == sql.Tables.BIDS:
##        return struct.Bid(next_id, int(form['term']),
##                                 int(form['year']), int(form['position']))
  
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

@app.route('/data/user', methods=['POST'])
def user():
    form = json.loads(request.data)
    ## Verify the logged in user is the requested user.
    ## Get user email
    user_email = 'kxia@jd20.law.harvard.edu'
    user_data = user_reference[user_email]
    return json.dumps({'userdata': user_data})

@app.route('/bid')
def bid():
    return Response(render_template('bid.html'))

@app.route('/stats')
def stats():
    return Response(render_template('stats.html'))

@app.route('/profile')
def profile():
    return Response(render_template('profile.html'))

@app.route('/logout')
def logout():
    return Response(render_template('logout.html'))

##@app.route('/submit_rows', methods=['POST'])
##def submit_rows():
##    form = json.loads(request.data)
##    table = form['table']
##    db = sql.sql_connect(database_src)
##    next_id = sql.get_next_id(db, table)
##    sql.update_next_id(db, table, next_id + 1)
##    db.close()
##    add_row(table, format_data(table, form, next_id))
##    return json.dumps({'status':'OK'})

@app.route('/get_bid_stats', methods=['GET', 'POST'])
def get_bid_stats():
    ## TODO: (P1) Segment only by included items. (kind of done).
    ## TODO: (P2) Cache bids.
    ## TODO: (P0) Check user status against requirements.
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

    results = {'bidCounts':{}, 'bidSuccesses':{}, 'bidWaitlists':{}}
    for result in sql.fetch_table(database_src, sql.Tables.BIDS):
        bidDate = date_to_int(result[2], result[3])
        #print 'Comparing start: %d\tend: %d\tvalue: %d' % (startDate, endDate, bidDate)
        if result[1] in full_ids and bidDate >= startDate and \
           bidDate <= endDate:
            target = None
            if result[5] == struct.GotIn.FROM_BIDS:
                target = 'bidSuccesses'
            if result[5] == struct.GotIn.OFF_WAITLIST:
                target = 'bidWaitlists'
            if target:
                if result[4] not in results[target]:
                    results[target][result[4]] = 0
                results[target][result[4]] += 1
            #print '\tbidDate is within range!'
            #print 'Start: %d\tEnd: %d\tActual: %d' % (startDate, endDate, bidDate)
            if result[4] not in results['bidCounts']:
                results['bidCounts'][result[4]] = 0
            results['bidCounts'][result[4]] += 1
    #print results
    return json.dumps(results)

@app.route('/submit_bids', methods=['POST'])
def submit_bids():
    ## TODO: (P0) Update user's submissions.
    print 'Received data: %s' % str(request.data)
    form = json.loads(request.data)
    bid_data = form['bids']
    ## Get user email; verify user.
    email = 'kxia@jd20.law.harvard.edu'
    user_id = 999#form['id']
    user_year = user_reference[email]['year']

    update_column = form_to_update_column(form)
    col_name = column_to_name(update_column)
    update_ids = []
    
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
        year = (3 - form['classYear']) + user_year
        sql.query(cursor, sql.SQL.INSERT.INSERT_BID %
                  (next_bid_id, full_id, bid['term'],
                   year + (0 if bid['term'] == Term.FALL else 1),
                   i + 1, got_in, -1))
        update_ids.append(next_bid_id)
        next_bid_id += 1
    sql.query(cursor, 'UPDATE nextIds SET nextId = %d WHERE id = %d' %
          (next_bid_id, sql.Tables.BIDS))
    sql.query(cursor, 'UPDATE users SET %s = "%s" WHERE id = %d' %
              (col_name, ids_to_csv(update_ids), user_id))
    db.commit()
    db.close()

    user_reference[email][update_column.value] = 0
    
    return json.dumps({'status':'OK'})

## The database should always already exist.
## setup_server()
if __name__ == '__main_':
    port = int(os.envion.get('PORT', Server.PORT))
    app.run(host=Server.HOST, port=port, debug=debug)

    
