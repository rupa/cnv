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

    drop index.py in a web-accessible folder with mod_python
    set to run .py files, and write permissions for apache.

    Visit the directory in a browser, should see a message about
    a config file being created.

    Adjust configuration.

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
        see upstart job at static/xvfb.conf

##TODO

    better xvfb support
    config option for DISPLAY
