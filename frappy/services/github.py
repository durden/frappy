"""
Class to perform operations on the Github API
"""

try:
    import json
except ImportError:
    import simplejson as json

from frappy.core.api import APICall


# FIXME: Potential problem with github API:
#           - SHA1 can start with a number so getting a specific commit will
#             result in a syntax error. For example:
#               commit = g.repos.durden.frappy.commits.
#                               160185c313f7c49167ce122c85b13db527eeece2()

class Github(APICall):
    """
    Tiny wrapper around Github API

    >>> from frappy.services.github import Github
    >>> g = Github()
    >>> commit = g.repos.durden.frappy.commits.b812be8c8dda041a694fd1560106e4ca9521bc18()
    >>> commit.response['commit']['message']
    u'Fix Twitter service rate limit properties'
    >>> x = g.repos.durden.frappy.commits(page=2,per_page=2)
    >>> x.requested_uri
    'https://api.github.com/repos/durden/frappy/commits?per_page=2&page=2'
    """

    def __init__(self, req_format="json", domain="api.github.com",
                 secure=True, auth=None, debug=False):

        APICall.__init__(self, auth=auth, req_format=req_format, domain=domain,
                         secure=secure, post_actions=['gists'], debug=debug)

    def _handle_auth(self, **kwargs):
        """
        Setup authentication in headers and return properly encoded request
        data
        """

        arg_data = APICall._handle_auth(self, **kwargs)

        # GET requests are just added to the uri as normal, but POST pass JSON
        if self._get_http_method() == 'GET':
            return arg_data
        else:
            return json.dumps(kwargs)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
