from flask import flash, render_template, session

from src import logger
from src import enums

def billsplit():
    """
    Certain bills associated with a household are running tallies resolved at the end of each month (like a grocery
    bill). This is a tool to split them between members of a household.
    Render the billsplit view.
    :return: The render template.
    """
    logger.logAdmin('danger noodles', session['id'], enums.e_admin_log_event_level.critical)
    return render_template('billing/billsplit.html')
