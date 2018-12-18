#!/usr/bin/env python
###################################################################
#
# faz_jsonapi.py by Jean-Pierre Forcioli
# Mainly inspired from fmg_jsonapi.py by Ashton Turpin
#
# A Python module to access the FortiAnalyzer JSON API
#
###################################################################

import requests

class FortiAnalyzerJSON(object):
    def __init__(self):
        self.ip = None
        self.user = None
        self.password = None
        self.session = None
        self.id = None
        self.use_https = True
        self.endpoint = "/jsonrpc/fazapi"

    def login(self, ip, user, password):
        pass
