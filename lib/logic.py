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
def year_to_requirements(grad_year, bid_data):
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
