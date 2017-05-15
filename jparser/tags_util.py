import re

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
