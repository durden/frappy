
"""
Class to perform operations on the Codrspace.com API
"""

from frappy.core.api import APICall


class Codrspace(APICall):
    """
    Tiny wrapper around Codrspace API

    Examples:

    Get user's posts
    ----------------

    >>> from frappy.services.codrspace import Codrspace
    >>> c = Codrspace('durden', 'c139439a4d682d2db84a8d603eddb5c38c56d8e5')
    >>> posts = c.post()
    >>> 'title' in posts.response['objects'][0]
    True
    >>> # Loop over posts
    ... for p in posts.response['objects']:
    ...    pass
    ...

    """

    def __init__(self, username, api_key, domain="codrspace.com/api/"):

        APICall.__init__(self, auth=None, req_format='json', domain=domain,
                         secure=False)

        self._api_key = api_key
        self._username = username

    def _prepare_request_params(self, **kwargs):
        """Append mandatory arguments for format"""

        # get requests are just added to the uri as normal, but post pass JSON
        kwargs['api_key'] = self._api_key
        kwargs['format'] = 'json'
        kwargs['username'] = self._username

        return kwargs

if __name__ == "__main__":
    import doctest
    doctest.testmod()
