# Convenience methods to do things to the client request, like send a failure page, or format ajax json.


def failRequest(code, message):
    """
    Aborts a Flask request with the specified error code and message. Logs the event to the user log.
    :param code: The HTTP code to which this failure corresponds.
    :param message: The problem with the request.
    :return: A redirect to an error page.
    """
    if not enums.contains(enums.e_http_codes, code):
        failRequest(enums.e_http_codes.internal_error, 'Invalid HTTP code specified while processing another error.')

    src.logger.logUser()
    if request.method == 'POST':
        # Can't redirect to the error page - it was an Ajax request! Send some error JSON instead.
        pass
    else:
        return redirect(url_for(message))
