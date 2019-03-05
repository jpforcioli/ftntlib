#!/usr/bin/env python

###################################################################
#
# fmg_xmlapi.py by Ashton Turpin
# originally  based on fmgWS.py by Jean-Rene Labarriere
#
# A Python module to access the FortiManager/FortiAnalyzer XML API 
#
###################################################################

from suds.client import Client
from suds.plugin import MessagePlugin
from lxml import etree
import time


class LogPlugin(MessagePlugin):


    def sending(self, context):
         root=etree.XML(str(context.envelope))
         tree=etree.ElementTree(root)
         print('REQUEST:')
         print(etree.tostring(tree, pretty_print=True))


    def received(self, context):
         root=etree.XML(str(context.reply))
         tree=etree.ElementTree(root)
         print('RESPONSE:')
         print(etree.tostring(tree, pretty_print=True))


class FortiManagerXML:


    def __init__(self,host,user,password,port=8080,verify=0):
        if verify==0:
            import ssl 
            ssl._create_default_https_context = ssl._create_unverified_context
        self._url='https://'+str(host)+':'+str(port)+'/'
        self._client=Client(self._url)
        self._servicePass=self._client.factory.create('servicePass')
        self._servicePass.userID=user
        self._servicePass.password=password
        return


    def debug(self,state):
        if state=='on':
            self._client.set_options(plugins=[LogPlugin()])
        else:
            self._client.set_options(plugins=[])

            
    def do(self,method,data):
        try:
            result=self._client.factory.create(method+'Response')
            result=getattr(self._client.service,method)(self._servicePass,**data)
#            print (result)
            return result
        except Exception as e:
            print(type(e))
            print(e)


    def __getattr__(self,method,data={}):
        def wrapperfunc(data={}):
            result=self.do(method,data) 
            return result
        return wrapperfunc


    def taskwait(self,adom,taskid):
        wait = 0
        interval = 5 
        timeout = 120
        while (wait < timeout):
           data = {'taskId': taskid }
           if adom:
               data['adom'] = adom
           result = self.do('getTaskList',data)
           if result['errorMsg']['errorCode'] == 0:
               if result['taskList'][0]['status'] in ['3','4','5','7','8']:
                   return result
               else:
                   time.sleep(interval) 
                   wait = wait + interval
           else:
               return result


