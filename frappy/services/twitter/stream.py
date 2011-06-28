"""
Small wrapper around Twitter streaming API
"""

import urllib2
import json

from frappy.core.api import APIHTTPError, DefaultVersion
from frappy.services.twitter.twitter import Twitter


class TwitterJSONIter(object):
    """Iterable JSON object"""

    def __init__(self, req, arg_data):
        self.decoder = json.JSONDecoder()
        self.req = req
        self.buf = b""
        self.arg_data = arg_data

    def __iter__(self):
        while True:
            self.buf += self.req.read(1024)
            try:
                utf8_buf = self.buf.decode('utf8').lstrip()
                res, ptr = self.decoder.raw_decode(utf8_buf)
                self.buf = utf8_buf[ptr:].encode('utf8')
                yield self.buf
            except ValueError as e:
                continue
            except urllib2.HTTPError as err:
                raise APIHTTPError(err.getcode(), self.req.get_full_url(),
                                   self.arg_data)


class TwitterStream(Twitter):
    """
    Interface to the Twitter Stream API (stream.twitter.com). This can
    be used pretty much the same as the Twitter class except the
    result of calling a method will be an iterator that yields objects
    decoded from the stream. For example::

    twitter_stream = TwitterStream(auth=UserPassAuth('joe', 'joespassword'))
    iterator = twitter_stream.statuses.sample()

    for tweet in iterator:
        ...do something with this tweet...

    The iterator will yield tweets forever and ever (until the stream
    breaks at which point it raises a TwitterHTTPError.)
    """
    def __init__(self, domain="stream.twitter.com", secure=False, auth=None):
        Twitter.__init__(self, auth=auth, req_format="json", domain=domain,
                         secure=secure, api_version=DefaultVersion)

    def __call__(self, *args, **kwargs):
        """
        Finish building uri with leftover arguments, append authentication, and
        send off request
        """

        kwargs = self._build_uri(**kwargs)

        # Wrapper for child classes to customize creation of the uri
        kwargs = self.service_build_uri(*args, **kwargs)

        # Append any authentication specified to request
        arg_data = self._handle_auth(**kwargs)

        # Normally self.uri would be cleared between each __call__ to allow for
        # new requests and previous request location would be in requested_uri,
        # but can't change self.uri now since we're hitting the same location
        # everytime for streaming...so just set requested_uri to try and stay
        # consistent with other supported services
        self.requested_uri = self.uri

        resp = self._send_request(arg_data)

        return self._handle_response(resp, arg_data)

    def _send_request(self, arg_data):
        """Send request to self.uri"""
        try:
            req = urllib2.Request(self.uri, arg_data, self.headers['request'])
            return urllib2.urlopen(req)
        except (urllib2.HTTPError, urllib2.URLError), err:
            raise APIHTTPError(err.getcode(), req.get_full_url(), arg_data)

    def _handle_response(self, resp, arg_data):
        return iter(TwitterJSONIter(resp, arg_data))
