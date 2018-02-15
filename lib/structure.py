from enum import IntEnum

class Season(IntEnum):
    FALL = 0
    WINTER = 1
    SPRING = 2

class BidType(IntEnum):
    GENERAL = 0
    CLINIC = 1
    INTL = 2
    SPRING_1L = 3

class Course():
    def __init__(self, c_id, n_id, name, p_id, bid_type):
        self.c_id = c_id ## int:    unique course id
        self.n_id = n_id ## string: course name code
        self.name = name ## string: full course name
        self.p_id = p_id ## int:    professor id
        self.bid_type = bid_type ## BidType

class Term():
    def __init__(self, year, season):
        self.year = year ## int
        self.season = season ## Season

class Bid():
    def __init__(self, c_id, term, u_id, position):
        self.c_id = c_id ## int:    unique course id
        self.term = term ## Term
        self.u_id = u_id ## int:    unique user id
        self.position = position ## int

class Professor():
    def __init__(self, p_id, name):
        self.p_id = p_id ## int:    unique professor id
        self.name = name ## string: full professor name
