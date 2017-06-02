# coding=utf-8
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='jparser',
    author="Sun, Junyi",
    version='0.0.20',
    license='MIT',

    packages=["jparser"],

    description="A robust parser which can extract title, content, images from html pages",
    long_description='''
Usage Example:
^^^^^^^^^^^^^^^^^^^^^
::

    import urllib2
    from jparser import PageModel
    html = urllib2.urlopen("http://news.sohu.com/20170512/n492734045.shtml").read().decode('gb18030')
    pm = PageModel(html)
    result = pm.extract()
    
    print "==title=="
    print result['title']
    print "==content=="
    for x in result['content']:
        if x['type'] == 'text':
            print x['data']
        if x['type'] == 'image':
            print "[IMAGE]", x['data']['src']
    
''',
    install_requires=[
        "lxml >= 3.7.1",
    ]
)