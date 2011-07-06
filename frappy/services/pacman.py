"""
Wrapper for fictional test service
"""

from frappy.core.api import APICall


class Pacman(APICall):
    """Wrapper for Pacman service API"""

    def __init__(self, req_format="json", domain="127.0.0.1:8000",
                 secure=False, auth=None):

        APICall.__init__(self, auth=auth, req_format=req_format, domain=domain,
                         secure=secure)
