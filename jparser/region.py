import heapq

class Region(object):

    def __init__(self, doc):
        self.doc = doc
        self.max_depth = 3
        self.region_ratios = (0.6, 0.7, 0.9)
        self.min_sentence_len = 15
        self.window_size = 2
        self.candidates_count = 3

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
            if p1.tag in ('span','font','li','ul','td','tr'):
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
            return k1.getparent()
        return p1

    def locate(self):
        p_list = self.doc.xpath('//p/text()|//div/text()|//span/text()|//font/text()|//td/text()')
        N_p = len(p_list)
        window_size = self.window_size
        for region_ratio in self.region_ratios:
            candidates  = [(len("".join([xx.strip() for xx in p_list[max(i-window_size,0):i+window_size]])), x,i ) 
                            for i,x in enumerate(p_list) if i < N_p * region_ratio 
                             and len(x.strip()) > self.min_sentence_len ]
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
        return region
