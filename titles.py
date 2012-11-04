import glob
import re
import os
from collections import Counter

token_entry_template = """<File path="docs/{}">
  <Token><TokenIdentifier>//apple_ref/cpp/{}/{}</TokenIdentifier></Token>
</File>"""

title_dict = {
    "function": "func",
    "method": "clm",
    "constructor": "clm",
    "enumeration": "clconst",
    "class": "cl",
    "object": "cl",
    "structure": "tdef",
    "property": "Attribute",
    "attribute": "Attribute",
    "field": "Attribute",       # ?
    "macro": "macro",
    "event": "Event",
    "interface": "cl",          # intf?
    "element": "Attribute",
    "reference": "cat",
    "api": "cat",
    "methods": "cat",
    "functions": "cat",
    "structures": "cat",
    "constants": "cat",
    "interfaces": "cat",
    "types": "cat",
    "enumerations": "cat",
    "properties": "cat",
    # routine: ?
}

def create_tokens(out_path):
    from main import root_path
    print "Creating token file"
    out_file = open(out_path, "wb")
    print >>out_file, '<Tokens version="1.0">'
    
    fs = glob.glob("{}*.html".format(root_path))
    titles = Counter()
    referenced = 0
    for f in fs:
        d = open(f, "rb").read()
        try:
            title = re.search('<h1 id="TopicTitle">(.*?)</h1>', d, re.DOTALL).group(1)
        except:
            print "Failed to parse title:", f
            continue
        
        title_type = title.lower().split()[-1]
        title_name = title.rsplit(' ', 1)[0]
        if title_type in title_dict.keys():
            file_path = os.path.basename(f)
            obj_type = title_dict[title_type]
            if obj_type in ['cat', 'intf']:
                title_name = title
            print >>out_file, token_entry_template.format(file_path, obj_type, title_name)
            referenced += 1
    
        titles.update([title_type])
        
    print >>out_file, '</Tokens>'
    
    print "%d added to token" % referenced
    print "Top Titles:"
    for title, count in titles.most_common(40):
        print '\t', title, count
        
if __name__ == "__main__":
    create_tokens("MSDN.docset/Contents/Resources/Tokens.xml")