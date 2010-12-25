##SUMMARY

    ebook manager for apache and mod_python.
    uses calibre's ebook-convert and ebook-meta tools.
    gank, normalize, convert, and download ebooks.

    Optimized for and tested with iphone and kindle.
    The idea is you can use it from a kindle or iphone or whatever,
    with just a web browser.

    gank:
        grabs books from urls
    normalize:
        makes filenames LNAME,FNAME_MNAME-TITLE.EXT
        sets author and title metadata if possible
    convert:
        convert to any format calibre supports
    download:
        all files are web-accesible

##INSTALLATION

    Install calibre. We use the ebook-convert and ebook-meta tools.

    clone cnv to a web-accessible folder with mod_python
    set to run .py files.

    make sure apache has write permissions to cnv folder

    Visit the directory in a browser, should see a message about
    a config file and a book dir being created.

    Adjust configuration.
        admins       - space separated list of users. if empty,
                       everyone is an admin.
        display      - explicitly set $DISPLAY. for use with xvfb
        book_path    - filesystem path to book dir
        default_type - default to convert to. A value of NONE does not convert.
        book_url     - url of book dir
        base_url     - url to the script

    make sure apache has write permissions to book_path

    Set up .htaccess authentication and/or mimetypes

    Optional:
        put a copy of [sorttable.js](http://www.kryogenix.org/code/browser/sorttable/) next to index.py to make the books sortable
        by alphabet.

##HTACCESS

    mimetypes for kindle to recognize these as downloadable:
        AddType application/x-mobipocket-ebook mobi
        AddType application/octet-stream azw prc

    basic authentication:
        AuthUserFile /path/to/.htpasswd
        AuthGroupFile /dev/null
        AuthName "cnv"
        AuthType Basic
        require valid-user

##USAGE

    Search:
        Only show files matching regex.

    Convert form:
         u: url to an ebook. Local or remote.
         t: title
         a: author (FML)
        to: format to convert to. NONE to keep current format

        See [calibre docs](http://calibre-ebook.com/user_manual/cli/ebook-convert.html)
        for supported formats:

        Grabs a local copy of the file, named according to title and author.
        Remove old local copy if name has changed.
        Create new file, named accordding to title, author, and file type.

    Books in library are shown most recently modified first.

    By default, anyone can add and convert files. Set up basic authentication
    to restrict users. Add specific users to config to further restrict
    add/convert rights.

##MISC

    some conversions fail without an X server running (grr)
        use Xvfb if :0.0 not available
        upstart job to keep Xvfb running?

##TODO

    better xvfb support
    config option for DISPLAY

##SCREENSHOTS

       Normal view:
       Books listed newest modified first.

   ![normal](https://github.com/rupa/cnv/raw/master/static/cnv-norm.png)

       Searching:
       With regexes.

   ![search](https://github.com/rupa/cnv/raw/master/static/cnv-search.png)

       Admin view:
       Admins can add and convert boooks
       Clicking [c] sets the form field to that book.

   ![admin](https://github.com/rupa/cnv/raw/master/static/cnv-admin.png)

       About to convert a book:

   ![convert](https://github.com/rupa/cnv/raw/master/static/cnv-conv1.png)

       Converting:
       See how it goes.

   ![convert](https://github.com/rupa/cnv/raw/master/static/cnv-conv2.png)
