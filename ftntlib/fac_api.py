import requests
import json

# To avoid the SSL warning
# Caught in https://stackoverflow.com/questions/15445981/how-do-i-disable-the-security-certificate-check-in-python-requests
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

class fortiauthenticator:

    def __init__(self):
        self._username = None
        self._secret_key = None
        self._ip = None
        self._version = None
        self._session = requests.Session()
        self._session.headers.update({'Accept': 'application/json'})
        self._debug = False
        
    def login(self, ip, username, secret_key, version='v1'):
        self._ip = ip
        self._username = username
        self._secret_key = secret_key
        self._base_url = f'https://{ip}/api/{version}'
        self._session.auth = (username, secret_key)

    def debug(self, status):
        if status == 'on':
            self._debug = True
        else:
            self._debug = False

    def debug_print(self, response):
        # REQUEST
        request_method = response.request.method
        request_url = response.request.url
        request_body = response.request.body
        print('==>')
        print(f'{request_method} {request_url}')
        if request_body:
            print(request_body.decode())

        # RESPONSE
        response_code = response.status_code
        response_reason = response.reason
        print('<==')
        print(f'{response_code} {response_reason}')
        print(json.dumps(response.json(), indent=2))

    def generate_response(self, response):

        if self._debug:
            self.debug_print(response)
            
        response_block = {
            'status': {
                'code': response.status_code,
                'reason': response.reason,
            },
            'data': response.json()
        }

        return response_block

    def get(self, resource, params=None):
        url = f'{self._base_url}/{resource}/'
        response = self._session.get(url, params=params, verify=False)

        return self.generate_response(response)

    def patch(self, resource, params=None, data=None):
        url = f'{self._base_url}/{resource}/'

        response = self._session.patch(url,
                                       params=params,
                                       json=data,
                                       verify=False)

        return self.generate_response(response)
    
if __name__ == '__main__':

    fac = fortiauthenticator()
    fac.login('10.222.51.147:10412',
              'ztpadmin',
              '5ftH8hCEgxSLPHDr49Ubp8TCPabjlEPrE5fbXkGe')

    response = fac.get(f'usercerts')
    print(response)

    data = {
        'status': 'revoked',
        'revocation_reason': 'Cessation Of Operation',
    }
    response = fac.patch(f'usercerts/2', data=data)
    print(response)
