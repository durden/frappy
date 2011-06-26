import urllib2
import json

from frappy.core.api import APIHTTPError, DEFAULT_VERSION
from twitter import Twitter

class TwitterJSONIter(object):

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
            except urllib2.HTTPError as e:
                raise APIHTTPError(e, self.uri, self.req_format, self.arg_data)

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
                         secure=secure, api_version=DEFAULT_VERSION)

    def __call__(self, *args, **kwargs):
        """
        Finish building uri with leftover arguments, append authentication, and
        send off request
        """

        self._build_uri(*args, **kwargs)

        # Normally self.uri would be cleared between each __call__ to allow for
        # new requests and previous request location would be in requested_uri,
        # but can't change self.uri now since we're hitting the same location
        # everytime for streaming...so just set requested_uri to try and stay
        # consistent with other supported services
        self.requested_uri = self.uri

        print 'here'
        return self._handle_response(None, self.arg_data)

    def _handle_response(self, req, arg_data):
        req = urllib2.Request(self.uri, self.body, self.request_headers)
        response = urllib2.urlopen(req)
        print 'handline'
        return iter(TwitterJSONIter(response, arg_data))
