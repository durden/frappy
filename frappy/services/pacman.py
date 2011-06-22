from frappy.core.api import APICall
from frappy.core.auth import NoAuth


class _DEFAULT(object):
    pass


class Pacman(APICall):
    """
    """
    def __init__(self, format="json", domain="127.0.0.1:8000", secure=False,
                 auth=None, api_version=_DEFAULT):

        APICall.__init__(self, auth=auth, format=format, domain=domain,
                         secure=secure)
