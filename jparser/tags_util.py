import re
import lxml

def clean_tags(page, tag):
    reTRIM = r'<{0}[^<>]*?>([\s\S]*?)<\/{0}>'
    return re.sub(reTRIM.format(tag), "", page, flags=re.I)

def clean_tags_hasprop(page, tag, prop):
    reTRIM = r'<{0}[^<>]+?{1}.*?>([\s\S]*?)<\/{0}>'
    return re.sub(reTRIM.format(tag,prop), "", page, flags=re.I)

def clean_tags_only(page, tag):
    reTRIM = r'<\/?{0}[^<>]*?>'
    return re.sub(reTRIM.format(tag), "", page, flags=re.I)

def clean_tags_exactly(page, tag):
    reTRIM = r'<\/?{0}>'
    return re.sub(reTRIM.format(tag), "", page, flags=re.I)

def pick_listed_tags(page, tag):
    res = []
    doc = lxml.html.fromstring(page)
    for bad in doc.xpath("//{}".format(tag)):
        if len(bad)>2:
            res.append(bad)
    return res

def clean_nolisted_tags(doc, tag):
    for bad in doc.xpath("//{}".format(tag)):
        if len(bad)<3:
            bad.drop_tag()
    return doc

def clean_ainp_tags(doc, tag):
    for bad in doc.xpath("//p/{}".format(tag)):
        bad.drop_tag()
    return doc
