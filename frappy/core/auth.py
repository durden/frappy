"""
Authentication module to easily append different types of authentication to API
calls
"""

from __future__ import print_function

try:
    import urllib.parse as urllib_parse
    from base64 import encodebytes
except ImportError:
    import urllib as urllib_parse
    from base64 import encodestring as encodebytes

from time import time
from random import getrandbits

import hashlib
import hmac
import base64


class Auth(object):
    """
    ABC for Authenticator objects.
    """

    def __init__(self):
        """"""
        pass

    def generate_headers(self):
        """Generates headers which should be added to the request if required
        by the authentication scheme in use."""

        return {}


class UserPassAuth(Auth):
    """
    Basic auth authentication using email/username and
    password. Deprecated.
    """

    def __init__(self, username, password):
        self.username = username
        self.password = password

        Auth.__init__(self)

    def generate_headers(self):
        return {b"Authorization": b"Basic " + encodebytes(
                    ("%s:%s" % (self.username, self.password)).encode('utf8'))
                    .strip(b'\n')}


class NoAuth(Auth):
    """
    No authentication authenticator.
    """
    pass


class OAuth(Auth):
    """
    An OAuth authenticator.
    """
    def __init__(self, token, token_secret, consumer_key, consumer_secret):
        """
        Create the authenticator. If you are in the initial stages of
        the OAuth dance and don't yet have a token or token_secret,
        pass empty strings for these params.
        """

        self.token = token
        self.token_secret = token_secret
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        Auth.__init__(self)

    def encode_params(self, base_url, method, params):
        """Encode oauth keys and params in format suitable for uri"""

        params = params.copy()

        if self.token:
            params['oauth_token'] = self.token

        params['oauth_consumer_key'] = self.consumer_key
        params['oauth_signature_method'] = 'HMAC-SHA1'
        params['oauth_version'] = '1.0'
        params['oauth_timestamp'] = str(int(time()))
        params['oauth_nonce'] = str(getrandbits(64))

        enc_params = urlencode_noplus(sorted(params.items()))

        key = self.consumer_secret + "&" + \
                        urllib_parse.quote(self.token_secret, '')

        message = '&'.join(
            urllib_parse.quote(i, '') for i in [method.upper(), base_url,
                                                enc_params])

        signature = (base64.b64encode(hmac.new(
                    key.encode('ascii'), message.encode('ascii'), hashlib.sha1)
                                      .digest()))
        return enc_params + "&" + "oauth_signature=" + \
                urllib_parse.quote(signature, '')


    @staticmethod
    def write_token_file(filename, oauth_token, oauth_token_secret):
        """
        Write a token file to hold the oauth token and oauth token secret.
        """

        oauth_file = open(filename, 'w')
        print(oauth_token, file=oauth_file)
        print(oauth_token_secret, file=oauth_file)
        oauth_file.close()


    @staticmethod
    def read_token_file(filename):
        """
        Read a token file and return the oauth token and oauth token secret.
        """

        token_file = open(filename)
        return token_file.readline().strip(), token_file.readline().strip()


def urlencode_noplus(query):
    """
    Apparently contrary to the HTTP RFCs, spaces in arguments must be encoded
    as %20 rather than '+' when constructing an OAuth signature (and therefore
    also in the request itself.) So here is a specialized version which does
    exactly that.
    """

    if hasattr(query, "items"):
        # mapping objects
        query = list(query.items())

    encoded_bits = []
    for name, val in query:
        # and do unicode here while we are at it...
        if isinstance(name, str):
            name = name.encode('utf-8')
        else:
            name = str(name)

        if isinstance(val, str):
            val = val.encode('utf-8')
        else:
            val = str(val)
        encoded_bits.append("%s=%s" % (urllib_parse.quote(name, ""),
                            urllib_parse.quote(val, "")))

    return "&".join(encoded_bits)
