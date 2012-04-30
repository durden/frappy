"""
Simple Twitter API wrapper
"""

from frappy.core.api import APICall


class Twitter(APICall):
    """
    The minimalist yet fully featured Twitter API class.

    Get RESTful data by accessing members of this class. The result
    is decoded python objects (lists and dicts).

    >>> from frappy.services.twitter.twitter import Twitter
    >>> t = Twitter()
    >>> statuses = t.statuses.public_timeline()
    >>> '200 OK' == statuses.headers['response']['status']
    True
    >>> statuses.requested_uri
    u'https://api.twitter.com/1/statuses/public_timeline.json'

    The Twitter API is documented here:

      http://dev.twitter.com/doc


    Examples::

      twitter = Twitter(
          auth=OAuth(token, token_key, con_secret, con_secret_key)))

      # Any call can accept a keyword argument 'method' to force the request
      # method to POST (default) is GET

      # Get the public timeline
      twitter.statuses.public_timeline()

      # Get a particular friend's timeline
      twitter.statuses.friends_timeline(id="billybob")

      # Also supported (but totally weird)
      twitter.statuses.friends_timeline.billybob()

      # Send a direct message
      twitter.direct_messages.new(
          user="billybob",
          text="I think yer swell!")

      # Get the members of a particular list of a particular friend
      twitter.user.listname.members(user="billybob", listname="billysbuds")


    Searching Twitter::

      twitter_search = Twitter(domain="search.twitter.com")

      # Find the latest search trends
      twitter_search.trends()

      # Search for the latest News on #gaza
      twitter_search.search(q="#gaza")


    Using the data returned
    -----------------------

    Twitter API calls return decoded JSON. This is converted into
    a bunch of Python lists, dicts, ints, and strings. For example::

      x = twitter.statuses.public_timeline()

      # The first 'tweet' in the timeline
      x[0]

      # The screen name of the user who wrote the first 'tweet'
      x[0]['user']['screen_name']


    Getting raw XML data
    --------------------

    If you prefer to get your Twitter data in XML format, pass
    format="xml" to the Twitter object when you instantiate it::

      twitter = Twitter(format="xml")

      The output will not be parsed in any way. It will be a raw string
      of XML.

    """
    def __init__(self, req_format="json", domain="api.twitter.com",
                secure=True, auth=None, api_version='1'):
        """
        Create a new twitter API connector.

        Pass an `auth` parameter to use the credentials of a specific
        user. Generally you'll want to pass an `OAuth`
        instance::

            twitter = Twitter(auth=OAuth(
                    token, token_secret, consumer_key, consumer_secret))


        `domain` lets you change the domain you are connecting. By
        default it's `api.twitter.com` but `search.twitter.com` may be
        useful too.

        If `secure` is False you will connect with HTTP instead of
        HTTPS.

        `api_version` is used to set the base uri. By default it's '1'.
        """
        if (req_format not in ("json", "xml", "")):
            raise ValueError("Unknown data format '%s'" % (req_format))

        if api_version is 1:
            if domain == 'api.twitter.com' or domain == 'stream.twitter.com':
                api_version = '1'
            else:
                api_version = None

        domain += "/%s" % (api_version)

        APICall.__init__(self, auth=auth, req_format=req_format, domain=domain,
                        secure=secure)

    def service_build_uri(self, *args, **kwargs):
        """
        Complete creation of request uri by adding additional Twitter specific
        syntax, etc.
        """

        # Append all extra arguments from *args
        APICall.service_build_uri(self, *args, **kwargs)

        # If an id kwarg is present and there is no id to fill in in
        # the list of uriparts, assume the id goes at the end.
        id = kwargs.pop('id', None)
        if id:
            self.uri += "/%s" % (id)

        # Twitter allows for specifying request format in uri
        dot = ""
        if self.req_format:
            dot = "."

        self.uri += "%s%s" % (dot, self.req_format)

        return kwargs


if __name__ == "__main__":
    import doctest
    doctest.testmod()

__all__ = ["Twitter"]
