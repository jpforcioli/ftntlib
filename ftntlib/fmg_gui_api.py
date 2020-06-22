import requests

class FmgGuiApi():
    def __init__(self):
        self._proto = 'https'
        self._host = None
        self._port = None
        self._base_url = None 
        self._web_session = requests.Session()
        self._debug = None

    def debug(value):
        if value == 'on':
            self._debug = True
        else
            self._debug = False

        return self._debug

    def login(self, host, login, password, port=''):
        self._host = host
        self._port = port
        self._base_url = '{}://{}:{}/'.format(proto,
                                              host,
                                              port)

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
        response = self._web_session.post(login_url1, json=request_body)

        ## This request will retrieve the XSRF-TOKEN and csrftoken cookies
        response = self._web_session.get(login_url2)