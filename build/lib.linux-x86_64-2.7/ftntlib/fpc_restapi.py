#!/usr/bin/env python
###################################################################
#
# fpc_restapi.py by Jean-Pierre Forcioli (jpforcioli@fortinet.com)
# Mainly inspired from fmg_jsonapi.py by Ashton Turpin
#
# A Python module to access the FortiPortal REST API
#
###################################################################

import requests
import json
import logging

logging.captureWarnings(True)

class FortiPortalREST():
    def __init__(self):
        self.ip = None
        self.user = None
        self.password = None
        self.endpoint = "/fpc/api"
        self._debug = False
        self.proto = 'https'
        self.headers = {'Content-Type': 'application/json'}

    def debug(self, status='off'):
        if status == 'on':
            self._debug = True
        elif status == 'off':
            self._debug = False

        return self._debug
        
    def login(self, ip, user, password):
        self.ip = ip
        self.user = user
        self.password = password

        path = "%s://%s%s/login" % (self.proto, self.ip, self.endpoint)
        headers = self.headers
        data = {
            "user": self.user,
            "password": self.password
        }
        r = requests.post(path, headers=headers, data=json.dumps(data), verify=False)
        self.dprint('REQUEST:', method='POST', path=r.url, data=data)
        self.dprint('RESPONSE:', data=r.json())
        
        self.headers['fpc-sid'] = str(r.json()['fpc-sid'])

    def logout(self):

        path = "%s://%s%s/logout" % (self.proto, self.ip, self.endpoint)
        r = requests.post(path, headers=self.headers, verify=False)
        self.dprint('REQUEST:', method='POST', path=r.url)
        self.dprint('RESPONSE:', string=r.content)

    def get(self, url):

        path = "%s://%s%s%s" % (self.proto, self.ip, self.endpoint, url)
        r = requests.get(path, headers=self.headers, verify=False)
        self.dprint('REQUEST:', method='GET', path=r.url)
        self.dprint('RESPONSE:', data=r.json())        

    def dprint(self, header, method=None, path=None, data=None, string=None):
        if self._debug:
            print('\n%s\n' % header)
            if path:
                print('%s %s\n' % (method, path))
            if data:
                print(json.dumps(data, indent=2, sort_keys=True))
            if string:
                print(string)
            
                    
