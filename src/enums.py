# ######################################################################################################################
# Enums
#
# Certain items in the database are constrained to numeric values representing a category or type. These integer values
# are stored in the SQL as names beginning with e_
#
# ######################################################################################################################

from enum import IntEnum

def contains(haystack, needle):
    """
    Determines if a given enum contains a given value.
    :param haystack: The enum to search.
    :param needle: The value to find.
    :return: True if the given enum contained the given value. False otherwise.
    """
    return int(needle) in [e.value for e in haystack]

class e_household_type(IntEnum):
    apartment = 1
    house = 2

class e_household_relation(IntEnum):
    member = 1
    admin = 2

class e_admin_log_event_level(IntEnum):
    info = 1
    warning = 2
    critical = 3

class e_user_authority(IntEnum):
    """
    The user authority defines the administrative rights of a user over the particular cutecasa instance.
    """
    user = 1,
    admin = 2