#Frappy
Frappy is a framework for interacting with social web APIs.  It is meant to be
an easy/quick way to create small Python wrappers for web APIs.

##History
Frappy was started by using The Minimalist Twitter API for Python.  This
project did a great job of making a small and easy to use wrapper for the
Twitter API.  However, the majority of the code was very generic, and was very
easy to extend to other web APIs.

##Supported APIs

* Twitter
* Github
* Forrst

###Add support for new service
Just subclass core.api.APICall class and place in services module.  See
existing services for examples.

###How do I use it?
Each service has a minimal set of doctests which show a few examples.  In
general, frappy should make it fairly obvious (hopefully) how to call an API
method in code.

Typically the '/' in an API call translate into different 'attributes' in
Python code.  Then, the final portion of the API URL is the actual method call.
For example, the following github API call:
    https://api.github.com/users/

Translates to a Python call like so:

    >>> from frappy.services.github import Github
    >>> g = Github()
    >>> r = g.users('octocat')
    >>> print r.repsonse
    >>> print r.repsonse_json

Notice that the 'users' portion of the API URL is the last part of the API URL
and it requires the username.  Thus, this argument is provided as an 'argument'
to the 'users' method.

You can also make basic authenticated calls by creating an authentication objet
and setting up your service object with it.

    >>> from frappy.services.github import Github
    >>> from frappy.core.auth import UserPassAuth
    >>> auth = UserPassAuth('joe', 'password')
    >>> g = Github(auth=auth)
    >>> x = g.gists(description='testing', public='true',
                files={'test.txt': {'content': 'This is a test from frappy'}})

###Contribution Guidelines

* All code should be PEP8 compliant.
* Try running pylint on your changes and minimize the errors/warnings.  Ideally
  all code should be rated at least 7.0 by pylint.

###Requirements

[Python Requests](https://github.com/kennethreitz/requests)
(See requirements file)
