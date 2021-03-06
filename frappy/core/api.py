"""
Base implementation of Frappy framework.
"""


from frappy.core.auth import NoAuth
import requests

try:
    import json
except ImportError:
    import simplejson as json


class APIHTTPError(Exception):
    """
    Base Exception thrown by the APICall object when there is a
    general error interacting with the API.
    """

    def __init__(self, status_code, uri):
        """Initalize error object"""

        self.status_code = status_code
        self.uri = uri

        super(Exception, self).__init__()

    def __str__(self):
        """Stringify error"""

        return ("API sent status %i for URL: %s " % (self.status_code,
                                                    self.uri))


class APICall(object):
    """
    Base implementation of API call.

    This class is very generic and should provide most of the send/retrieve
    functionality for API access.  Thus, you should be able to subclass it,
    and provide a basic __init__ method.
    """

    def __init__(self, auth, req_format, domain, secure=True):

        """Initialize call API object"""

        self.auth = auth
        if auth is None:
            self.auth = NoAuth()

        self.req_format = req_format

        secure_str = ''
        if secure:
            secure_str = 's'

        self.base_uri = "http%s://%s/" % (secure_str, domain)
        self.uri = self.base_uri

        self.requested_uri = ""
        self.method = "get"

        self.response = None
        self.headers = {'request': {}, 'response': {}}

        self.missing_attrs = ()

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

    def service_build_uri(self, *args, **kwargs):
        """
        Service specific build uri

        This method is meant to be overriden by child classes to have the last
        opportunity to verify self.uri and add additional elements to it, etc.

        NOTE: Make sure to pop all arguments off the list if you use
        them otherwise they will be appended twice since all leftovers are
        eventually added to the request uri

        Also, don't forget to call this base method after doing service
        specific alterations!
        """

        # Don't use join here b/c not all arguments are required to be strings
        for arg in args:
            self.uri += '/%s' % (arg)

        return kwargs

    def _build_uri(self, **kwargs):
        """
        Build uri for request with any missing attribute accesses that have
        accumulated and any arguments or keyword arguments and return any
        leftover keyword arguments
        """

        uriparts = []

        # Search all missing attributes for matching keyword argument
        for uripart in self.missing_attrs:
            # If keyword argument matches missing attribute use the value of
            # keyword argument, otherwise just append the missing attribute
            # This allows for putting keyword arguments in the middle of a uri
            # string instead of the at end
            # For example:
            # myobject.test.id.details(id=1) maps to domain/test/1/details/
            uriparts.append(str(kwargs.pop(uripart, uripart)))

        self.uri += '/'.join(uriparts)

        # Return leftover keyword arguments for service specific code to use,
        # otherwise they'll just be appended at the end later
        return kwargs

    def _handle_auth(self):
        """
        Setup authentication in headers and return properly encoded request
        data
        """

        if self.auth is None:
            raise ValueError('Authentication is None')

        self.headers['request'].clear()
        self.headers['response'].clear()

        self.headers['request'].update(self.auth.generate_headers())

    def _set_request_method(self, **kwargs):
        """Set request method for response by passing in 'method' kwarg"""
        self.method = kwargs.pop('method', 'get')

    def __call__(self, *args, **kwargs):
        """
        Finish building uri with leftover arguments, append authentication, and
        send off request
        """

        kwargs = self._build_uri(**kwargs)

        # Wrapper for child classes to customize creation of the uri
        kwargs = self.service_build_uri(*args, **kwargs)

        self._set_request_method(**kwargs)

        # Append any authentication specified to request
        self._handle_auth()

        resp = self._send_request(**kwargs)

        return self._handle_response(resp)

    def _prepare_request_params(self, **kwargs):
        """Handle encoding or any special processing of request parameters"""

        return kwargs

    def request_method_is_safe(self):
        """
        Determines if request is 'safe' in REST terminology (aka doesn't
        change data, just requests it)
        """
        return self.method == 'get' or self.method == 'head'

    def _send_request(self, **kwargs):
        """Send request to self.uri with associated (encoded) data"""

        # Make it lowercase to b/c the methods in requests module are lowercase
        self.method = self.method.lower()
        method_call = getattr(requests, self.method, None)

        if method_call is None:
            raise AttributeError(
                            '%s not a supported HTTP method' % (self.method))

        arg_data = self._prepare_request_params(**kwargs)

        # 'get' and 'head' take params to put in query string
        if self.request_method_is_safe():
            resp = method_call(self.uri, params=arg_data,
                               headers=self.headers['request'])

            # Update uri with full location (including query params encoded)
            self.uri = resp.url
        else:
            resp = method_call(self.uri, data=arg_data,
                               headers=self.headers['request'])

        return resp

    def _handle_response(self, resp):
        """Verify response code and format data accordingly"""

        self.headers['response'] = resp.headers

        # Roll over request to prepare for new one
        self._reset_uri()

        # 200 - ok, 201 - created
        if resp.status_code != 200 and resp.status_code != 201:
            if (resp.status_code == 304):
                return []
            else:
                raise APIHTTPError(resp.status_code, self.requested_uri)

        if "json" == self.req_format:
            self.response = json.loads(resp.content.decode('utf8'))
            self.response_json = json.dumps(self.response)
        else:
            self.response = resp.content.decode('utf8')

        return self

    def _reset_uri(self):
        """Clear active request uri to make way for another request"""

        # Save off the current uri request just for testing and inspection
        self.requested_uri = self.uri
        self.uri = self.base_uri
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
