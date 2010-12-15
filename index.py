#!/usr/bin/env python
# web interface to calibre's ebook-convert utility
# requires calibre

import os, pipes, shutil, urllib
import subprocess

# apache to have write perms to these
# base path
bdir = '/home/rupa/www/rupa.at/cnv/'
# base url
burl = 'http://cnv.rupa.at/'
# output dir name
odirname = 'books/'
# default type to convert to
default_type = '.mobi'

try:
    from mod_python import util
except:
    class Req(object):
        def write(self, str):
            print str

odir = '%s%s' % (bdir, odirname)
ourl = '%s%s' % (burl, odirname)

def norm_book_name(title, author):
    '''
    return lname,fname_mname-title
    '''
    title = title.strip()
    author = author.strip().split()
    lname = author.pop()
    if author:
        fname, mname = author[0], author[1:]
        nauth = '%s,%s' % (lname, fname)
        if mname:
            nauth = '%s_%s' % (nauth, '_'.join(mname))
    else:
        nauth = lname
    return '%s-%s' % (nauth.replace(' ', '_'), title.replace(' ', '_'))

def book_from_url(url, title, author):
    '''
    grab a book from a url and normalize its filename
    '''
    iname, iext = os.path.splitext(url)
    oname = norm_book_name(title, author)
    opath = '%s%s%s' % (odir, oname, iext)
    if os.path.exists(opath):
        return opath, { 'msg:' : 'file already retrieved' }
    f, h = urllib.urlretrieve(url, '%s%s%s' % (odir, oname, iext))
    return f, h

def convert(req, fl, ofl, title, author):
    def run(cmd):
        return subprocess.Popen(cmd, shell=True,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, close_fds=True)

    if not os.path.exists(fl):
        req.write('can\'t find %s' % (fl))
        return
    if os.path.exists(ofl):
        req.write('%s already exists' % (fl))
        return

    cmd = 'ebook-convert %s %s --authors="%s" --title="%s"' % (pipes.quote(fl),
                                                               pipes.quote(ofl),
                                                               author,
                                                               title)
    req.write('running: ' + cmd + '\n\n')
    p = run(cmd)
    req.write(p.stdout.read())
    req.write(p.stderr.read())
    req.write('\n\n')
    #cm2 = 'ebook-meta -a "%s" -t "%s" %s' % (author, title, pipes.quote(ofl))
    #req.write('running: ' + cm2 + '\n\n')
    #p = run(cm2)
    #req.write(p.stdout.read())
    #req.write(p.stderr.read())
    #req.write('\n\n')

def usage():
    return '''
    <pre>

    ?u=help

        Show this message.

    ?u=<b>BOOKURL</b>&to=<b>.EXT</b>&t=<b>TITLE</b>&a=<b>AUTHOR</b>

        Fetch a book from <b>BOOKURL</b>, and convert it to <b>.EXT</b>.
        Normalize the filename by <b>AUTHOR</b> and <b>TITLE</b>.

        BOOKURL - required. url to an ebook file.
        .EXT    - optional. defaults to %s
        TITLE   - required. Title of book.
        AUTHOR  - required, Author (expects FML. multiple authors not supported)

        Conversion requires a POST, but GET requests will be cause the form to
        be filled appropriately.

    ?s=<b>SEARCH</b>

        Only show books matching <b>SEARCH</b> string.
    </pre>
    ''' % default_type

def index(req):
    req.content_type = 'text/html; charset=utf-8'
    url = req.form.getfirst('u') or ''
    oext = req.form.getfirst('to') or default_type
    author = req.form.getfirst('a') or ''
    title = req.form.getfirst('t') or ''
    srch = req.form.getfirst('s') or ''

    req.write('''
        <head>
        <title>cnv.rupa.at</title>
        <style>
            a { text-decoration: none }
            a.p { color: blue }
            .b { font-size: 2em }
        </style>
        </head>
    ''')

    if url == 'help':
        req.write(usage())
        return

    if req.method == 'POST' and url and oext and author and title:
        req.write('<pre>')
        req.write('getting %s...\n' % url)
        iname, headers = book_from_url(url, title, author)
        oname = '%s%s%s' % (odir, norm_book_name(title, author), oext)

        for k,v in headers.items():
            req.write('%s: %s\n' % (k, v))

        convert(req, iname, oname, title, author)

        req.write('\n\n<a href="%s">done</a>' % (burl))
        req.write('</pre>')
    else:
        req.write('''
        <pre>
        <form method="post", action="/">
     u: <input value="%s" name="u" size=50>
    to: <input value="%s" name="to" size=10>
     t: <input value="%s" name="t" size=50>
     a: <input value="%s" name="a" size=50>
        <input type="submit" value="convert">
        </form>''' % (url, oext, title, author))
        fmt = '\n\t<a class="p" href="%s?u=%s%s">%s</a> <a href="%s%s">%s</a>'
        for i in os.listdir(odir):
            if os.path.isdir('%s%s' % (odir, i)):
                continue
            if srch and srch not in i:
                continue
            req.write(fmt % (burl, ourl, i,
                             #u'<span class="b">\u21D4</span>'.encode('utf-8'),
                             '[c]',
                             ourl, i, i))
        req.write('\n\t</pre>')

if __name__ == '__main__':
    req = Req()
    req.write('''
    this script intended to run under mod_python

        bdir: %s
        burl: %s
        odir: %s
        ourl: %s
default_type: %s
    ''' % (bdir, burl, odir, ourl, default_type))
    req.write(usage())
