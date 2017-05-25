import heapq
import re
from math import log, e

class Region(object):

    def __init__(self, doc):
        self.doc = doc
        self.max_depth = 4
        self.region_ratios = (0.6, 0.75, 1.0)
        self.min_sentence_len = 15
        self.max_sub_div_len = 10
        self.window_size = 2
        self.candidates_count = 3
        self.stripper = re.compile(r'\s+')

    def find_common_parent(self, k1, k2):
        all_parent = []
        p = k2.getparent()
        while p!= None and p.tag != 'html' and p.tag != 'body':
            if p.tag != 'a':
                all_parent.append(p)
            p = p.getparent()
        p1 = k1.getparent()
        depth = 1
        while p1!= None and p1.tag != 'html' and p1.tag != 'body':
            if p1.tag in ('span','font','li','ul','td','tr','br'):
                p1 = p1.getparent()
                continue
            if p1.tag == 'p':
                p1 = p1.getparent()
                depth += 1
                continue
            if p1 in all_parent:
                break
            p1 = p1.getparent()
            depth +=1
        if depth > self.max_depth:
            return k1.getparent().getparent()
        return p1

    def locate(self):
        p_list = self.doc.xpath('//p/text()|//div/text()|//td/text()')
        unimportant_texts = set(self.doc.xpath("//a/text()|//dd//text()"))
        N_p = len(p_list)
        window_size = self.window_size
        for region_ratio in self.region_ratios:
            candidates  = [(len("".join([xx.strip() for xx in p_list[max(i-window_size,0):i+window_size]])) / log(i+e), x,i ) 
                            for i,x in enumerate(p_list) if i < N_p * region_ratio 
                             and len(self.stripper.sub("",x)) > self.min_sentence_len
                             and x not in unimportant_texts]
            if len(candidates) >= self.candidates_count:
                break
        top_list = heapq.nlargest(self.candidates_count, candidates)
        if len(top_list) < 1:
            return None
        k1 = top_list[0][1]
        n1 = top_list[0][2]
        if len(top_list) < 2:
            return k1.getparent()
        neighbours = top_list[1:]
        neighbours.sort(key = lambda x: -1*abs(x[2] - n1))
        k2 = neighbours[0][1]
        region = self.find_common_parent(k1, k2)
        sub_div_count =  len(region.xpath('./div'))
        sub_p_count =  len(region.xpath('./p'))
        if sub_div_count > self.max_sub_div_len and sub_div_count > sub_p_count:
            return k1.getparent().getparent()
        return region
