#!/usr/bin/env python
# mod_python web interface to calibre's ebook-convert utility
# needs xvfb if :0.0 isn't up
# Xvfb :0 -ac

import os, pipes, re, shutil, time, urllib
import subprocess
import ConfigParser

try:
    from mod_python import util
except:
    class Req(object):
        def write(self, str):
            print str

def usage(home, default_type):
    return '''

<a class="t" href="%s">[back]</a>

?u=help

    Show this message.

?s=<b>SEARCH</b>

    Only show books matching <b>SEARCH</b> string.

?u=<b>BOOKURL</b>&to=<b>.EXT</b>&t=<b>TITLE</b>&a=<b>AUTHOR</b>

    Fetch a book from <b>BOOKURL</b>, and convert it to <b>.EXT</b>.
    Normalize the filename by <b>AUTHOR</b> and <b>TITLE</b>.

    BOOKURL - required. url to an ebook file.
    .EXT    - optional. defaults to %s. Value of NONE simply gets a local copy,
    TITLE   - required. Title of book.
    AUTHOR  - required, Author (expects FML. multiple authors not supported)

    Conversion requires a POST, but GET requests will be cause the form to
    be filled appropriately.

config:

    On first run, a config file is generated at %s.
    You may wish to edit this file.

    admins       - space separated list of users
    book_path    - filesystem path to book dir
    default_type - default to convert to. A value of NONE does not convert.
    book_url     - url of book dir

formats:

    see <a href="http://calibre-ebook.com/user_manual/cli/ebook-convert.html">http://calibre-ebook.com/user_manual/cli/ebook-convert.html</a>

    ''' % (home, default_type, '%s/config' % os.path.dirname(__file__))

class Conf(object):
    def __init__(self, c={}):
        self.msg = ''
        self.config = ConfigParser.RawConfigParser()
        configfile = '%s/config' % os.path.dirname(__file__)
        if os.path.exists(configfile):
            self.config.read(configfile)
        elif not c:
            return
        else:
            fh = open(configfile, 'wb')
            self.config.add_section('options')
            self.config.set('options', 'default_type', '.epub')
            self.config.set('options', 'book_path', c['path'] + 'books/')
            self.config.set('options', 'book_url', c['url'] + 'books/')
            self.config.set('options', 'admins', '')
            self.config.set('options', 'display', '')
            self.config.write(fh)
            fh.close()
            self.msg += 'created config file %s ...\n' % (configfile)
        self.default_type = self.config.get('options', 'default_type')
        self.odir = self.config.get('options', 'book_path')
        self.ourl = self.config.get('options', 'book_url')
        self.admins = self.config.get('options', 'admins')
        self.display = self.config.get('options', 'display')
        if self.admins:
            self.admins = self.admins.split(' ')
        if not os.path.exists(self.odir):
            self.msg += 'creating dir %s ...\n' % self.odir
            os.makedirs(self.odir, 0777)

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

class MyURLopener(urllib.FancyURLopener):
    def auth(self, user, passwd):
        self.user = user
        self.passwd = passwd
        return self
    def prompt_user_passwd(self, host, realm):
        return self.user, self.passwd

def from_url(url, odir, title, author):
    '''
    grab a book from a url and normalize its filename
    '''
    msg = ''
    iname, iext = os.path.splitext(url)
    oname = norm_book_name(title, author)
    opath = '%s%s%s' % (odir, oname, iext.lower())
    if os.path.exists(opath):
        return opath, { 'msg' : 'file %s already retrieved' % opath }

    old_file = False
    if os.path.exists('%s%s' % (odir, os.path.basename(url))):
        old_file = True

    f, h = urllib.urlretrieve(url, opath)
    h['msg'] = 'got file %s ...\n' % opath

    # delete old (poorly named) files if they are in the library
    if old_file:
        h['msg'] += 'deleting old file %s ...\n' %  os.path.basename(url)
        os.unlink('%s%s' % (odir, os.path.basename(url)))

    return f, h

def convert(req, fl, ofl, title, author, display):
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
    if display:
        display = 'DISPLAY=%s' % display

    cmd = '%s ebook-convert %s %s --authors="%s" --title="%s"' % (display,
                                                                  pipes.quote(fl),
                                                                  pipes.quote(ofl),
                                                                  author,
                                                                  title)
    req.write('running: ' + cmd + '\n\n')
    p = run(cmd)
    req.write(p.stdout.read())
    req.write(p.stderr.read())
    req.write('\n\n')

    cm2 = 'ebook-meta %s' % (pipes.quote(ofl))
    req.write('running: ' + cm2 + '\n\n')
    p = run(cm2)
    req.write(p.stdout.read())
    req.write(p.stderr.read())
    req.write('\n\n')

def index(req):

    home = 'http://%s%s' % (req.hostname, os.path.dirname(req.uri))
    if not home.endswith('/'):
        home += '/'
    conf = Conf({ 'path' : os.path.dirname(__file__) + '/', 'url' : home })

    req.content_type = 'text/html; charset=utf-8'
    url = req.form.getfirst('u') or ''
    oext = req.form.getfirst('to') or conf.default_type
    author = req.form.getfirst('a') or ''
    title = req.form.getfirst('t') or ''
    srch = req.form.getfirst('s') or ''

    if srch:
        match = re.compile(srch, re.I)

    req.write('''
        <head>
        <title>cnv</title>
        <style>
            body {
                white-space: pre;
                font-family: monospace;
            }
            a { text-decoration: none }
            a.c { color: blue }
            a.t { font-family: helvetica, arial }
        </style>
        </head>
    ''')

    if conf.msg:
        req.write('%s' % conf.msg)

    if (not conf.admins or req.user in conf.admins) and url == 'help':
        req.write(usage(home, conf.default_type))
        return

    if req.method == 'POST' and url and oext and author and title:
        if conf.admins and req.user not in conf.admins:
            req.write('\n\n<a href="%s">not allowed ...</a>' % (home))
            return
        req.write('getting %s...\n' % url)
        urllib._urlopener = MyURLopener().auth(req.user,
                                               req.get_basic_auth_pw())
        iname, headers = from_url(url, conf.odir, title, author)
        for k,v in headers.items():
            req.write('%s: %s\n' % (k, v))

        if oext.upper() != 'NONE':
            oname = '%s%s%s' % (conf.odir, norm_book_name(title, author), oext)
            convert(req, iname, oname, title, author, conf.display)
        req.write('\n\n<a href="%s">done</a>' % (home))
    else:
        if not conf.admins or req.user in conf.admins:
            req.write('<a class="t" href="?u=help">Hi, %s</a>' % req.user)
        req.write('''
        <form method="get", action="%s">
        <input value="%s" name="s" size=41> <input type="submit" value="search">
        </form>''' % (home, srch))
        if not conf.admins or req.user in conf.admins:
            req.write('''<form method="post", action="%s">
     u: <input value="%s" name="u" size=50>
     t: <input value="%s" name="t" size=50>
     a: <input value="%s" name="a" size=50>
    to: <input value="%s" name="to" size=10> <input type="submit" value="convert">
        </form>''' % (home, url, title, author, oext))

        if not conf.admins or req.user in conf.admins:
            fmt = '<a class="c" href="%s?u=%s%%s">[c]</a> ' % (home, conf.ourl)
        else:
            fmt = '<a id="%s"></a>'
        fmt = '\n%s<a class="t" title="%%s" href="%%s%%s">%%s</a>' % fmt

        files = []
        for file in os.listdir(conf.odir):
            stats = os.stat(conf.odir + file)
            files.append((time.localtime(stats[8]), file, stats[6]))

        for (dt, i, sz) in sorted(files, reverse=True):
            if i.startswith('.'):
                continue
            if os.path.isdir('%s%s' % (conf.odir, i)):
                continue
            if srch and not match.search(i):
                continue
            if len(i) > 65:
                s = '%s ...' % i[:65]
            else:
                s = i
            req.write(fmt % (urllib.quote(i),
                             '%sK' % (sz//1024),
                             conf.ourl,
                             urllib.quote(i),
                             s))

if __name__ == '__main__':
    req = Req()
    req.write('this script intended to run under mod_python.')
