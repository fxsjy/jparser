#!/bin/evn python
import urllib2
import json
import time
import traceback
import requests
from flask import Flask, request, render_template
from jparser import PageModel

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/parser", methods=["GET","POST"])
def parser():
    t1 = time.time()
    url = request.args.get('url')
    try:
        if url and url.strip() != "":
            url = url.strip()
            headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'}
            rsps = requests.get(url, headers = headers)
            try:
                page = rsps.content.decode('utf-8') 
            except:
                page = rsps.content.decode('gb18030','ignore')
        else:
            page = request.form.get("html_content")
        t2 = time.time()
        pm = PageModel(page, url)
        result = pm.extract()
        t3 = time.time()
    except:
        traceback.print_exc()
        return "download url failed"
    return render_template("result.html", data = result['content'], title = result['title'], json_s = json.dumps(result, indent = 4),
                           download_cost = t2 - t1, extract_cost = t3 - t2)
    
if __name__ == "__main__":
    app.run(host = "0.0.0.0", port = 8838, debug = True)


