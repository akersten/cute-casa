
def getUserRow(userId):
    """
    Get a user row based on their id.
    :param userId: The user id to look up.
    :return: The database row for this user.
    """
    user = db.getRow('users', userId)
    return user


def getUserDisplayname(userId):
    """
    Convert a user id into their display name.
    :param userId: The user id to look up.
    :return: The display name for this user.
    """
    u = g.dog.zdb.getUser(userId)
    if u is None:
        return None
    return u.displayname


def checkLogin():
    """Check that the user is logged in and transmit an HTTP error if not."""
    if not session.get('logged_in'):
        abort(401)

def checkAdmin():
    """Check that the user is logged in as a CuteCasa admin."""
    checkLogin()
    if not session['admin']:
        abort(401, "you are not an admin")



def isCuteCasaAdmin(userId):
    """
    Checks whether the given user is a CuteCasa administrator for this instance.
    :param userId: THe user id to check.
    :return: True if the specified user is a CuteCasa admin, False otherwise.
    """
    return db.getValue('users', 'e_user_authority', userId) == 2



# ######################################################################################################################
# User object representation
# ######################################################################################################################

import persistent, transaction

class User(persistent.Persistent):

    def __init__(self, id, displayname):
        if not type(id) is str:
            raise TypeError('A user id must be of str type.')

        if not type(displayname) is str:
            raise TypeError('A displayname must be of str type.')

        if len(id) == 0:
            raise ValueError('A user id must be non-zero length.')

        if len(displayname) == 0:
            raise ValueError('A displayname must be non-zero length.')

        self.id = id
        self.displayname = displayname

        self.yoUsername = ""
        self.favoriteColor = "#E0E0FF"
        self.cellphone =""


    @property
    def displayname(self):
        return self._displayname
    @displayname.setter
    def displayname(self, displayname):
        self._displayname = displayname
        transaction.commit()

    @property
    def yoUsername(self):
        return self._yoUsername
    @yoUsername.setter
    def yoUsername(self, yoUsername):
        self._yoUsername = yoUsername
        transaction.commit()


    @property
    def favoriteColor(self):
        return self._favoriteColor
    @favoriteColor.setter
    def favoriteColor(self, favoriteColor):
        self._favoriteColor = favoriteColor
        transaction.commit()

    @property
    def cellphone(self):
        return self._cellphone
    @cellphone.setter
    def cellphone(self, cellphone):
        self._cellphone = cellphone
        transaction.commit()