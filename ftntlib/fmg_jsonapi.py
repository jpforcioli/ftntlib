#!/usr/bin/env python
###################################################################
#
# fmg_jsonapi.py by Ashton Turpin 
#
# A Python module to access the FortiManager/FortiAnalyzer JSON API 
#
###################################################################


import time
import logging
import requests
import json

logging.captureWarnings(True)

class FortiManagerJSON (object):
    
    def __init__ (self):
        self._reqid = 1
        self._sid = None
        self._url = None
        self._ssl_verify = False
        self._debug = False
        self._bbcode = False
        self._ws_mode = False
        self._params = False
        self._skip = False
        self._verbose = False   
        self._root = False
        self._rootpath = None
        self._timeout = None
    
  
    def jprint (self,json_obj):
        return json.dumps(json_obj, indent=2, sort_keys=True)
    
    
    def dprint (self, msg, str):
        if self._bbcode:
            msg = '[color=#008080][b]'+msg+'[/b][/color]'
            str = '[code]'+self.jprint(str)+'[/code]'
        else:
            str = self.jprint(str)
        if self._debug:
            print(msg)
            print(str)
            
                                  
    def debug (self, status):
        if status == 'on':
            self._debug = True
        if status == 'off':
            self._debug = False
            
            
    def bbcode (self, status):
        if status == 'on':
            self._bbcode = True
        if status == 'off':
            self._bbcode = False
    
    
    def skip (self, status):
        if status == 'on':
            self._skip = 1
        if status == 'off':
            self._skip = 0
        if status == 'default':
            self._skip = False
    
    
    def verbose (self, status):
        if status == 'on':
            self._verbose = 1
        if status == 'off':
            self._verbose = False
    
            
    def chroot (self, rootpath):
        if rootpath:
            self._root = True
            self._rootpath = rootpath
        else: 
            self._root = False
    
    
    def params (self, params):
        if params:
            self._params = params

    def timeout (self, timeout):
        if timeout:
            self._timeout = timeout
            
    def workspace_mode (self, status):
        if status == 'auto':
            self._ws_mode = self._detect_ws_mode()
        elif status == 'workflow':
            self._ws_mode = 2
        elif status == 'normal' or status == 'on':
            self._ws_mode = 1
        elif status == 'disabled' or status == 'off':
            self.ws_mode = False                        
        else:
            pass # to do: warn  


    def http_request (self,method,params):
        headers = { 'content-type' : 'application/json' }
        if self._params:
            params[0].update(self._params)
            self._params = False
        datagram = { 'id' : self._reqid, 
                     'session' : self._sid,
                     'method' : method,
                     'params' : params,
                    }
        if self._skip is not False:
            datagram['skip'] = int(self._skip)
        if self._verbose:
            datagram['verbose'] = int(self._verbose)
        if self._root:
            datagram['root'] = self._rootpath
            
        self.dprint('REQUEST:',datagram)

        try: 
            response = requests.post(
                                     self._url, 
                                     data=json.dumps(datagram), 
                                     headers=headers,
                                     verify=self._ssl_verify, 
                                     timeout=self._timeout
                                     )
            response = response.json()
        except requests.exceptions.ConnectionError as cerr:
            print ('Connection ERROR: ', cerr)
            return cerr
        except Exception as err:
            print ('ERROR: ', err)
            return err
        assert response['id'] == datagram['id']
        self.dprint('RESPONSE:',response)
        return self.response(response) 
      
    def response (self, response):
        status = { 'code' : 0 }
        data = {}
        try: 
            if self._sid == None and 'session' in response:
                self._sid = response['session']
            result={}
            if type(response['result']) is list:
                result = response['result'][0]
            else:
                result = response['result']
            if 'status' in result:
                status = result['status'] 
            else:
                status['message'] = 'Did not receive status from host.'
            if 'data' in result:
                data = result['data']
            return status, data
        except Exception as e:
            print ("Response parser error: (%s) %s", type(e), e)
            status['code'] = 1
            status['message'] = 'Response parser error'
            return status, data
                    
    def login (self, ip, user, passwd, ssl=True):
        if ssl:
            self._url = 'https://' + ip + '/jsonrpc'
        else:
            self._url = 'http://' + ip + '/jsonrpc'
        
        params = [ {
                    'url': 'sys/login/user',
                    'data': [ {
                                'passwd': passwd,
                                'user': user
                    } ]
                 } ]  
        status, response = self.http_request('exec', params)
        return status, response
    
                            
    def logout (self):
        params = [ { 'url': 'sys/logout' } ]
        status, response = self.http_request('exec', params)
        self._sid = None
        return status, response

    def _do (self,method,url,data={}):
        store = { 'root' : self._root,
                  'skip' : self._skip,
                  'verbose' : self._verbose }
        self._root = False
        self._skip = False
        self._verbose = False                         
        if method == 'get' or method == 'move':
            if data:
                data['url'] = url
                params = [ data ]
            else:
                params = [{'url' : url }]
        else:
            params = [{ 'url' : url }]
            if data:
                params[0]['data'] = data
        status, response = self.http_request(method,params)
        self._root = store['root']
        self._skip = store['skip']
        self._verbose = store['verbose']
        return status, response

    def do (self,method,params):
        status, response = self.http_request(method,params)
        return status, response
            
    def get (self,url,data={}):
        if data:
            data['url'] = url
            params = [ data ]
        else: 
            params = [{'url' : url }]
        status, response = self.http_request('get',params)
        return status, response
    
    def add (self,url,data={}):
        params = [{ 'url' : url }]
        if data:
            params[0]['data'] = data
        status, response = self.http_request('add',params)
        return status, response
    
    def update (self,url,data={}):
        params = [{ 'url' : url }]
        if data:
            params[0]['data'] = data
        status, response = self.http_request('update',params)
        return status, response
    
    def set (self,url,data={}):
        params = [{ 'url' : url }]
        if data:
            params[0]['data'] = data
        status, response = self.http_request('set',params)
        return status, response
    
    def delete (self,url,data={}):
        params = [{ 'url' : url }]
        if data:
            params[0]['data'] = data
        status, response = self.http_request('delete',params)
        return status, response
    
    def replace (self,url,data={}):
        params = [{ 'url' : url }]
        if data:
            params[0]['data'] = data
        status, response = self.http_request('replace',params)
        return status, response
    
    def clone (self,url,data={}):
        params = [{ 'url' : url }]
        if data:
            params[0]['data'] = data
        status, response = self.http_request('clone',params)
        return status, response
    
    def move (self,url,data):
        data['url'] = url
        params = [ data ]
        status, response = self.http_request('move',params)
        return status, response
    
    def execute (self,url,data={}):
        params = [{ 'url' : url }]
        if data:
            params[0]['data'] = data
        status, response = self.http_request('exec',params)
        return status, response
            
    
    def taskwait (self, taskid):
        url = 'task/task/'+str(taskid)
        wait = 0
        interval = 5 
        timeout = 120
        while (wait < timeout):
            status,response = self._do('get',url)             
            if status['code'] == 0:
                if response['percent'] == 100:
                    return status,response
                else:
                    time.sleep(interval)
                    wait = wait + interval
            else:
                return status,response            
    # Package methods

    def install_package (self,adom,package,scope,flags=['install_chg']):
        url = 'securityconsole/install/package'
        pkg = 'adom/'+adom+'/pkg/'+package
        data =  { 
                  'adom' : adom,
                  'pkg' : pkg,
                  'flags' : flags,
                  'scope' : scope
                  }
        code, resp = self._do('exec',url,data)
        if code == 0: 
            status, response = self.taskwait(resp['data']['task'])
            return status, response
        else:
            return code, resp

    # Device methods

    def get_devid (self,devicename):
        url = 'dvmdb/device/'+str(devicename)
        code, device = self._do('get',url, {'loadsub' : 1 })
        if device['data']['vdom'][0]['devid']:
            return device['data']['vdom'][0]['devid']
        else:
            return 1
    
    def discover_device (self,ip,username,password):
        url = 'dvm/cmd/discover/device'
        deviceinfo = { 'ip' : ip,
                       'adm_usr' : username,
                       'adm_pass' : password
                       }
        data = { 'device' : deviceinfo }
        status, response = self._do('exec',url,data)
        return status, response
    
    def add_device (self,adom,ip,username,password,mgmtmode=3):
        url = 'dvm/cmd/add/device'
        code,response = self.discover_device(ip,username,password)
        device={}
        if code==0:
            device = response['data']['device']
        else:
            return response
        device['mgmt_mode']=mgmtmode
        data = { 'adom' : adom,
                 'device' : device,
                 'flags' : [ 'create_task' , 'nonblocking' ]
                 }
        status, response = self._do('exec',url,data)        
        if response['data']['taskid']:
            status, response = self.taskwait(response['data']['taskid'])
        else:
            return status, response
        ucode,ures = self.update_device(adom,device['name'])
        if ucode !=0:
            return ucode,ures
        rcode,rres = self.reload_devlist(adom,{'name' : device['name']},'dvm')
        if rcode !=0:
            return rcode,rres
        return status, response
        
    def add_devlist (self,adom,deviceinfo):
        url='dvm/cmd/add/dev-list'
        data = { 'adom' : adom,
                 'add-dev-list' : deviceinfo,
                 'flags' : [ 'create_task' , 'nonblocking' ]
                 }
        status, response = self._do('exec',url,data)
        if response['data']['taskid']:
            status, response = self.taskwait(response['data']['taskid'])
        else:
            return status, response
        return status, response
            
    def update_device (self,adom,devicename):
        url = 'dvm/cmd/update/device'
        data = { 'adom' : adom,
                 'device' : devicename,
                 'flags' : [ 'create_task' , 'nonblocking' ]
                 }
        status, response = self._do('exec',url,data)        
        if response['data']['taskid']:
            status, response = self.taskwait(response['data']['taskid'])
        else:
            return status, response
        return status, response

    def update_devlist (self,adom,devlist):
        url = 'dvm/cmd/update/dev-list'
        data = { 'adom' : adom,
                 'reload-dev-member-list' : devlist,
                 'flags' : [ 'create_task' , 'nonblocking' ]
                 }
        status, response = self._do('exec',url,data)        
        if response['data']['taskid']:
            status, response = self.taskwait(response['data']['taskid'])
        else:
            return status, response
        return status, response

    def reload_device (self,adom,devicename,frm='dvm'):
        url = 'dvm/cmd/reload/device'
        data = { 'adom' : adom,
                 'device' : devicename,
                 'flags' : [ 'create_task' , 'nonblocking' ],
                 'tag' : 'Retrieved from JSON API',
                 'from' : frm
                 }
        status, response = self._do('exec',url,data)        
        if response['data']['taskid']:
            status, response = self.taskwait(response['data']['taskid'])
        else:
            return status, response
        return status, response

    def reload_devlist (self,adom,devlist,frm='dvm'):
        url = 'dvm/cmd/reload/dev-list'
        data = { 'adom' : adom,
                 'reload-dev-member-list' : devlist,
                 'flags' : [ 'create_task' , 'nonblocking' ],
                 'tag' : 'Retrieved from JSON API',
                 'from' : frm
                 }
        status, response = self._do('exec',url,data)        
        if response['data']['taskid']:
            status, response = self.taskwait(response['data']['taskid'])
        else:
            return status, response
        return status, response

    def delete_device (self,adom,devicename):
        url = 'dvm/cmd/del/device'
        data = { 'adom' : adom,
                 'device' : devicename,
                 'flags' : [ 'create_task' , 'nonblocking' ]
                 }
        status, response = self._do('exec',url,data)        
        if response['data']['taskid']:
            status, response = self.taskwait(response['data']['taskid'])
        else:
            return status, response
        return status, response

    def delete_devlist (self,adom,deviceinfo):
        url = 'dvm/cmd/del/dev-list'
        data = { 'adom' : adom,
                 'del-dev-member-list' : deviceinfo,
                 'flags' : [ 'create_task' , 'nonblocking' ]
                 }
        status, response = self._do('exec',url,data)        
        if response['data']['taskid']:
            status, response = self.taskwait(response['data']['taskid'])
        else:
            return status, response
        return status, response
    
    def get_unreg_devices (self):
        url = 'dvmdb/device'
        opts = {
                'loadsub' : 0,
                'filter' : [ 'mgmt_mode', '==', 0 ]
                }
        status, response = self._do('get',url,data)        
        return status, response
                       
    def promote_device (self,adom,devicename,username,password):
        c,r = self._do('get', 
                       'dvmdb/device/'+str(devicename), 
                       { 'filter' : ['mgmt_mode', '==', 0] }
                       )
        if c !=0:
            return c,r
        url = 'dvm/cmd/promote/dev-list'
        object = { 'flags' : r['data']['flags'],
                   'ip' : r['data']['ip'],
                   'sn' : r['data']['sn'],
                   'oid' : r['data']['vdom'][0]['devid'],
                   'adm_usr' : username,
                   'adm_pass' : password }
        data = { 'adom': adom,
                 'add-dev-list' : [ object ],
                 'flags' : [ 'create_task', 'nonblocking' ]
                 }
        status, response = self._do('exec',url,data)        
        if response['data']['taskid']:
            status, response = self.taskwait(response['data']['taskid'])
        else:
            return status, response
        return status, response
        
        
    # Workspace methods

    def _detect_ws_mode (self):
        url = 'cli/global/system/global'
        code,response = self._do('get',url)
        return response['data']['workspace-mode']

    def _workspace (self, adom, action,pkgpath=False):
        if pkgpath:
            url = 'pm/config/adom/'+str(adom)+'/_workspace/'+str(action)+'/'+str(pkgpath)
        else:
            url = 'pm/config/adom/'+str(adom)+'/_workspace/'+str(action)
        status, response = self._do('exec',url)
        return status, response
         
    def ws_lock (self, adom):
        status, response = self._workspace(adom,'lock')
        return status, response

    def ws_commit (self, adom):
        status, response = self._workspace(adom,'commit')
        return status, response

    def ws_unlock (self, adom):
        status, response = self._workspace(adom,'unlock')
        return status, response

    def pkg_lock (self, adom, pkgpath):
        status, response = self._workspace(adom,'lock',pkgpath)
        return status, response

    def pkg_commit (self, adom, pkgpath):
        status, response = self._workspace(adom,'commit',pkgpath)
        return status, response

    def pkg_unlock (self, adom, pkgpath):
        status, response = self._workspace(adom,'unlock',pkgpath)
        return status, response
    

    # Workflow methods
    """
    def _workflow (self, adom, action, session=False, params=False):
        if session:
            url = 'dvmdb/adom/'+str(adom)+'/workflow/'+str(action)+'/'+str(session)
            if params:
               status, response = self._do('exec',url,params)
            else: 
               status, response = self._do('exec',url)
            return status, response
        else: 
            url = 'dvmdb/adom/'+str(adom)+'/workspace/'+str(action)
            status, response = self._do('exec',url)       
            return status, response  
     """       
         
