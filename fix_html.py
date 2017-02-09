import re
import os
import shutil
import urllib
import sys

css_dict = {}
css_count = 0
empty_count = 0

def fix_css(page_data):
    """ Update CSS reference in an HTML code; download the css if it doesn't exist locally """
    from main import crawl_path, root_path
    global css_count
    global css_dict
    global empty_count

    css_found = re.findall('<link rel="stylesheet" type="text/css" href="([^"]*)" />', page_data)

    if len(css_found) == 0:
        empty_count += 1

    for css_url in css_found:
        if not css_url.startswith("http"):
            continue

        if css_url not in css_dict.keys():
            local_file = "css_{}.css".format(css_count)
            css_count += 1
            css_data = urllib.urlopen(css_url).read()
            css_data = fix_imgs(css_data)
            open(os.path.join(root_path, local_file), "wb").write(css_data)
            css_dict[css_url] = local_file

        page_data = page_data.replace(css_url, css_dict[css_url])

    return page_data

def fix_imgs(page_data):
    from main import crawl_path, root_path
    from urlparse import urlparse
    for img_url in ["https://i-msdn.sec.s-msft.com/Areas/Epx/Content/Images/ImageSprite.png?v=636221982608587215",
                    "https://i-msdn.sec.s-msft.com/Areas/Library/Content/ImageSprite.png?v=636221982770946327"]:
        local_file = img_url.rsplit("/")[-1].replace(".png?v=", "_") + ".png"
        if not os.path.exists(os.path.join(root_path, local_file)):
            print "Found new image, downloading"
            urllib.urlretrieve(img_url, os.path.join(root_path, local_file))
        parsed_url = urlparse(img_url)
        img_uri = parsed_url.path + "?" + parsed_url.query
        page_data = page_data.replace(img_url, local_file)
        page_data = page_data.replace(img_uri, local_file)
    return page_data

def fix_html(path):
    from main import crawl_path, root_path, base_url
    page_data = open(os.path.join(crawl_path, path), "rb").read()
    # fix links
    page_data = page_data.replace(base_url, "")
    page_data = page_data.replace("/en-us/library/", "")
    page_data = page_data.replace("(v=vs.85).aspx", ".html")
    # add content encoding for browser
    page_data = page_data.replace("<head>", """<head>\n<meta http-equiv="Content-Type" content="text/html;charset=UTF-8">\n""")
    # remove header
    page_data = re.sub('<div id="ux-header".*?<div id="breadcrumbs"', '<div id="breadcrumbs"', page_data, flags=re.DOTALL)
    # remove footer
    page_data = re.sub('<div id="standardRatingBefore".*?<span class="logoLegal">', '<footer class="bottom" role="contentinfo"><span class="logoLegal">', page_data, flags=re.DOTALL)
    # remove breadcrumb button
    page_data = re.sub('class="breadcrumbDropSmall"', "", page_data, flags=re.DOTALL)
    page_data = re.sub(' role="button" aria-expanded="false"', "", page_data, flags=re.DOTALL)
    page_data = re.sub('href="#" target', "", page_data, flags=re.DOTALL)
    # remove TOC slider button
    page_data = re.sub("""<a id="tocMenuToggler".*?</a>""", "", page_data, flags=re.DOTALL)
    # make TOC expanded by default
    page_data = re.sub("""<span id="tocExpandButton".*?</span>""", "", page_data, flags=re.DOTALL)
    page_data = re.sub(""" id="tocExpand">""", "", page_data, flags=re.DOTALL)
    # remove floating right navigation menu (print, export, share...)
    page_data = re.sub("""<div id="rightNavigationMenu".*?<ul id="indoc_toclist"></ul>\s*</div>\s*</div>\s*</div>""", "", page_data, flags=re.DOTALL)
    # remove "topic not in scope" notification
    page_data = re.sub("""<div class="topicNotInScope" id="topicNotInScope">.*?<div class="Clear"></div>\s*</div>\s*</div>""", "", page_data, flags=re.DOTALL)
    # remove "Other Versions" dropbox
    page_data = re.sub("""<div class="lw_vs">.*?<div style="clear:both;">""", '<div style="clear:both;">', page_data, flags=re.DOTALL)
    # remove "not being maintained" messages
    page_data = re.sub("""<div id="archiveDisclaimer">.*not being maintained.</div>""", "", page_data, flags=re.DOTALL)
    # remove injected js
    page_data = re.sub("""<script type="text/javascript" class="mtps-injected">.*?</script>""", "", page_data, flags=re.DOTALL)
    page_data = fix_css(page_data)
    page_data = fix_imgs(page_data)

    html_path = path.replace("(v=vs.85)", "").replace(".aspx", ".html")
    open(os.path.join(root_path, html_path), "wb").write(page_data)

def fix_htmls():
    from main import crawl_path, root_path, main_page
    files_to_fix = os.listdir(crawl_path)
    total = len(files_to_fix)
    precent = int(total / 100)
    current = 0
    print "Patching HTML files"
    for path in files_to_fix:
        fix_html(path)
        if precent != 0 and current % precent == 0:
            print "\r" + " " * 60 + "\r",
            percent_txt = float(current) / float(total) * 100.0
            print "%d%% (downloaded %d css files; %d files have no css link)" % (percent_txt, css_count, empty_count),
            sys.stdout.flush()
        current += 1
    shutil.copy(os.path.join(root_path, main_page.replace("aspx", "html")), os.path.join(root_path, "index.html"))
    print "\r100%% (downloaded %d css files; %d files have no css link)" % (css_count, empty_count)

if __name__ == "__main__":
    fix_htmls()
