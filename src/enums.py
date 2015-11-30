# ######################################################################################################################
# Enums
#
# Certain items in the database are constrained to numeric values representing a category or type. These integer values
# are stored in the SQL as names beginning with e_
#
# ######################################################################################################################

from enum import IntEnum

class e_household_type(IntEnum):
    apartment = 1
    house = 2

class e_household_relation(IntEnum):
    member = 1
    admin = 2
