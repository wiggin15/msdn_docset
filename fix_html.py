import re
import os
import shutil
import urllib
import sys

css_dict = {}
css_index = 0

def fix_css(page_data):
    """ Update CSS reference in an HTML code; download the css if it doesn't exist locally """
    from main import crawl_path, root_path
    global css_index
    global css_dict

    try:
        css = re.search('<link rel="stylesheet" type="text/css" href="(.*?)" />', page_data).group(1)
    except:
        print "Failed to find css reference"
        return page_data

    if not css.startswith("http"):
        return page_data

    if css not in css_dict.keys():
        local_file = "Combined_{}.css".format(css_index)
        css_index += 1
        print "Found new CSS, downloading. index={}".format(css_index)
        urllib.urlretrieve(css, os.path.join(root_path, local_file))
        css_dict[css] = local_file

    page_data = re.sub('<link rel="stylesheet" type="text/css" href="(.*?)" />', '<link rel="stylesheet" type="text/css" href="{}" />'.format(css_dict[css]), page_data, count=1)
    return page_data

def fix_imgs(page_data):
    from main import crawl_path, root_path
    for img in ["http://i.msdn.microsoft.com/Areas/Epx/Themes/Metro/Content/ImageSprite.png",
                "http://i.msdn.microsoft.com/dynimg/IC600829.png"]:
        local_file = img.rsplit("/")[-1]
        if not os.path.exists(os.path.join(root_path, local_file)):
            print "Found new image, downloading"
            urllib.urlretrieve(img, os.path.join(root_path, local_file))
        page_data = page_data.replace(img, local_file)
    return page_data

def fix_html(path):
    from main import crawl_path, root_path
    page_data = open(os.path.join(crawl_path, path), "rb").read()
    # fix links
    page_data = page_data.replace("http://msdn.microsoft.com/en-us/library/windows/desktop/", "")
    page_data = page_data.replace("/en-us/library/windows/desktop/", "")
    page_data = page_data.replace("(v=vs.85).aspx", ".html")
    # add content encoding for browser
    page_data = page_data.replace("<head>", """<head>\n<meta http-equiv="Content-Type" content="text/html;charset=UTF-8">\n""")
    # remove header and footer:
    #page_data = re.sub("""<div id="ux-footer">.*?<div class="footerPrintView">""", """<div class="footerPrintView" style="display:block">""", page_data, flags=re.DOTALL)
    page_data = re.sub("""<div class="blocks">.*?<div class="footerMSLogo">""", """<div class="footerMSLogo">""", page_data, flags=re.DOTALL)
    page_data = re.sub("""<div id="ux-header">.*?</div>\s*<div class="breadCrumb">""", """<div class="breadCrumb">""", page_data, flags=re.DOTALL)
    # remove other stuff
    page_data = re.sub("""<div id="contentFeedback">.*?</form>\s*</div>""", "", page_data, flags=re.DOTALL)
    page_data = re.sub("""<div id="ratingCounterSeperator.*?</span>\s*</div>""", "", page_data, flags=re.DOTALL)
    page_data = re.sub("""<div class="communityContentContainer">.*?</div>(\s*</div>\s*</div>\s*<div class="clear"></div>)""", "\\1", page_data, flags=re.DOTALL)
    page_data = re.sub("""<script type="text/javascript" class="mtps-injected">.*?</script>""", "", page_data, flags=re.DOTALL)
    page_data = re.sub("""<noscript>.*?</noscript>""", "", page_data, flags=re.DOTALL)
    page_data = re.sub("""<a id="NavigationResize" href="javascript:epx.library.navigationResize.resize()">.*?</a>""", "", page_data, flags=re.DOTALL)
    # remove reference to different section of MSDN from this article originates:
    page_data = re.sub("""<div class="topicNotInScope" id="topicNotInScope">.*?<div class="Clear"></div>\s*</div>\s*</div>""", "", page_data, flags=re.DOTALL)
    # remove "send comments about this topic to microsoft":
    page_data = re.sub("""<a href="mailto.*?</a>""", "", page_data, flags=re.DOTALL)
    # remove the first two elements of the breadcrumb:
    page_data = re.sub("""<a href="http://msdn.microsoft.com/en-us/windows/desktop/" title="Dev Center - Desktop">"""
                       """Dev Center - Desktop</a>\s*<span>&gt;</span>\s*<a href="" title="Docs">Docs</a>"""
                       """(\s*<span>&gt;</span>)?""", "", page_data)
    page_data = re.sub("""<script id="CommentTemplate" type="text/x-jquery-tmpl">.*?</script>""", "", page_data, flags=re.DOTALL)
    # this fixes some .NET pages that get cut after removing the counter and cross-reference:
    page_data = re.sub("""<div class="lw_vs">""", """<div id="ratingCounter" style="display:block"></div><div class="lw_vs">""", page_data)
    page_data = fix_css(page_data)
    page_data = fix_imgs(page_data)

    html_path = path.replace("(v=vs.85)", "").replace(".aspx", ".html")
    open(os.path.join(root_path, html_path), "wb").write(page_data)

def fix_htmls():
    from main import crawl_path, root_path
    files_to_fix = os.listdir(crawl_path)
    total = len(files_to_fix)
    precent = int(total / 100)
    current = 0
    print "Patching HTML files"
    for path in files_to_fix:
        fix_html(path)
        if precent != 0 and current % precent == 0:
            print "\r    \r%d%%" % (float(current) / float(total) * 100.0),
            sys.stdout.flush()
        current += 1
    shutil.copy(os.path.join(root_path, "aa904962.html"), os.path.join(root_path, "index.html"))
    print "\r100%"

if __name__ == "__main__":
    fix_htmls()
