from enum import IntEnum
from constants import *
from logic import *

class NextId(IntEnum):
    PROFESSOR = 0
    COURSE = 1
    FULL_COURSE = 2
    USER = 3
    BID = 4

## TODO: see how useful any part of this file is from here and below
##class User():
##    def __init__(self, u_id, bids=[]):
##        self.id = u_id
##        self.bids = bids
##
##    def has_bids(self):
##        return len(self.bids) > 0

class Course():
    def __init__(self, c_id, name, course_type):
        self.id = c_id
        self.name = name
        self.type = course_type

    def __hash__(self):
        ## This is fine so long as there are not more than ~8000 courses.
        return hash(self.name) * 100000 + self.type + self.id * 10

    def __eq__(self, other):
        return other and other.name == self.name and \
               other.type == self.type and other.id == self.id

class FullCourse():
    def __init__(self, _id, c_id, p_ids):
        self.id = _id
        self.c_id = c_id
        self.p_ids = p_ids

    def __hash__(self):
        ## This assumes there is only one p_id associated, maybe two.
        ## This also assumes there are not more than ~8000 courses.
        r = self.c_id
        for i in range(len(self.p_ids)):
            r += self.p_ids[i] * (1000 ** (i + 1))
        return r

    def __eq__(self, other):
        return other and other.c_id == self.c_id and \
               other.p_ids == self.p_ids

class CTerm():
    def __init__(self, year, term):
        self.year = year ## int
        self.term = term ## Term

class Bid():
    def __init__(self, b_id, term, year, position):
        self.id = b_id ## int:    unique course id
        self.term = term ## Term
        self.year = year ## int
        self.position = position ## int

class Professor():
    def __init__(self, p_id, name):
        self.id = p_id ## int:    unique professor id
        self.name = name ## string: full professor name

## Is this used anywhere?
def email_to_bid_data(email):
    lines = email.split('\n')
    bids = []
    for line in lines:
        parts = line.split('\t')
        components = []
        for part in parts:
            subparts = [s.strip() for s in part.split('  ')]
            components.extend(subparts)
        components = [c for c in components if c]
        if len(components) > 0:
            bids.append(components)
    return bids
