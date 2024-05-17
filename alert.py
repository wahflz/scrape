import urllib
import http.client
from . import APP_DIR

class Pushover:
    PUSHOVER_API_URL = 'api.pushover.net:443'

    def __init__(self, app_token: str, user_key: str):
        self.app_token = app_token
        self.user_key = user_key

    def __enter__(self):
        self.cnx = http.client.HTTPSConnection(self.PUSHOVER_API_URL)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.cnx:
            self.cnx.close()

    def message(self, content: str):
        self.cnx.request('POST', '/1/messages.json',
            urllib.parse.urlencode({
                'token': self.app_token,
                'user': self.user_key,
                'message': content,
            }),
            { "Content-type": "application/x-www-form-urlencoded" }
        )

        self.cnx.getresponse() # check and raise error, etc. etc.

if __name__ == '__main__':
    from . import load_yaml_config

    config = load_yaml_config(APP_DIR / 'config.yml')
    
    with Pushover(config['pushover']['api_key'], config['pushover']['user_key']) as p:
        p.message('This is a test!')