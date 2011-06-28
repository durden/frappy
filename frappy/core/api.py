"""
Base implementation of Frappy framework.
"""


from frappy.core.auth import NoAuth
import requests

try:
    import json
except ImportError:
    import simplejson as json


class DefaultVersion(object):
    """Default version class"""
    pass


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

    def __init__(self, status_code, uri, req_format, uriparts):
        """Initalize error object"""

        self.status_code = status_code
        self.uri = uri
        self.req_format = req_format
        self.uriparts = uriparts

        APIError.__init__(self)

    def __str__(self):
        """Stringify error"""

        return (
            "API sent status %i for URL: %s using parameters: "
            "(%s)" % (self.status_code, self.uri, self.uriparts))


class APICall(object):
    """
    Base implementation of API call.

    This class is very generic and should provide most of the send/retrieve
    functionality for API access.  Thus, you should be able to subclass it,
    and provide a basic __init__ method.
    """

    def __init__(self, auth, req_format, domain, uriparts=None, secure=True,
                 post_actions=None, debug=False):

        """Initialize call API object"""

        self.auth = auth
        if auth is None:
            self.auth = NoAuth()

        self.req_format = req_format
        self.domain = domain
        self.uri = ""
        self.requested_uri = ""
        self.secure = secure
        self.post_actions = post_actions

        if self.post_actions is None:
            self.post_actions = []

        self.response = None
        self.headers = {'request': {}, 'response': {}}

        self.method = "GET"
        self.body = None
        self.arg_data = ""
        self.missing_attrs = ()

        self.uriparts = uriparts
        if self.uriparts is None:
            self.uriparts = ()

        # Set to True to test requests without Internet access (useful for unit
        # testing and just verifying that calls generate correct request uris)
        self.debug = debug

    def __getattr__(self, k):
        """
        Look for attribute k in base object, other wise append to uri

        This is allows for a very powerful and expressive syntax for creating
        API calls that map closely to the uri they query.  For example a
        Twitter call: <object>.statuses.public_timeline() will map to
        <domain>/statuses/public_timeline.
        """

        self.missing_attrs += (k,)
        return self

    def service_build_uri(self, **kwargs):
        """
        Service specific build uri

        This method is meant to be overriden by child classes to have the last
        opportunity to verify self.uri and add additional elements to it, etc.
        """
        return

    def _build_uri(self, *args, **kwargs):
        """Build up the final uri for the request"""

        uriparts = []
        extra_uri = self.uriparts + self.missing_attrs

        for uripart in extra_uri:
            # If this part matches a keyword argument, use the
            # supplied value otherwise, just use the part.
            uriparts.append(str(kwargs.pop(uripart, uripart)))

        self.uri += '/'.join(uriparts)

        # Don't use join here b/c not all arguments are required to be strings
        for arg in args:
            self.uri += '/%s' % (arg)

        secure_str = ''
        if self.secure:
            secure_str = 's'

        self.uri = "http%s://%s/%s" % (secure_str, self.domain, self.uri)

        # Wrapper for child classes to customize creation of the uri
        self.service_build_uri(**kwargs)

        # method is GET by default
        for action in self.post_actions:
            if self.uri.find(action) > -1:
                self.method = "POST"
                break

       # Append any authentication specified to request
        self._handle_auth(**kwargs)

    def _handle_auth(self, **kwargs):
        """
        Attach requested authentication to request and encoded body and
        parameters
        """

        if self.auth is None:
            raise ValueError('Authentication is None')

        self.headers['request'].clear()
        self.headers['response'].clear()

        self.headers['request'].update(self.auth.generate_headers())
        self.arg_data = self.auth.encode_params(self.uri, self.method,
                                                kwargs)

        if self.method == 'GET':
            self.uri += '?' + self.arg_data
        else:
            self.body = self.arg_data.encode('utf8')

    def __call__(self, *args, **kwargs):
        """
        Finish building uri with leftover arguments, append authentication, and
        send off request
        """

        self._build_uri(*args, **kwargs)
        resp = requests.get(self.uri, headers=self.headers['request'])
        return self._handle_response(resp, self.arg_data)

    def _handle_response(self, resp, arg_data):
        """Verify response code and format data accordingly"""

        self.headers['response'] = resp.headers

        # Roll over request to prepare for new one
        self._reset_uri()

        if resp.status_code != 200:
            if (resp.status_code == 304):
                return []
            # Allows for testing without Internet access
            elif self.debug:
                return self
            else:
                raise APIHTTPError(resp.status_code, self.requested_uri,
                                   self.req_format, arg_data)

        if "json" == self.req_format:
            self.response = json.loads(resp.content.decode('utf8'))
        else:
            self.response = resp.content.decode('utf8')

        return self

    def _reset_uri(self):
        """Clear active request uri to make way for another request"""

        # Save off the current uri request just for testing and inspection
        self.requested_uri = self.uri
        self.uri = ""
        self.missing_attrs = ()

    @property
    def rate_limit_remaining(self):
        """
        Remaining requests in the current rate-limit.
        """

        try:
            return int(self.headers['response']['x-ratelimit-remaining'])
        except KeyError:
            return 0

    @property
    def rate_limit(self):
        """
        Max number of requests allowed.
        """

        try:
            return int(self.headers['response']['x-ratelimit-limit'])
        except KeyError:
            return 0

    @property
    def rate_limit_reset(self):
        """
        Time in UTC epoch seconds when the rate limit will reset.
        """

        try:
            return int(self.headers['response']['x-ratelimit-reset'])
        except KeyError:
            return 0
