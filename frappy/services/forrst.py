"""
Class to perform operations on the Forrst API
"""

from frappy.core.api import APICall, DefaultVersion


class Forrst(APICall):
    """
    Tiny wrapper around Forrst API
    """

    def __init__(self, req_format="json", domain="forrst.com/api",
                 secure=False, auth=None, api_version=DefaultVersion,
                 debug=False):

        if api_version is DefaultVersion:
            api_version = 'v2'

        uriparts = ()
        if api_version:
            uriparts += (str(api_version),)

        APICall.__init__(self, auth=auth, req_format=req_format, domain=domain,
                         secure=secure, uriparts=uriparts, debug=debug)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
