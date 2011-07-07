"""
Class to perform operations on the Forrst API
"""

from frappy.core.api import APICall, DefaultVersion


class Forrst(APICall):
    """
    Tiny wrapper around Forrst API

    >>> from frappy.services.forrst import Forrst
    >>> f = Forrst()
    >>> x = f.stats()
    >>> x.response['stat']
    u'ok'
    >>> x = f.users.info(username='durden')
    >>> x.response['stat']
    u'ok'
    >>> x.response['resp']['username']
    u'durden'
    >>> x = f.posts.show(id=45114)
    >>> x.response['stat']
    u'ok'
    >>> 'content' in x.response['resp']
    True
    >>> x = f.posts.all()
    >>> x.response['stat']
    u'ok'
    >>> x = f.posts.list(post_type='code')
    >>> x.response['stat']
    u'ok'
    >>> 'posts' in x.response['resp']
    True
    """

    def __init__(self, req_format="json", domain="forrst.com/api",
                 secure=False, auth=None, api_version=DefaultVersion):

        if api_version is DefaultVersion:
            api_version = 'v2'

        uriparts = ()
        if api_version:
            uriparts += (str(api_version),)

        APICall.__init__(self, auth=auth, req_format=req_format, domain=domain,
                         secure=secure, uriparts=uriparts)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
