blogstrap.py
==============

Author: [mox1](http://moxone.me)

blogstrap.py is a simple, no frills blog content management system, powered by Bootstrap and web.py
In its default configruation the full software stack consists of: 
* Bootstrap3 (http://getbootstrap.com/)
* web.py (http://webpy.org/)
* Peewee ORM (https://github.com/coleifer/peewee)
* sqlite (http://www.sqlite.org/)

blogstrap.py has been designed to be simple and "just work", if you experience problems please create an issue on github!

Blogstrap.py includes an awesome default theme written by [HackerThemes](http://www.hackerthemes.com). Any of HackerThemes "Tales" themes
will work by default with blogstrap.py.

Example
==============
[mox1's Blog](http://moxone.me) - A live real world example / demo of blogstrap.py

Setup / Initial Config
==============
    mkdir my_blog
    cd my_blog
    git clone https://github.com/mox1/webpy-bootstrap-blog .
    pip install -r requirements.txt
    vim config.py
    python ./app.py 
    
In your favorite browser navigate to localhost:8080/admin/admin

Usage
==============
Have a look at the [QuickStart guide](http://www.moxone.me/post?pid=2)


Running with apache / lighttpd / nginx
==============
While the usage instructions above will get you up and running with a quick site for production / real-world environemnts, 
you will probably want to run web.py under apache or lighttpd. Google "web.py + " your desired web server for instruction. 
For apache mod_wsgi see: http://webpy.org/cookbook/mod_wsgi-apache 
For lighttpd mod_fastcgi see: http://webpy.org/cookbook/fastcgi-lighttpd

Getting Involed
==============
It is my goal to eventually turn blogstrap.py into a fully functional, feature complete Blogging platform. But, I can't do all of that by myself!
Anyone wishing to get involed into the project should join the mailing list at [blogstrap-py@googlegroups.com](blogstrap-py@googlegroups.com)


Copyright
==============
Portions of this sofware Copyright 2014 by mox1. This software is made available to you through through the "GPLv3" license, unless otherwise noted.
See LICENSE.txt for a complete copy of the GPLv3 license.
