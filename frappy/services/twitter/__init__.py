"""
The minimalist yet fully featured Twitter API and Python toolset.

The Twitter and TwitterStream classes are the key to building your own
Twitter-enabled applications.

"""

from .twitter import Twitter, TwitterResponse
from .stream import TwitterStream


# Who needs Sphinx? Not me!

__doc__ += """
The Twitter class
=================
"""
__doc__ += Twitter.__doc__

__doc__ += """
The TwitterStream class
=======================
"""
__doc__ += TwitterStream.__doc__


__doc__ += """
Twitter Response Objects
========================
"""
__doc__ += TwitterResponse.__doc__


__all__ = ["Twitter", "TwitterStream", "TwitterResponse"]
