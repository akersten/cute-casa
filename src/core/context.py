# ######################################################################################################################
# THe global context for the CuteCasa application. This object tracks the global state and singletons for an instance.
# ######################################################################################################################

from core.web.client import run_integrity_checks


class Context:
    """
    The CuteCasa global context for this instance, to track state and singletons.
    """

    def __init__(self):

        # Singleton initialization.
        self.Zdb = None
        self.Yoer = None

        pass

    def before_request(self):
        """
        Do any bringup for things that we need during a request.
        """

        # TODO: find better subscripts of g to set things on. These should actually all be accessed via the context
        # anyway so there shouldn't be much to do here. THis context object should have instance methods like get_db()
        # or similar to get these things. We would just have to do the connecting to the database here using the local
        # reference we already have.
        g.db = connect_db()

        # Add singleton references to dog object.
        g.dog = lambda: None
        g.dog.zdb = S_Zdb
        g.dog.yoer = S_Yoer


        run_integrity_checks()

    def teardown_request(self, exception):
        """
        Take care of any teardown after a request.
        """
        db = getattr(g, 'db', None)
            if db is not None:
                db.close()