import getpass
import requests
import json

class fmgapi():
    """
    A class used to operate the Fortinet FortiManager.

    ...

    Attributes
    ----------
    None

    Methods
    -------
    login(host, login, password=None, protocol='https', port=443)
        Login to the FortiMnager.
    """

    def __init__(self):
        self._id = 1
        self._session = requests.Session()
        self._host = None
        self._login = None
        self._password = None
        self._protocol = None
        self._port = None
        
    def login(self, host, login, password=None, protocol='https', port=443):
        """
        Login to the FortiManager.

        Parameters
        ----------
        host: str
            The FortiManager IP or FQDN
        login: str
            The FortiManager administrator login
        password: str
            The FortiManager administrator password.
            If not given, user will be prompted to enter one.
        protocol: str
            The protocol to be used.
            Default is 'https'.
        port: int
            The TCP port to be used.
            Default is 443.
        """
        
        self._host = host
        self._login = login
        self._password = getpass.getpass()
        self._protocol = protocol
        self._port = port

        self._url = '{}://{}:{}/jsonrpc'.format(protocol,
                                                host,
                                                port)

        jsonrpc = {
            'id': self._id,
            'method': 'exec',
            'params': [
                {
                    'url': '/sys/login/user',
                    'data': {
                        'user': self._login,
                        'passwd': self._password,
                    },
                },
            ],
            'session': False,
        }            

        response = self._session.post(self._url, json=jsonrpc, verify=False)

        self._session_id = response.json()['session']

        if self._debug:
            self.debug_print(response)

    def logout(self):
        """
        Logout from the FortiManager
        
        Parameters
        ----------
        No parameter required.
        """
        
        jsonrpc = {
            'id': self._id,
            'method': 'exec',
            'params': [
                {
                    'url': '/sys/logout',
                },
            ],
            'session': self._session_id
        }

        response = self._session.post(self._url, json=jsonrpc)

        if self._debug:
            self.debug_print(response)        

    def debug(self, status):
        """
        Enable/Disable debug mode.

        Parameters
        ----------

        status: bool
            When True, debug is enabled.
            When False, debug is disabled.
        """
        self._debug = bool

    def debug_print(self, response):
        """
        Process requests.Response object to print debug messages.
        
        Is used internally by fmgapi class methods when debug mode is
        enabled.

        Parameters
        ----------

        response: requests.Response
            Object returned by the requests.Session.{get,etc.} methods.
        """
        
        print('REQUEST:')
        method = response.request.method
        url = response.request.url
        body = json.dumps(json.loads(response.request.body), indent=4)
        print('{method} {url}'.format(method, url))
        print(body)

        print('RESPONSE:')
        content = json.dumps(json.loads(response.content), indent=4)
        print(content)

if __name__ == '__main__':
    fmg = fmgapi()
    fmg.debug(True)
    fmg.login('35.204.236.88', 'admin', port=10408)
    fmg.logout()
    
