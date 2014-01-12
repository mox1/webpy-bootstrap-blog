blogstrap.py
==============

Author: [mox1](http://moxone.me)

blogstrap.py is a simple, no frills blog system, powered by Bootstrap and web.py
In its default configruation the full software stack consists of: 
* Bootstrap3 (http://getbootstrap.com/)
* web.py (http://webpy.org/)
* Peewee ORM (https://github.com/coleifer/peewee)
* sqlite (http://www.sqlite.org/)


blogstrap.py has been designed to be simple and "just work", if you experience problems please create an issue on github!

Example
==============
[My Blog](http://moxone.me) - Consider this site a real world example / demo of blogstrap.py

While blogstrap.py is open-source, my blog does include a copyrighted bootstrap template, called [Tales](https://wrapbootstrap.com/theme/tales-responsive-blog-theme-WB034M8P5). 
Tales is not required, but you will notice the default blogstrap.py is different from the example above. Please don't steal this guys hard work! (I am not affiliated with him) 

Setup / Initial Config
==============
    mkdir my_blog
    cd my_blog
    git clone https://github.com/mox1/webpy-bootstrap-blog .
    pip install -r requirements.txt (or you can do this through apt/rpm etc.)
    (Optional) open config.py with your favorite editor and edit a few config settings
    python ./app.py 
    In your favorite browser navigate to localhost:8080/admin/admin
    Create A User
    Modify the Global Settings



Running with apache / lighttpd / nginx
====
While the Usage instruction above will get you up and running with a quick site (via CherryPi), for production / real-world environemnts, 
you will probably want to run web.py under apache or lighttpd. google "web.py + " your desired web server for instruction. 
For apache mod_wsgi see: http://webpy.org/cookbook/mod_wsgi-apache 
For lighttpd mod_fastcgi see: http://webpy.org/cookbook/fastcgi-lighttpd

Running the tests
====
There aren't any tests yet, eventually some will be here.
    python test.py


Copyright
==============
Portions of this sofware Copyright 2014 by mox1. This software is made available to you through through the "GPLv3" license, unless otherwise noted.
See LICENSE.txt for a complete copy of the GPLv3 license.
