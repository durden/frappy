"""
Base implementation of Frappy framework.
"""


try:
    import urllib.request as urllib_request
    import urllib.error as urllib_error
except ImportError:
    import urllib2 as urllib_request
    import urllib2 as urllib_error

try:
    import json
except ImportError:
    import simplejson as json


class APIError(Exception):
    """
    Base Exception thrown by the APICall object when there is a
    general error interacting with the API.
    """

    pass


class APIHTTPError(APIError):
    """
    Base Exception thrown by the APICall object when there is a
    general error interacting with the API.
    """

    def __init__(self, e, uri, format, uriparts):
        """Initalize error object"""

        self.e = e
        self.uri = uri
        self.format = format
        self.uriparts = uriparts

    def __str__(self):
        """Stringify error"""

        return (
            "API sent status %i for URL: %s.%s using parameters: "
            "(%s)\ndetails: %s" % (
                self.e.code, self.uri, self.format, self.uriparts,
                self.e.fp.read()))


class APICall(object):
    """
    Base implementation of API call.

    This class is very generic and should provide most of the send/retrieve
    functionality for API access.  Thus, you should be able to subclass it,
    and provide a basic __init__ method.
    """

    def __init__(self, auth, format, domain, uriparts=None,
                 secure=True):

        """Initialize call API object"""

        self.auth = auth
        self.format = format
        self.domain = domain
        self.uri = ""
        self.secure = secure

        self.response = None
        self.request_headers = {}
        self.response_headers = None

        self.method = "GET"
        self.body = None
        self.arg_data = ""

        self.uriparts = uriparts
        if self.uriparts is None:
            self.uriparts = ()

    def __getattr__(self, k):
        """
        Look for attribute k in base object, other wise append to uri

        This is allows for a very powerful and expressive syntax for creating
        API calls that map closely to the uri they query.  For example a
        Twitter call: <object>.statuses.public_timeline() will map to
        <domain>/statuses/public_timeline.
        """

        try:
            return object.__getattr__(self, k)
        except AttributeError:
            self.uriparts += (k,)
            return self

    def _build_uri(self, **kwargs):
        """Build up the final uri for the request"""

        uriparts = []
        for uripart in self.uriparts:
            # If this part matches a keyword argument, use the
            # supplied value otherwise, just use the part.
            uriparts.append(str(kwargs.pop(uripart, uripart)))

        self.uri += '/'.join(uriparts)

        # FIXME
        #for action in POST_ACTIONS:
            #if uri.endswith(action):
                #self.method = "POST"
                #break

        # If an id kwarg is present and there is no id to fill in in
        # the list of uriparts, assume the id goes at the end.
        id = kwargs.pop('id', None)
        if id:
            self.uri += "/%s" % (id)

        secure_str = ''
        if self.secure:
            secure_str = 's'

        dot = ""
        if self.format:
            dot = "."

        # FIXME: Don't assume API uses .json or .xml format, maybe it always
        # just returns the self.format
        #self.uri = "http%s://%s/%s" % (secure_str, self.domain, self.uri)

        self.uri = "http%s://%s/%s%s%s" % (
                    secure_str, self.domain, self.uri, dot, self.format)


        # Append any authentication specified to request
        self._handle_auth(**kwargs)

    def _handle_auth(self, **kwargs):
        """
        Attach requested authentication to request and encoded body and
        parameters
        """

        if self.auth:
            self.request_headers.update(self.auth.generate_headers())
            self.arg_data = self.auth.encode_params(self.uri, self.method,
                                                    kwargs)

            if self.method == 'GET':
                self.uri += '?' + self.arg_data
            else:
                self.body = self.arg_data.encode('utf8')

    def __call__(self, **kwargs):
        """
        Finish building uri with leftover arguments, append authentication, and
        send off request
        """

        self._build_uri(**kwargs)

        req = urllib_request.Request(self.uri, self.body, self.request_headers)

        return self._handle_response(req, self.arg_data)

    def _handle_response(self, req, arg_data):
        """Verify response code and format data accordingly"""

        try:
            handle = urllib_request.urlopen(req)
            self.response_headers = handle.headers

            if "json" == self.format:
                self.response = json.loads(handle.read().decode('utf8'))
            else:
                self.response = handle.read().decode('utf8')

            return self
        except urllib_error.HTTPError as e:
            if (e.code == 304):
                return []
            else:
                raise APIHTTPError(e, self.uri, self.format, arg_data)
