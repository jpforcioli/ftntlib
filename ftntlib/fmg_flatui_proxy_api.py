# coding: utf-8

"""Operate the FortiManager using the FMG GUI API."""

from json.decoder import JSONDecodeError
import sys
import logging
import json

from requests import Session

if sys.version_info >= (2, 7):
    logging.captureWarnings(True)
else:
    from requests.packages.urllib3.exceptions import InsecureRequestWarning

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class InvalidHTTPMethod(Exception):
    """Invalid HTTP Method."""


class FmgFlatuiProxyApi:
    """FMG GUI API class."""

    def __init__(self):
        self._proto = "https"
        self._host = None
        self._port = None
        self._base_url = None
        self._session = Session()
        self._debug = None
        self._debug_cookie = None
        self._debug_header = None

    def debug(self, value):
        """
        Enable/Disable debug mode for HTTP request/response.

        Parameters
        ----------
        value: str
            "on" to enable debug mode.
            "off" to disable debug mode.

        Returns
        -------
        Return a boolean
        """
        if value == "on":
            self._debug = True
        else:
            self._debug = False

        return self._debug

    def debug_cookie(self, value):
        """
        Enable/Disable debug mode for HTTP cookies.

        Parameters
        ----------
        value: str
            "on" to enable debug mode.
            "off" to disable debug mode.

        Returns
        -------
        Return a boolean
        """
        if value == "on":
            self._debug_cookie = True
        else:
            self._debug_cookie = False

        return self._debug_cookie

    def debug_header(self, value):
        """
        Enable/Disable debug mode for HTTP headers.

        Parameters
        ----------
        value: str
            "on" to enable debug mode.
            "off" to disable debug mode.

        Returns
        -------
        Return a boolean
        """
        if value == "on":
            self._debug_header = True
        else:
            self._debug_header = False

        return self._debug_header

    def debug_print(self, response):
        """
        Print the HTTP debub.

        Parameters
        ----------
        response: dict
            The dict returned from a FMG GUI API request
        """
        if self._debug:
            # REQUEST
            method = response.request.method
            url = response.request.url
            if response.request.body:
                body = json.loads(response.request.body)
                no_body = False
            else:
                no_body = True

            print(">>> [request]")
            print("{} {}".format(method, url))

            if not no_body:
                print(">>> [body]")
                print("\n{}".format(json.dumps(body, indent=4)))

            if self._debug_header:
                print(">>> [headers]")
                # for header in self._session.headers:
                for header in response.request.headers:
                    # print("{}: {}".format(header, self._session.headers[header]))
                    print("{}".format(response.request.headers[header]))

            if self._debug_cookie:
                print(">>> [cookies]")
                # for cookie in self._session.cookies:
                for cookie in response.request._cookies:
                    print(cookie)

            # RESPONSE
            status_code = response.status_code
            content_type = response.headers.get("content-type")

            print("<<< [status]")
            print("{}".format(status_code))

            if content_type == "application/json":
                print("\n{}".format(json.dumps(json.loads(response.text), indent=4)))
            else:
                print("\n{}".format(response.text))

            if self._debug_header:
                print("<<< [headers]")
                for header in self._session.headers:
                    print("{}: {}".format(header, self._session.headers[header]))

            if self._debug_cookie:
                print("<<< [cookies]")
                for cookie in response.cookies:
                    print(cookie)

    def set_headers_from_cookies(self, response):
        """
        Set the HTTP headers with received cookies.

        Parameters
        ----------
        response: dict
            The dict returned from a FMG GUI API request
        """
        x_csrftoken = {"X-CSRFToken": self._session.cookies["csrftoken"]}
        # self._session.headers.update(x_csrftoken)

        xsrf_token = {"XSRF-TOKEN": self._session.cookies["XSRF-TOKEN"]}
        self._session.headers.update(xsrf_token)

        # self._session.headers.update(x_xsrf_token)

    def login(self, host, login, password, port=443):
        """
        Login to FortiManager.

        Parameters
        ----------
        host: str
            The FortiManager IP or FQDN

        login: str
            The FortiManager admin's login

        password: str
            The FortiManager admin's password

        port: int
            The port numner (default is 443).

        Design notes
        ------------
        According to Mantis #0643655, we have to set the "Content-Type" to
        "application/json".
        """
        self._session.headers.update({"Content-Type": "application/json"})

        self._host = host
        self._port = port
        self._base_url = "{}://{}:{}".format(self._proto, self._host, self._port)

        login_url1 = "{}/cgi-bin/module/flatui_auth".format(self._base_url)
        login_url2 = "{}/p/app/".format(self._base_url)

        request_body = {
            "url": "/gui/userauth",
            "method": "login",
            "params": {
                "username": login,
                "secretkey": password,
                "logintype": 0,
            },
        }

        # This request will retrieve the CURRENT_SESSION and HTTP_CSRF_TOKEN
        # cookies. They will be conserved automatically by the requests.Session
        # object.
        response1 = self._session.post(login_url1, json=request_body, verify=False)
        response1.raise_for_status()
        self.debug_print(response1)

        # This request will retrieve the XSRF-TOKEN and csrftoken cookies.
        response2 = self._session.get(login_url2, verify=False)
        self.debug_print(response2)

        ## Set X-CSRFToken, XSR-TOKEN and X-XSRF-TOKEN
        self.set_headers_from_cookies(response2)

    def logout(self):
        """
        Logout from the FortiManager
        """
        # The logout URL
        logout_url = "{}/p/logout/".format(self._base_url)

        # We GET the logout
        response = self._session.get(logout_url)
        response.raise_for_status()
        self.debug_print(response)

    def flatui_proxy(self, method="post", params=None, payload=None):
        """
        Send a FMG GUI API request.

        Parameters
        ----------
        method: str
            The HTTP method to be used (default is "post")

        params: dict
            The HTTP parameters.

        payload: dict
            The payload to send to the FortiManager.
            Default is "None".
        """
        url = "{}/cgi-bin/module/flatui_proxy".format(self._base_url)

        if method == "get":
            response = self._session.get(url, params=params)

        elif method == "post":
            response = self._session.post(url, params=params, json=payload)

        else:
            raise InvalidHTTPMethod('Wrong method "{}"'.format(method))

        response.raise_for_status()
        self.debug_print(response)

        return response.json()

    def deploymng(self, action, payload, method="post"):
        """
        Explore the /deploymng/<action> API.

        Parameters
        ----------
        action: str
            The action to be performed.
            For the moment, we know about the following actions:
            - DeploymentPreview: trigger an install preview

        payload: dict
            The argument to be used for the mentioned action.

        method: str
            The HTTP method (default is "post").
        """
        url = "{}/cgi-bin/module/deploymng/{}".format(self._base_url, action)

        if method == "get":
            response = self._session.get(url, data=payload)
        elif method == "post":
            response = self._session.get(url, data=payload)
        else:
            raise InvalidHTTPMethod

        response.raise_for_status()
        self.debug_print(response)


# Main
if __name__ == "__main__":
    ip = "10.210.35.112"
    login = "devops"
    password = "fortinet"

    fmg = FmgFlatuiProxyApi()

    fmg.debug("on")
    fmg.debug_cookie("on")
    fmg.debug_header("on")
    fmg.login(ip, login, password)
    fmg.logout()
    fmg.debug("off")
