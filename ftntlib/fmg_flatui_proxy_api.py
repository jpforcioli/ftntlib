import sys
import logging
import requests
import json

if sys.version_info >= (2,7):
    logging.captureWarnings(True)
else:
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings()
    
class FmgFlatuiProxyApi():
    def __init__(self):
        self._proto = 'https'
        self._host = None
        self._port = None
        self._base_url = None 
        self._web_session = requests.Session()
        self._debug = None
        self._debug_cookie = None
        self._debug_header = None

    def debug(self, value):
        if value == 'on':
            self._debug = True
        else:
            self._debug = False

        return self._debug

    def debug_cookie(self, value):
        if value == 'on':
            self._debug_cookie = True
        else:
            self._debug_cookie = False

        return self._debug_cookie

    def debug_header(self, value):
        if value == 'on':
            self._debug_header = True
        else:
            self._debug_header = False

        return self._debug_header

    def debug_print(self, response):
        if self._debug:
            # REQUEST
            method = response.request.method
            url = response.request.url
            body = response.request.body

            print('>>>')
            print('{} {}'.format(method, url))

            if body:
                print('\n{}'.format(json.dumps(json.loads(body), indent=4)))

            if self._debug_header:
                print('>>> [headers]')
                for header in self._web_session.headers:
                    print('{}: {}'.format(header, self._web_session.headers[header]))

            if self._debug_cookie:
                print('>>> [cookies]')
                for cookie in self._web_session.cookies:
                    print(cookie)

            # RESPONSE
            status_code = response.status_code
            content_type = response.headers.get('content-type')

            print('<<<')
            print('{}'.format(status_code))

            if content_type == 'application/json':
                print('\n{}'.format(json.dumps(json.loads(response.text), indent=4)))
            else:
                print('\n{}'.format(response.text))

            if self._debug_cookie:
                print('<<< [cookies]')
                for cookie in response.cookies:
                    print(cookie)

    def set_headers_from_cookies(self, response):
        x_csrftoken = {
            'X-CSRFToken': self._web_session.cookies['csrftoken']
        }
        #self._web_session.headers.update(x_csrftoken)

        xsrf_token = {
            'XSRF-TOKEN': self._web_session.cookies['XSRF-TOKEN']
        }
        self._web_session.headers.update(xsrf_token)        

        #self._web_session.headers.update(x_xsrf_token)                

    def login(self, host, login, password, port=443):
        '''
        According to Mantis #0643655, we have to set Content-Type to application/json
        '''
        self._web_session.headers.update({'Content-Type': 'application/json'})

        self._host = host
        self._port = port
        self._base_url = '{}://{}:{}'.format(self._proto,
                                              self._host,
                                              self._port)

        login_url1 = '{}/cgi-bin/module/flatui_auth'.format(self._base_url)
        login_url2 = '{}/p/app/'.format(self._base_url)

        request_body = {
            'url': '/gui/userauth',
            'method': 'login',
            'params': {
                'username': login,
                'secretkey': password,
                'logintype': 0,
            },
        }

        ## This request will retrieve the CURRENT_SESSION and HTTP_CSRF_TOKEN cookies 
        response = self._web_session.post(login_url1, json=request_body, verify=False)
        self.debug_print(response)

        ## This request will retrieve the XSRF-TOKEN and csrftoken cookies
        response = self._web_session.get(login_url2, verify=False)
        self.debug_print(response)

        ## Set X-CSRFToken, XSR-TOKEN and X-XSRF-TOKEN
        self.set_headers_from_cookies(response)

    def flatui_proxy(self, method, params=None, json=None):
        url = '{}/cgi-bin/module/flatui_proxy'.format(self._base_url)

        if method == 'get':
            response = self._web_session.get(url, params=params)

        elif method == 'post':
            response = self._web_session.post(url, params=params, json=json)
            self.debug_print(response)