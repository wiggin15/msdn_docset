import glob
import re
import os
from collections import Counter

token_entry_template = """<File path="docs/{}">
  <Token><TokenIdentifier>//apple_ref/cpp/{}/{}</TokenIdentifier></Token>
</File>"""

# https://kapeli.com/docsets#supportedentrytypes
title_dict = {
    "api": "Interface",
    "attribute": "Attribute",
    "class": "Class",
    "component": "Component",
    "constants": "Constant",
    "constructor": "Constructor",
    "element": "Element",
    "enumeration": "Enum",
    "event": "Event",
    "example": "Sample",
    "field": "Field",
    "file": "File",
    "function": "Function",
    "interface": "Interface",
    "macro": "Macro",
    "member": "Variable",
    "message": "Event",
    "method": "Method",
    "object": "Object",
    "overview": "Category",
    "property": "Property",
    "provider": "Provider",
    "reference": "Category",
    "resource": "Resource",
    "routine": "Subroutine",
    "sample": "Sample",
    "service": "Service",
    "structure": "Struct",
    "test": "Test",
    "type": "Type",
    "union": "Union",

    "attributes": "Category",
    "classes": "Category",
    "components": "Category",
    "constructors": "Category",
    "elements": "Category",
    "enumerations": "Category",
    "events": "Category",
    "examples": "Category",
    "files": "Category",
    "functions": "Category",
    "interfaces": "Category",
    "macros": "Category",
    "members": "Category",
    "methods": "Category",
    "objects": "Category",
    "properties": "Category",
    "references": "Category",
    "resources": "Category",
    "routines": "Category",
    "samples": "Category",
    "services": "Category",
    "structures": "Category",
    "tests": "Category",
    "types": "Category",
    "values": "Category",
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
            title = re.search('<h1 class="title">([^\[(<]*)', d, re.DOTALL).group(1)
            assert title.strip()
        except:
            print "Failed to parse title:", f
            continue

        title = title.strip()
        if title[0].isdigit():
            continue
        title_type = title.lower().split()[-1]
        title_name = title.rsplit(' ', 1)[0]
        if title_type in title_dict.keys():
            file_path = os.path.basename(f)
            obj_type = title_dict[title_type]
            if title.lower().startswith("about"):
                obj_type = "Category"
            if obj_type in ["Category", "Interface"]:
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
