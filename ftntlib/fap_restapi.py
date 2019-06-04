#!/usr/bin/env python

###################################################################
#
# fap_restapi.py is based on fos_restapi.py
# Author: Jeremy Parente
#
# A Python module to access the FAP REST API
#
###################################################################

import requests
import json

from .fos_restapi import FortiOSREST


class FAPREST(FortiOSREST):
    api_get_path = '/api/v1/'

    def get_url(self, api, path, name, action, mkey):
        """`api`, `name`, `action` and `mkey` are ignored, just here to keep
        same signature than FortiOSREST.get_url

        """
        url_postfix = self.api_get_path + path
        url = self.url_prefix + url_postfix
        return url

    def decode_reply(self, res):
        if res.status_code in {200, 202}:
            try:
                return res.json()
            except ValueError as err:
                return {
                    "errors": [str(err)],
                    "reply": res,
                }
        else:
            return {
                "errors": ['http status code: %s' % res.status_code],
                "reply": res,
            }

    def get(self, path, action=None, mkey=None, parameters=None):
        url = self.get_url(None, path, None, action, mkey)
        res = self._session.get(url,params=parameters)
        self.dprint(res)
        return self.decode_reply(res)

    def set(self, path, parameters, timeout=None):
        url = self.get_url(None, path, None, None, None)
        res = self._session.post(url, json=parameters, timeout=timeout)
        self.dprint(res)
        return self.decode_reply(res)

    def reboot(self, timeout=10):
        try:
            return self.set('reboot', {}, timeout=timeout)
        except (requests.ConnectionError, requests.Timeout) as err:
            return {
                "errors": [],
                "warnings": [str(err)],
            }


if __name__ == '__main__':
    from .debug import main
    exit(main(FAPREST))
