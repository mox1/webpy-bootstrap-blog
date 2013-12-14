blogstrap.py
==============

blogstrap.py is a simple, no frills blog system, powered by Bootstrap and web.py
In its default configruation the full software stack consists of: 
* Bootstrap3 (http://getbootstrap.com/)
* jQuery (http://jquery.com/)
* web.py (http://webpy.org/)
* Peewee ORM (https://github.com/coleifer/peewee)
* sqlite (http://www.sqlite.org/)


blogstrap.py has been designed 

Example
==============
[My Blog](http://moxone.me) - Consider this site a real world example / demo of blogstrap.py

While blogstrap.py is open-source, my blog does include a copyrighted bootstrap template, called [Tales](https://wrapbootstrap.com/theme/tales-responsive-blog-theme-WB034M8P5)
Tales is not required, but you will notice the default blogstrap.py is different from the example above. Please don't steal this guys hard work! 

Usage
==============
    mkdir my_blog
    cd my_blog
    git clone https://github.com/mox1/webpy-bootstrap-blog .
    python ./app.py 
    In your favorite browser navigate to localhost:8080 and finish the installation

The first person to browse the root of app.py will be the one configuring the site. Do not forget this setup (especially if performing the setup on a web-server) or you will have a somewhat vulnerable page available for anyone to mess with. 
 
   

Initial Configuration
==============
    pip install -r requirements.txt

Running with apache
====
While the Usage instruction above will get you up and running with a quick site, for production / real-world environemnts, 
you will probably want to run web.py under apache or lighttpd. google "web.py + " your desired web server for instruction. 
For apache mod_wsgi see: http://webpy.org/cookbook/mod_wsgi-apache 

Running the tests
====
There aren't any tests yet, eventually some will be here.
    python test.py

