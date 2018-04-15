import datetime
from enum import IntEnum
DATABASE_PATH = 'data/bidintel.db'

class Term(IntEnum):
    FALL = 0
    WINTER = 1
    SPRING = 2

class CourseType(IntEnum):
    GENERAL_ELECTIVE = 0
    MULTISECTION = 1
    CLINIC = 2
    INTERNATIONAL = 3
    LEGAL_PROFESSION = 4

class BidType(IntEnum):
    INTERNATIONAL_1L = 0
    SPRING_1L = 1
    CLINIC_2L = 2
    MULTISECTION_2L = 3
    FALL_2L = 4
    WINTER_2L = 5
    SPRING_2L = 6
    CLINIC_3L = 7
    MULTISECTION_3L = 8
    LEGAL_PROFESSION_3L = 9
    FALL_3L = 10
    WINTER_3L = 11
    SPRING_3L = 12

## The month, date should be set to the time bids open
## for the current year.
bid_type_to_year_month = {
    BidType.INTERNATIONAL_1L: datetime.date(1, 10, 30),
    BidType.SPRING_1L: datetime.date(1, 11, 7),
    BidType.CLINIC_2L: datetime.date(2, 3, 29),
    BidType.MULTISECTION_2L: datetime.date(2, 4, 5),
    BidType.FALL_2L: datetime.date(2, 4, 13),
    BidType.WINTER_2L: datetime.date(2, 9, 1),
    BidType.SPRING_2L: datetime.date(2, 9, 1),
    BidType.CLINIC_3L: datetime.date(3, 3, 29),
    BidType.MULTISECTION_3L: datetime.date(3, 4, 5),
    BidType.LEGAL_PROFESSION_3L: datetime.date(3, 4, 9),
    BidType.FALL_3L: datetime.date(3, 4, 13),
    BidType.WINTER_3L: datetime.date(3, 9, 1),
    BidType.SPRING_3L: datetime.date(3, 9, 1)
}

## These should change with the bid season.
required_1L = [BidType.MULTISECTION_2L]
required_2L = [BidType.FALL_2L]
required_3L = [BidType.FALL_3L]
