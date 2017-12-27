"""
Fetches relevant information from Request Tracker using
the rt API.

Tracker example:

    import rt
    tracker = rt.Rt('http://localhost/rt/REST/1.0/', 'user_login', 'user_pass')
    tracker.login()
    True
    tracker.logout()
"""

import rt

