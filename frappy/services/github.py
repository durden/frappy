"""
Class to perform operations on the Github API
"""

try:
    import json
except ImportError:
    import simplejson as json

from frappy.core.api import APICall


class Github(APICall):
    """
    Tiny wrapper around Github API (pass method=<method>) to any call to alter
    request method

    Note when dealing with SHA1 for commits make sure to use string syntax
    instead of method calls b/c SHA1 can start with numbers, which results in
    invalid syntax.  See below for examples.


    Examples

    Create authenticated API object
    -------------------------------

    from frappy.services.github import Github
    from frappy.core.auth import UserPassAuth

    auth = UserPassAuth('joe', 'password')
    g = Github(auth=auth)

    Edit a gist
    -----------

    # Requires authenticated API object

    gist = g.gists('1066339', files={'test.txt':
                {'content': 'This is yet another updated test from frappy'}},
                method='patch')

    Create a gist
    -------------

    # Requires authenticated API object

    x = g.gists(description='testing', public='true',
                files={'test.txt': {'content': 'This is a test from frappy'}})


    >>> from frappy.services.github import Github
    >>> g = Github()
    >>> commit = \
    g.repos.durden.frappy.commits.b812be8c8dda041a694fd1560106e4ca9521bc18()
    >>> commit.response['commit']['message']
    u'Fix Twitter service rate limit properties'
    >>> commit = \
    g.repos.durden.frappy.commits('160185c313f7c49167ce122c85b13db527eeece2')
    >>> commit.response['commit']['message']
    u'Frappy supports Github! (use with caution..)'
    >>> x = g.repos.durden.frappy.commits(page=2,per_page=2)
    >>> x.requested_uri
    u'https://api.github.com/repos/durden/frappy/commits?per_page=2&page=2'
    """

    def __init__(self, req_format="json", domain="api.github.com",
                 secure=True, auth=None):

        APICall.__init__(self, auth=auth, req_format=req_format, domain=domain,
                         secure=secure)

    def _prepare_request_params(self, **kwargs):
        """Encode specific request data as json"""

        # get requests are just added to the uri as normal, but post pass JSON
        if self.request_method_is_safe():
            return kwargs

        return json.dumps(kwargs)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
