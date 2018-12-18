#! /usr/bin/python

from fpc_restapi import FortiPortalREST

ip = '192.168.194.195'
user = 'spuser'
password = 'test123'

api = FortiPortalREST()
api.debug('on')
api.login(ip, user, password)
api.get('/customers')
api.logout()
api.debug('off')

