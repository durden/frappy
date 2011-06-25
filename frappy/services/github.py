"""
Class to perform operations on the Github API
"""

from frappy.core.api import APICall


class _DEFAULT(object):
    pass


class Github(APICall):
    """
    Tiny wrapper around Github API

    >>> from frappy.services.github import Github
    >>> g = Github()
    >>> commit = g.repos.durden.frappy.commits.b812be8c8dda041a694fd1560106e4ca9521bc18()
    >>> commit.response['commit']['message']
    u'Fix Twitter service rate limit properties'
    """

    def __init__(self, req_format="json", domain="api.github.com",
                 secure=True, auth=None, api_version=_DEFAULT):

        APICall.__init__(self, auth=auth, req_format=req_format, domain=domain,
                         secure=secure)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
