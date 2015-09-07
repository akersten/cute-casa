# ######################################################################################################################
# Certain bills associated with a household are running tallies resolved at the end of each month (like a grocery bill).
# ######################################################################################################################

from flask import flash, render_template

def billsplit():
    """
    Render the billsplit view.
    :return: The render template.
    """
    flash("yes it's working")
    flash("aw yeah")
    return render_template('billing/billsplit.html')
