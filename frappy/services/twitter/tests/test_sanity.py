"""
Simple tests for Twitter API
"""

import os
from random import choice

from frappy.services.twitter.twitter import Twitter
from frappy.services.twitter.cmdline import CONSUMER_KEY, CONSUMER_SECRET

from frappy.core.auth import NoAuth, OAuth

noauth = NoAuth()

# Open oauth_creds file in this directory and create oauth client using
oauth = OAuth(*OAuth.read_token_file(os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 'oauth_creds'))
                + (CONSUMER_KEY, CONSUMER_SECRET))

twitter = Twitter(domain='api.twitter.com', auth=oauth, api_version='1')
twitter_na = Twitter(domain='api.twitter.com', auth=noauth, api_version='1')


AZaz = "abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def get_random_str():
    return ''.join(choice(AZaz) for _ in range(10))


def test_API_get_some_public_tweets():
    updates = twitter_na.statuses.public_timeline()
    assert updates
    assert updates[0]['created_at']


def test_API_set_tweet():
    random_tweet = "A random tweet " + get_random_str()
    twitter.statuses.update(status=random_tweet)

    recent = twitter.statuses.user_timeline()
    assert recent
    assert random_tweet == recent[0]['text']


def test_API_friendship_exists():
    assert True == twitter.friendships.exists(
        user_a='ptttest0001', user_b='sixohsix')
    assert False == twitter.friendships.exists(
        user_a='gruber', user_b='ptttest0001')


def test_search():
    t_search = Twitter(domain='search.twitter.com')
    results = t_search.search(q='foo')
    assert results


def main():
    """Find all functions with names like _test and execute them"""

    # NOTE: This could easily be done by the nose project, but just trying to
    # keep down the dependencies right now...
    import sys, types
    module = sys.modules[__name__]

    for name, var in vars(module).items():
        if type(var) == types.FunctionType and name.startswith('test_'):
            print "Running %s ... " % (name),

            try:
                var()
            except Exception as e:
               print "failed %s " % (str(e))
            else:
               print "passed "


if __name__ == "__main__":
    main()
