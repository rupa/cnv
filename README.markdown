##SUMMARY

    ebook manager for apache and mod_python.
    uses calibre's ebook-convert and ebook-meta tools.
    gank, normalize, convert, and download ebooks.

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

    make sure apache has write permissions to book_path

    Set up .htaccess authentication and/or mimetypes

##HTACCESS

    mimetypes for kindle downloading:
        AddType application/x-mobipocket-ebook mobi
        AddType application/octet-stream azw prc

    basic authentication:
        AuthUserFile /path/to/.htpasswd
        AuthGroupFile /dev/null
        AuthName "cnv"
        AuthType Basic
        require valid-user

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
