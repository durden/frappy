"""
Authentication module to easily append different types of authentication to API
calls
"""

try:
    import urllib.parse as urllib_parse
    from base64 import encodebytes
except ImportError:
    import urllib as urllib_parse
    from base64 import encodestring as encodebytes


class Auth(object):
    """
    ABC for Authenticator objects.
    """

    def generate_headers(self):
        """Generates headers which should be added to the request if required
        by the authentication scheme in use."""
        raise NotImplementedError()


class UserPassAuth(Auth):
    """
    Basic auth authentication using email/username and
    password. Deprecated.
    """
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def generate_headers(self):
        return {b"Authorization": b"Basic " + encodebytes(
                    ("%s:%s" % (self.username, self.password)).encode('utf8'))
                    .strip(b'\n')}


class NoAuth(Auth):
    """
    No authentication authenticator.
    """
    def __init__(self):
        pass

    def generate_headers(self):
        return {}
