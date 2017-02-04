import urllib
import re
import os
import shutil
from page_getter import PageGetter
from titles import create_tokens
from fix_html import fix_htmls
import sys

# documentation for creating docsets for Dash: http://kapeli.com/docsets/

base_url = "http://msdn.microsoft.com/en-us/library/windows/desktop/"
docset_root = "MSDN.docset"
root_path = "{}/Contents/Resources/Documents/docs/".format(docset_root)
crawl_path = "download_folder/"

def crawl():
    page_getter = PageGetter(base_url)
    urls_to_visit = ["ee663300.aspx"]   # MSDN page: "Windows desktop app development"
    known_urls = set(urls_to_visit)   # URLs we visited or will visit
    visited_count = 0

    while len(urls_to_visit) > 0:
        cur_url = urls_to_visit.pop(0)
        local_url = os.path.join(crawl_path, cur_url)
        remote_url = base_url + cur_url
        print cur_url, "(%d remaining, %d visited)" % (len(urls_to_visit), visited_count),
        sys.stdout.flush()
        if os.path.exists(local_url):
            cur_url_html = open(local_url, "rb").read()
            print "\r                                                                           \r",
        else:
            cur_url_html = page_getter.urlretrieve(remote_url, local_url)
            print
        visited_count += 1
        new_urls = re.findall("(?:href|src)=['\"].*?en-us/library/windows/desktop/(\w\w\d{6}\(v=vs.85\).aspx)['\"]", cur_url_html, re.I)
        new_urls = set(url for url in new_urls if url not in known_urls)
        urls_to_visit.extend(list(new_urls))
        known_urls.update(new_urls)
    print "Done crawling. Crawled %d pages" % (visited_count,)

def main():
    if not os.path.exists(root_path):
        os.makedirs(root_path)
    if not os.path.exists(crawl_path):
        os.makedirs(crawl_path)
    crawl()
    fix_htmls()
    create_tokens("{}/Contents/Resources/Tokens.xml".format(docset_root))
    shutil.copy("static/icon.png", "{}/".format(docset_root))
    shutil.copy("static/Info.plist", "{}/Contents/".format(docset_root))
    shutil.copy("static/Nodes.xml", "{}/Contents/Resources/".format(docset_root))
    os.system("/Applications/Xcode.app/Contents/Developer/usr/bin/docsetutil index {}".format(docset_root))

if __name__ == "__main__":
    main()
