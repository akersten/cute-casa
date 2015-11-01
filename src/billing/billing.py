from flask import flash, render_template


def billsplit():
    """
    Certain bills associated with a household are running tallies resolved at the end of each month (like a grocery
    bill). This is a tool to split them between members of a household.
    Render the billsplit view.
    :return: The render template.
    """
    return render_template('billing/billsplit.html')
