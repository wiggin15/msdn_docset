import httplib
import urlparse
from StringIO import StringIO
from gzip import GzipFile
import os

class PageGetter(object):
    def __init__(self, base_url):
        self.conn = httplib.HTTPConnection(urlparse.urlsplit(base_url).netloc, httplib.HTTP_PORT)
        
    def urlretrieve(self, remote_url, local_url):
        for i in range(10):
            try:
                self.conn.request("GET", urlparse.urlsplit(remote_url).path, headers={"Accept-Encoding": "gzip"})
                response = self.conn.getresponse()
                cur_url_html = response.read()
                if dict(response.getheaders())["content-encoding"] == "gzip":
                    cur_url_html = GzipFile(fileobj=StringIO(cur_url_html)).read()
                if not os.path.exists(os.path.dirname(local_url)):
                    os.makedirs(os.path.dirname(local_url))
                open(local_url, "wb").write(cur_url_html)
                return cur_url_html
            except:
                pass