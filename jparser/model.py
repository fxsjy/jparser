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
        self.impurity_threshold = 30
        self.anchor_ratio_limit = 0.3
        self.stripper = re.compile(r'\s+')

    def extract_content(self, region):
        items = region.xpath('.//text()|.//img|./table')
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
                parent_tag = item.getparent().tag
                if  parent_tag != winner_tag \
                    and len(self.stripper.sub("",txt)) < self.impurity_threshold \
                    and parent_tag != 'li':
                    continue
                if txt == "":
                    continue
                contents.append({"type":"text","data":txt})
            elif item.tag == 'table':
                if winner_tag == 'td':
                    continue
                if item != region:
                    for el in item.xpath(".//a"):
                        el.drop_tag()
                    table_s = lxml.html.tostring(item)
                    contents.append({"type":"html","data":table_s})
                else:
                    for sub_item in item.xpath("//td/text()"):
                        contents.append({"type":"text","data":sub_item})
            elif item.tag == 'img':
                for img_prop in ('original', 'file', 'data-original', 'src-info', 'data-src', 'src'):
                    src =  item.get(img_prop)
                    if src != None:
                        break
                if self.url != "":
                    if not src.startswith("/") and not src.startswith("http") and not src.startswith("./"):
                        src = "/" + src
                    src = urlparse.urljoin(self.url, src, False)
                contents.append({"type":"image","data":{"src": src}})    
            else:
                pass   
        return contents

    def extract_title(self):
        doc = self.doc
        tag_title = doc.xpath("/html/head/title/text()")
        s_tag_title = "".join(re.split(r'_|-',"".join(tag_title))[:1])
        title_candidates = doc.xpath('//h1/text()|//h2/text()|//h3/text()|//p[@class="title"]/text()')
        for c_title in title_candidates:
            c_title = c_title.strip()
            if c_title!="" and (s_tag_title.startswith(c_title) or s_tag_title.endswith(c_title)):
                return c_title
        sort_by_len_list = sorted((-1*len(x.strip()),x) for x in ([s_tag_title] + title_candidates))
        return sort_by_len_list[0][1]

    def extract(self):
        title = self.extract_title()
        region = self.region.locate()
        if region == None:
            return {'title':'', 'content':[]}
        rm_tag_set = set([])
        for p_el in region.xpath(".//p|.//li"):
            child_links = p_el.xpath(".//a/text()")
            count_p = len(" ".join(p_el.xpath(".//text()")))
            count_a = len(" ".join(child_links))
            if float(count_a) / (count_p + 1.0) > self.anchor_ratio_limit:
                p_el.drop_tree()
        for el in region.xpath(".//a"):
            rm_tag_set.add(el)
        for el in region.xpath(".//strong|//b"):
            rm_tag_set.add(el)
        for el in rm_tag_set:
            el.drop_tag()
        content = self.extract_content(region)
        return {"title":title , "content": content}
