import requests

class PageGetter(object):
    def __init__(self, base_url):
        self._session = requests.Session()

    def urlretrieve(self, remote_url, local_url):
        response = self._session.get(remote_url)
        html = response.text.encode(response.encoding)
        open(local_url, "wb").write(html)
        return html
