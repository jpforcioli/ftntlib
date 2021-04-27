#!/usr/bin/env python

###################################################################
#
# fos_restapi.py is based on fgt_api.py by Tri Huynh
# refactored and packaged with ftntlib by Ashton Turpin
#
# A Python module to access the FortiOS REST API
#
###################################################################

import requests
import json


class FortiOSREST(object):
    def __init__(self):
        self._debug = False
        self._http_debug = False
        self._https = True
        self._session = requests.session()  # use single session for all requests
        self._auth_token = None
        self.log_session_id = None

    def jprint(self, json_obj):
        return json.dumps(json_obj, indent=2, sort_keys=True)

    def dprint(self, response):
        if self._debug:
            method = response.request.method
            url = response.request.url
            body = response.request.body

            # REQUEST
            print("\nREQUEST:\n")
            print(method + ": " + url)

            if self._http_debug:
                headers = response.request.headers
                for key, value in headers.iteritems():
                    print(key + ": " + value)

            if body is not "null":
                if body is not None:
                    try:
                        j = json.loads(body)
                    except (ValueError, TypeError):
                        print("\n" + body)
                    else:
                        print("\n" + json.dumps(j, indent=2, sort_keys=True))

            # RESPONSE
            print("\nRESPONSE:\n")
            body = response.content

            if self._http_debug:
                status_code = response.status_code
                reason = response.reason
                headers = response.headers

                print(str(status_code) + " " + reason)
                for key, value in headers.iteritems():
                    print(key + ": " + value)

            if body is not "null":
                if body is not None:
                    try:
                        j = json.loads(body)
                    except (ValueError, TypeError):
                        print("\n" + str(body))
                    else:
                        print("\n" + json.dumps(j, indent=2, sort_keys=True))

    def debug(self, status):
        if status == "on":
            self._debug = True
        if status == "off":
            self._debug = False

    def http_debug(self, status):
        if status == "on":
            self._http_debug = True
        if status == "off":
            self._http_debug = False

    def https(self, status):
        if status == "on":
            self._https = True
        if status == "off":
            self._https = False

    def update_csrf(self):
        # Retrieve server csrf and update session's headers
        for cookie in self._session.cookies:
            if cookie.name == "ccsrftoken":
                csrftoken = cookie.value[1:-1]  # token stored as a list
                self._session.headers.update({"X-CSRFTOKEN": csrftoken})

    def url_prefix(self, host):
        if self._https is True:
            self._url_prefix = "https://" + host
        else:
            self._url_prefix = "http://" + host

    def login_token(self, host, token):
        self._auth_token = token
        self._session.headers.update({"Authorization": "Bearer {}".format(token)})
        self._session.verify = False
        self.url_prefix(host)

    def login(
        self, host, username, password, timeout=None, token=None, path="/logincheck"
    ):
        self.url_prefix(host)
        url = self._url_prefix + path
        res = self._session.post(
            url,
            data="username=" + username + "&secretkey=" + password,
            verify=False,
            timeout=timeout,
        )
        self.dprint(res)

        # Update session's csrftoken
        self.update_csrf()

    def logout(self, path="/logout"):
        url = self._url_prefix + path
        res = self._session.post(url)

        self.dprint(res)

    api_get_path = "/api/v2/"
    valid_apis = {"monitor", "cmdb", "log"}

    def get_url(self, api, path, name, action, mkey):
        # Check for valid api
        if api not in self.valid_apis:
            print("Unknown API {0}. Ignore.".format(api))
            return

        # Construct URL request, action and mkey are optional
        url_postfix = self.api_get_path + api + "/" + path + "/" + name
        if action:
            url_postfix += "/" + action
        if mkey:
            url_postfix = url_postfix + "/" + str(mkey)
        url = self._url_prefix + url_postfix
        return url

    def get_v1(self, api, path, name, action="select"):
        if api == "monitor":
            url_postfix = "/api/monitor"
            payload_prefix = "json="
        elif api == "cmdb":
            url_postfix = "/api/cmdb"
            payload_prefix = "request"
        else:
            print("Unknown API {0}. Ignore.".format(api))
            return

        url = self._url_prefix + url_postfix
        data = {"path": path, "name": name, "action": action}
        payload = payload_prefix + json.dumps(data)

        res = self._session.get(url, params=payload)
        self.dprint(res)
        return res.content

    def get_webui(self, url_postfix, parameters=None):
        url = self._url_prefix + url_postfix
        res = self._session.get(url, params=parameters)
        self.dprint(res)
        return res.content

    def get_log(self, path, name, action=None, mkey=None, parameters=None):
        if not self.log_session_id:
            content = self.get("log", path, name, action=action, mkey=mkey)
            try:
                data = json.loads(content)
            except Exception as err:
                print("Can not get session_id (%s): %s" % (err, content))
                return content
            self.log_session_id = int(data["session_id"])
        parameters = parameters.copy() if parameters else {}
        parameters.setdefault("session_id", self.log_session_id)
        return self.get(
            "log", path, name, action=action, mkey=mkey, parameters=parameters
        )

    def get(self, api, path, name, action=None, mkey=None, parameters=None, data=None):
        url = self.get_url(api, path, name, action, mkey)
        res = self._session.get(url, params=parameters, data=json.dumps(data))
        self.dprint(res)
        return res.content

    def post(self, api, path, name, action=None, mkey=None, parameters=None, data=None):
        url = self.get_url(api, path, name, action, mkey)
        res = self._session.post(url, params=parameters, data=json.dumps(data))
        self.dprint(res)
        return res.content

    def put(self, api, path, name, action=None, mkey=None, parameters=None, data=None):
        url = self.get_url(api, path, name, action, mkey)
        res = self._session.put(url, params=parameters, data=json.dumps(data))
        self.dprint(res)
        return res.content

    def delete(
        self, api, path, name, action=None, mkey=None, parameters=None, data=None
    ):
        url = self.get_url(api, path, name, action, mkey)
        res = self._session.delete(url, params=parameters, data=json.dumps(data))
        self.dprint(res)
        return res.content


if __name__ == "__main__":
    from .debug import main

    exit(main(FortiOSREST))
