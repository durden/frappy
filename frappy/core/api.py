try:
    import urllib.request as urllib_request
    import urllib.error as urllib_error
except ImportError:
    import urllib2 as urllib_request
    import urllib2 as urllib_error

from .auth import NoAuth

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
        self.e = e
        self.uri = uri
        self.format = format
        self.uriparts = uriparts

    def __str__(self):
        return (
            "API sent status %i for URL: %s.%s using parameters: "
            "(%s)\ndetails: %s" % (
                self.e.code, self.uri, self.format, self.uriparts,
                self.e.fp.read()))


class APICall(object):

    def __init__(
        self, auth, format, domain, callable_cls, uri="",
        uriparts=None, secure=True):
        self.auth = auth
        self.format = format
        self.domain = domain
        self.callable_cls = callable_cls
        self.uri = uri
        self.uriparts = uriparts
        self.secure = secure

    def __getattr__(self, k):
        try:
            return object.__getattr__(self, k)
        except AttributeError:
            return self.callable_cls(
                auth=self.auth, format=self.format, domain=self.domain,
                callable_cls=self.callable_cls, uriparts=self.uriparts + (k,),
                secure=self.secure)

    def __call__(self, **kwargs):
        # Build the uri.
        uriparts = []
        for uripart in self.uriparts:
            # If this part matches a keyword argument, use the
            # supplied value otherwise, just use the part.
            uriparts.append(str(kwargs.pop(uripart, uripart)))
        uri = '/'.join(uriparts)

        method = "GET"
        #for action in POST_ACTIONS:
            #if uri.endswith(action):
                #method = "POST"
                #break

        # If an id kwarg is present and there is no id to fill in in
        # the list of uriparts, assume the id goes at the end.
        id = kwargs.pop('id', None)
        if id:
            uri += "/%s" %(id)

        secure_str = ''
        if self.secure:
            secure_str = 's'
        dot = ""
        if self.format:
            dot = "."
        uriBase = "http%s://%s/%s%s%s" %(
                    secure_str, self.domain, uri, dot, self.format)

        headers = {}
        if self.auth:
            headers.update(self.auth.generate_headers())
            arg_data = self.auth.encode_params(uriBase, method, kwargs)
            if method == 'GET':
                uriBase += '?' + arg_data
                body = None
            else:
                body = arg_data.encode('utf8')

        req = urllib_request.Request(uriBase, body, headers)
        return self._handle_response(req, uri, arg_data)

    def _handle_response(self, req, uri, arg_data):
        try:
            handle = urllib_request.urlopen(req)
            if "json" == self.format:
                res = json.loads(handle.read().decode('utf8'))
                return wrap_response(res, handle.headers)
            else:
                return wrap_response(
                    handle.read().decode('utf8'), handle.headers)
        except urllib_error.HTTPError as e:
            if (e.code == 304):
                return []
            else:
                raise APIHTTPError(e, uri, self.format, arg_data)
