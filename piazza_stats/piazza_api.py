# Edited from https://github.com/hfaran/piazza-api
# Original file by hfaran on github, git cloned 01 Oct 2014.

import requests
import json
import getpass
import random
from datetime import date
import time


class AuthenticationError(Exception):
    """AuthenticationError"""


class NotAuthenticatedError(Exception):
    """NotAuthenticatedError"""


class PiazzaAPI(object):
    """Tiny wrapper around Piazza's Internal API

    Example:
        >>> p = PiazzaAPI("hl5qm84dl4t3x2")
        >>> p.user_auth()
        Email: ...
        Password: ...
        >>> p.get(181)
        ...
        
    :type  network_id: str
    :param network_id: This is the ID of the network (or class) from which
        to query posts
    """
    def __init__(self, network_id):
        self._nid = network_id
        self.base_api_uri = 'https://piazza.com/logic/api'
        self.cookies = None

    def user_auth(self, email=None, password=None):
        """Login with email, password and get back a session cookie

        :type  email: str
        :param email: The email used for authentication
        :type  password: str
        :param password: The password used for authentication
        """
        email = raw_input("Email: ") if email is None else email
        password = getpass.getpass() if password is None else password

        login_uri = self.base_api_uri
        login_data = {
            "method": "user.login",
            "params": {
                "email": email,
                "pass": password
            }
        }
        login_params = {"method": "user.login"}
        # If the user/password match, the server respond will contain a
        #  session cookie that you can use to authenticate future requests.
        r = requests.post(
            login_uri,
            data=json.dumps(login_data),
            params=login_params
        )
        if r.json()["result"] not in ["OK"]:
            raise AuthenticationError(
                "Could not authenticate.\n{}".format(r.json())
            )
        self.cookies = r.cookies

    def demo_auth(self, auth=None, uri=None):
        """Authenticate with a "Share Your Class" URL using a demo user.

        You may provide either the entire ``uri`` or simply the ``auth`` parameter.

        :param uri: Example - "https://piazza.com/demo_login?nid=hbj11a1gcvl1s6&auth=06c111b"
        :param auth: Example - "06c111b"
        """
        assert all([
            auth or uri,  # Must provide at least one
            not (auth and uri)  # Cannot provide more than one
        ])
        if uri is None:
            uri = "https://piazza.com/demo_login"
            params = dict(nid=self._nid, auth=auth)
            res = requests.get(uri, params=params)
        else:
            res = requests.get(uri)
        self.cookies = res.cookies

    def get(self, cid, nid=None):
        """Get data from post `cid` in network `nid`

        :type  nid: str
        :param nid: This is the ID of the network (or class) from which
            to query posts. This is optional and only to override the existing
            `network_id` entered when created the class
        :type  cid: str|int
        :param cid: This is the post ID which we grab
        :returns: Python object containing returned data
        """
        self._check_authenticated()

        nid = nid if nid else self._nid
        content_uri = self.base_api_uri
        content_params = {"method": "get.content"}
        content_data = {
            "method": "content.get",
            "params": {
                "cid": cid,
                "nid": nid
            }
        }
        return requests.post(
            content_uri,
            data=json.dumps(content_data),
            params=content_params,
            cookies=self.cookies
        ).json()
    
    def _check_authenticated(self):
        if self.cookies is None:
            raise NotAuthenticatedError("You must authenticate before making any other requests.")
    
    
    # added by Ben
    def get_statistics_csv(self):
        """Get CSV of class participation statistics
        
        :returns: String containing contents of CSV
        """
        self._check_authenticated()
        
        content_uri = "https://piazza.com/class_statistics/{nid}?day={d}".format(
            nid=self._nid,
            d=date.today().strftime("%b-%d"))
        
        return requests.get(
            content_uri,
            cookies=self.cookies).text
    
    @staticmethod
    def generate_aid():
        """Generate a random AID for a request.
        This mess is a direct translation of the JS code in Piazza.

        :returns: String containing random AID
        """
        
        # http://stackoverflow.com/questions/2063425/python-elegant-inverse-function-of-intstring-base
        def digit_to_char(digit):
            digit = int(digit)
            return str(digit) if digit < 10 else chr(ord('a') + digit - 10)
            
        def str_base(number, radix):
            if number < 0:
                return '-' + str_base(-number, radix)
            (d, m) = divmod(number, radix)
            if d > 0:
                return str_base(d, radix) + digit_to_char(m)
            return digit_to_char(m)
        
        return str_base(time.time(),36) + str_base(round(random.randrange(0,1679616)),36)
    
    
    def get_users(self, user_ids):
        self._check_authenticated()
        
        user_uri = "https://piazza.com/logic/api?method=network.get_users"
        
        return requests.post(
            user_uri,
            params={
                "method": "network.get_users",
                "aid": self.generate_aid()
            },
            data=json.dumps({
                "method": "network.get_users",
                "params": {
                    "ids": user_ids,
                    "nid": self._nid
                }
            }),
            cookies=self.cookies
        ).json().get('result')
    
    
    def get_instructor_stats(self):
        self._check_authenticated()
        
        res = requests.post(
            "https://piazza.com/logic/api",
            params={
                "method": "network.get_instructor_stats",
                "aid": self.generate_aid()
            },
            data=json.dumps({
                "method": "network.get_instructor_stats",
                "params": {
                    "nid": self._nid
                }
            }),
            cookies=self.cookies
        ).json()
        
        return res['result'] if not res.get('error') else res





