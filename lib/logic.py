import datetime
from constants import *

def to_ascii_simple(s):
    return s.decode('utf-8').encode('ascii', 'ignore')

def to_ascii(form):
    result = {}
    for k in form:
        result[k] = str(form[k].decode('utf-8').encode('ascii'))
    return result

def ids_to_csv(ids):
    return ','.join([str(_id) for _id in ids])

def csv_to_ids(csv):
    return [int(_id) for _id in csv.split(',')]

## TODO: (P3) Remove this hack to put Fall 2018 after Spring 2018.
def date_to_int(term, year):
    return year * 10 + term + (3 if term == 0 else 0)

## Map a list of bids and None to a list of values of if the bid
## data has been submitted / needs to be submitted.
## 0 = submitted, 1 = missing, 2 = required, 3 = unavailable.
## TODO: (P2) Add transfer student logic
def year_to_requirements(grad_year, is_transfer, bid_data):
    today = datetime.datetime.now()
    year = 4 - (grad_year - today.year)
    bid_requirements = {}
    for k in BidType:
        bid_requirements[k.value] = 0 if bid_data[k.value] else 1
    
    ## If you are an alum from the past 3 years, you MUST still provide 3L data.
    ## Alums from further back may not have used the same bid system.
    law_school_year = year
    if today.month < 5: # May
        law_school_year -= 1
    requirements = []
    if law_school_year == 1:
        requirements = required_1L
    elif law_school_year == 2:
        requirements = required_2L
    elif law_school_year >= 3 and law_school_year < 6:
        requirements = required_3L
        
    for requirement in requirements:
        if is_transfer and requirement <= BidType.FALL_2L:
            continue
        ## Submitted -> Submitted; Missing -> Required
        bid_requirements[requirement.value] *= 2
    
    if year <= 0: # No further bids
        return bid_requirements

    relative_today = datetime.date(year, today.month, today.day)
    for requirement in bid_requirements:
        target = bid_type_to_year_month[BidType(requirement)]
        if relative_today < target:
            bid_requirements[requirement] = 3

    return bid_requirements

def form_to_update_column(form):
    courseType = form['courseType']
    term = form['term']
    year = form['classYear'] + 1

    if courseType == CourseType.INTERNATIONAL:
        return BidType.INTERNATIONAL_1L
    if courseType == CourseType.LEGAL_PROFESSION:
        return BidType.LEGAL_PROFESSION_3L

    general_elective = {
        2: {Term.FALL: BidType.FALL_2L,
            Term.WINTER: BidType.WINTER_2L,
            Term.SPRING: BidType.SPRING_2L},
        3: {Term.FALL: BidType.FALL_3L,
            Term.WINTER: BidType.WINTER_3L,
            Term.SPRING: BidType.SPRING_3L}}
    if courseType == CourseType.GENERAL_ELECTIVE:
        return BidType.SPRING_1L if year == 1 else general_elective[year][term]
    if courseType == CourseType.CLINIC:
        return BidType.CLINIC_2L if year == 2 else BidType.CLINIC_3L
    if courseType == CourseType.MULTISECTION:
        return BidType.MULTISECTION_2L if year == 2 else BidType.MULTISECTION_3L

def column_to_name(bidType):
    fields = {BidType.INTERNATIONAL_1L: 'intl_1L',
        BidType.SPRING_1L: 'spring_1L',
        BidType.CLINIC_2L: 'clinic_2L',
        BidType.MULTISECTION_2L: 'multisection_2L',
        BidType.FALL_2L: 'fall_2L',
        BidType.WINTER_2L: 'winter_2L',
        BidType.SPRING_2L: 'spring_2L',
        BidType.CLINIC_3L: 'clinic_3L',
        BidType.MULTISECTION_3L: 'multisection_3L',
        BidType.LEGAL_PROFESSION_3L: 'legalprof_3L',
        BidType.FALL_3L: 'fall_3L',
        BidType.WINTER_3L: 'winter_3L',
        BidType.SPRING_3L: 'spring_3L'}
    return fields[bidType]
            
def compute_stats(bids, form, full_course_reference, course_reference):
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
    #print len(bids)
    for result in bids:
        bidDate = date_to_int(result[2], result[3])
        #print bidDate, startDate, endDate
        #print 'Comparing start: %d\tend: %d\tvalue: %d' % (startDate, endDate, bidDate)
        if result[1] in full_ids and bidDate >= startDate and \
           bidDate <= endDate:
            target = None
            if result[5] == GotIn.FROM_BIDS:
                target = 'bidSuccesses'
            if result[5] == GotIn.OFF_WAITLIST:
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
    return results
    
