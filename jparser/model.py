#!/bin/env python
#encoding=utf-8
import re
import lxml
import lxml.html
import urlparse
from .tags_util import clean_tags_only, clean_tags_hasprop, clean_tags_exactly, clean_tags
from .region import Region

class PageModel(object):
    def __init__(self, page, url = ""):
        assert type(page) is unicode
        for tag in ['style','script']:
            page = clean_tags(page, tag)
        page = clean_tags_hasprop(page, "div", "(display:.?none|comment|measure)")
        page = clean_tags_only(page, "(span|section|font|em)")
        self.doc = lxml.html.fromstring(page)
        self.url = url
        self.region = Region(self.doc)

    def extract_content(self, region):
        items = region.xpath('//p/text()|//div/text()|//table|.//img')
        tag_hist = {}
        for item in items:
            if  hasattr(item,'tag'):
                continue
            t = item.getparent().tag
            if t not in tag_hist:
                tag_hist[t] = 0
            tag_hist[t] += len(item.strip())
        winner_tag = None
        if len(tag_hist) > 0:
            winner_tag = max((c,k) for k,c in tag_hist.items())[1]
        contents = []
        for item in items:
            if not hasattr(item,'tag'):
                txt = item.strip()
                if item.getparent().tag != winner_tag:
                    continue
                contents.append({"type":"text","data":txt})
            elif item.tag == 'table':
                if item != region:
                    table_s = lxml.html.tostring(item)
                    contents.append({"type":"html","data":table_s})
                else:
                    for sub_item in item.xpath("//td/text()"):
                        contents.append({"type":"text","data":sub_item})
            elif item.tag == 'img':
                for img_prop in ('original', 'src', 'data-original', 'src-info', 'file','data-src'):
                    src =  item.get(img_prop)
                    if src != None:
                        break
                if self.url != "":
                    src = urlparse.urljoin(self.url, src)
                contents.append({"type":"image","data":{"src": src}})    
            else:
                pass   
        return contents

    def extract_title(self):
        doc = self.doc
        tag_title = doc.xpath("/html/head/title/text()")
        t_list = doc.xpath("//h1/text()")
        s_tag_title = "".join(tag_title)
        for p in t_list:
            if s_tag_title.startswith(p) or s_tag_title.endswith(p):
                return p
        s_tag_title = "".join(re.split(r'_|-\s',s_tag_title)[:1])
        return s_tag_title

    def extract(self):
        title = self.extract_title()
        region = self.region.locate()
        if region == None:
            return {'title':'', 'content':[]}
        region_html = lxml.html.tostring(region)
        region_html = clean_tags_only(region_html, "(a|!)")
        region_html = clean_tags_exactly(region_html, "(b|strong)")
        clean_region = lxml.html.fromstring(region_html)
        content = self.extract_content(clean_region)
        return {"title":title , "content": content}

