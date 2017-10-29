
class RestrictedAccessError(Exception):

    def __init__(self):
        super(RestrictedAccessError, self).__init__("Access to restricted files denied!")


class BadRequestError(Exception):

    def __init__(self):
        super(BadRequestError, self).__init__("Invalid request. Check URI and headers!")