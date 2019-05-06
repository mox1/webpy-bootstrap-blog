#!/usr/bin/env python

#err under Apache this is going to cause some issues 
#because Apache does add "." to path
import os,sys
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0,CURRENT_DIR)
import config
import logging
logger = logging.getLogger("blogstrap")
logger.info("Starting blogstrap.py")
logger.debug("app.py DEBUG messages enabled!")

from dolog import LoggerWriter
#redirect stderr to stdout and the logger created above
sys.stderr = LoggerWriter(logger)

from collections import defaultdict
from datetime import datetime
import time
import threading
import web
from web import websafe
import datetime
import model as m
import hashlib
import xml.etree.ElementTree as ET
from string import Template

VERSION = "0.9.8-BETA"

logger.info("You are running version %s" % VERSION)

#if you change urls, make sure urls[0]  is your homepage!!
urls = (
    r"/", "Index",
    r"/sitemap.xml","SiteMap",
    r"/robots.txt","Robots",
    r"/newest", "IndexFull",
    r"/post", "BlogPost",
    r"/about", "About",
    r"/credits","Credits",
    r"/bycategory","ByCategory",
    r"/newcomment","AddComment",
    r"/contactme", "ContactMe",
    r"/tags", "Tags",
    r"/search", "Search",
    r"/admin/preview", "Preview",
    r"/admin/(.*)","Admin")

app = web.application(urls, globals())

def my_loadhook():
    #logger.debug("Connecting to db")
    try:
        m.db.connect()
    except Exception:
        pass

def my_unloadhook():
    #logger.debug("Closing db")
    m.db.close()

app.add_processor(web.loadhook(my_loadhook))
app.add_processor(web.unloadhook(my_unloadhook))

sinit = {
        "flash"     : defaultdict(list),
        "logged_in" : False,
        "vcount"    : 0,
        }

# Allow session to be reloadable in development mode.
if web.config.get("_session") is None:
    session = web.session.Session(app, web.session.DiskStore("%s/sessions" % CURRENT_DIR),
                                  initializer=sinit)

    web.config._session = session
else:
    session = web.config._session


b_data = m.BlogData.get(update=True)
def blog_data(update = False):
    global b_data
    if update == False:
        return b_data
    else:
        b_data = m.BlogData.get(update=True)
        return b_data


def update_db():
    global t_globals
    logger.info("Start updating blog data")
    m.BlogData.update_stats()
    blog_data(update=True)
    logger.info("Finish updating blog data")
    
    
#this function allows us to do periodic things
#not perfect, but eh. 
#for now this simply updates the statistics
#but could easily be used to do more "cron" like things
#this gets called for EVERY page, so don't do any heavy lifting
next_cron_run = 0
def my_processor(handler): 
    global next_cron_run
    if (time.time() > next_cron_run):
        #logger.debug("DOING CRON RUN")
        thr = threading.Thread(target=update_db)
        thr.start()
        next_cron_run = time.time() + config.STAT_UPDATES 
    
    return handler()

app.add_processor(my_processor)

def flash(group, message):
    session.flash[group].append(message)


def flash_messages(group=None):
    if not hasattr(web.ctx, "flash"):
        web.ctx.flash = session.flash
        session.flash = defaultdict(list)
    if group:
        return web.ctx.flash.get(group, [])
    else:
        return web.ctx.flash

def csrf_token():
    if not session.has_key('csrf_token'):
        from uuid import uuid4
        session.csrf_token=uuid4().hex
    return session.csrf_token

def csrf_protected(f):
    def decorated(*args,**kwargs):
        inp = web.input()
        if not (inp.has_key('csrf_token') and inp.csrf_token==session.pop('csrf_token',None)):
            logger.error("CSRF Detected!!!: ip=%s" % web.ctx.ip )
            raise web.HTTPError(
                "400 Bad request",
                {'content-type':'text/html'},
                """Cross-site request forgery (CSRF) attempt (or stale browser form). 
                <a href="">Back to the form</a>.""") 
        return f(*args,**kwargs)
    return decorated

#lets check if out database tables exist, if not create them
for x in [m.User,m.Post,m.Image,m.Comment,m.BlogData]:
 #this will fail silently if they already exist
 x.create_table(True)


render = web.template.render("%s/templates/" % CURRENT_DIR,
                             #base="base",
                             cache=config.cache)
t_globals = web.template.Template.globals
t_globals["datestr"] = web.datestr
t_globals["app_version"] = lambda: VERSION + " - " + config.env
t_globals["flash_messages"] = flash_messages
t_globals["render"] = lambda t, *args: render._template(t)(*args)
t_globals["get_recent_posts"] = m.Post.get_recent
t_globals["pretty_date"] = m.print_dates
t_globals["fav_posts"] = m.Post.get_favs
t_globals["next_posts"] = m.Post.get_next
t_globals["recent_posts"] = m.Post.recent_posts
t_globals["popular_posts"] = m.Post.most_popular
t_globals["dt_now"] = datetime.datetime.now
t_globals["dt_as_str"] = m.datetime_str
t_globals["dt_as_ago"] = m.datetime_ago
t_globals["hashlib"] = hashlib
t_globals["csrf_token"] = csrf_token
t_globals["max_comment"] = config.MAX_COMMENT

#get statistics
#This is now updated in the Admin class, method globalsettings
#And in the my_processor function above 
t_globals["blog_data"] = blog_data
print "Admin page currently set to: /admin/%s" % blog_data().adminurl
logger.info("Admin page currently set to: /admin/%s" % blog_data().adminurl)


#Dynamically Generated robots.txt
#By Default allows all , except for /admin/
robot_template = Template("""#Generated by blogstrap.py
User-agent: * 
Disallow: /admin/
Sitemap: $sitemap
""")
class Robots:
    def GET(self):
        sitemap_url = "%s/sitemap.xml" % web.ctx.home
        web.header("Content-Type", "text/plain")
        return robot_template.substitute(sitemap=sitemap_url) 

#Dynamically Generated sitemap.xml 
#By default simply includes links to all blog posts that are public
class SiteMap:
    def GET(self):
        host = web.ctx.home
        #print web.ctx
        #1st get all public posts
        posts = m.Post.all()
        #generate opening xml
        urlset = ET.Element("urlset",xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
        #add root
        url = ET.SubElement(urlset,"url")
        loc = ET.SubElement(url,"loc")
        loc.text = "%s/" % host
        lastmod = ET.SubElement(url,"lastmod")
        lastmod.text = datetime.datetime.now().strftime("%Y-%m-%d")
        changefreq = ET.SubElement(url,"changefreq")
        changefreq.text = "daily"
        priority = ET.SubElement(url,"priority")
        priority.text = "0.8"
        
        for post in posts:
            url = ET.SubElement(urlset,"url")
            loc = ET.SubElement(url,"loc")
            loc.text = "%s/post?pid=%d" % (host,post.id)
            lastmod = ET.SubElement(url,"lastmod")
            lastmod.text = post.updated.strftime("%Y-%m-%d")
            changefreq = ET.SubElement(url,"changefreq")
            changefreq.text = "yearly"
        
        #ok return xml
        web.header("Content-Type", "text/xml; charset=utf-8")
        return ET.tostring(urlset, encoding="utf-8", method="xml")
        
        


#This is the main Admin handler class. All admin functions are executed through POST's
#utilizing a method=XXX variable passed by an ajax call, a form, etc.

#url is used here as a bit of security through obsecurity
#it just prevents dumb attackers from searching google for our admin urls,
#launching internet wide script attacks ,etc.
class Admin:
    def GET(self,url):
        #compare url vs our BlogData valid url
        if url == "logout":
                session.logged_in = False
                session.kill()
                flash("success","Session Data removed!")
                return web.seeother(urls[0])
        elif url != blog_data().adminurl:
            #nope go away, send em to the home page
            #logger.warn("Bad Adminurl (needed %s, got %s)" % (t_globals["blog_data"].adminurl,url))
            return web.seeother(urls[0])
        
        #ok they found the magic url, good
        if session.logged_in == False:
            if m.User.is_setup() == False:
                #we have 0 users, ask to add a new one
                return render.fullpageindex("Please Create a user",render.createuser(),"")
            else:
                #show login page
                return render.fullpageindex("Please Login to Continue",render.login(),"")
        else:
            images = m.Image.get_all(private=True)
            return render.fullpageindex("Logged in as %s" % session.dispname,render.admin(images),render.bottom_admin())
                
    def POST(self,url):
        global t_globals
        #compare url vs our BlogData valid url
        if url != blog_data().adminurl:
            #nope go away, send em to the home page
            logger.warn("Bad Adminurl (needed %s, got %s)" % (t_globals["blog_data"].adminurl,url))
            return web.seeother(urls[0])
        
        admin_url = "/admin/%s" % blog_data().adminurl
        #ok they found the magic url, good
        data = web.input(nifile={})
        method = data.get("method","malformed")
        if session.logged_in == False:
            #the only thing you can do here is try to login or create a user
            if method =="login":
                (resl,msg) = m.User.attempt_auth(data.email,data.password)
                if resl != None:
                    set_auth(resl)
                    return web.seeother(admin_url)
                else:
                    flash("error",msg)
                    return web.seeother(admin_url)
            elif method == "createuser" and m.User.is_setup() == False:
                #only allow this method for user 1, or anyone can crete an account!
                (resl,msg) = m.User.new_from_input(data)
                if resl != None:
                    flash("success",msg)
                    set_auth(resl)
                else:
                    flash("error",msg)
                return web.seeother(admin_url)
            else:
                flash("error","Please login first")
                return web.seeother(admin_url)
        else:   
            #if we drop down here session says we are logged in
            if method == "malformed":
                flash("error","Unknown admin method!")
                return web.seeother(admin_url)
            elif method == "login":
                (resl,msg) = m.User.attempt_auth(data.email,data.password)
                if resl != None:
                    set_auth(resl)
                else:
                    flash("error",msg)
                return web.seeother(admin_url)
            elif method == "newpost":
                (resl,msg) = m.Post.new_from_input(data,session.uid)
                if resl != None:
                    flash("success","Succes, blog entry saved! (id = %s)" % resl.id)
                else:
                    flash("error",msg)
                return web.seeother(admin_url)
            elif method == "newimage":
                (resl,msg) = m.Image.new_from_input(data)
                if resl!= None:
                    flash("success",msg)
                else:
                    flash("error",msg)
                return web.seeother(admin_url)
            elif method == "globalsettings":
                (resl,msg) = m.BlogData.update_info_from_input(data)
                #always update blog_data, even in error cases
                blog_data(update=True)
                if resl != None:
                    flash("success",msg)
                else:
                    flash("error",msg)
                #adminurl can change from the BlogData.update call above
                admin_url = "/admin/%s" % blog_data().adminurl
                return web.seeother(admin_url)
            elif method == "getallposts":
                resl = m.Post.all(evenprivate=True)
                return render.datatable_posts(resl)
            elif method == "getallimages":
                images = m.Image.get_all(private=True)
                return render.datatable_images(images)
            elif method == "getcomments":
                id = data.get("id","-1")
                (count,comments) = m.Comment.get_comments(id,True)
                return render.datatable_comments(count,comments)
            elif method == "getsinglepost":
                id = data.get("id","-1")
                resl = m.Post.get(m.Post.id==id)
                images = m.Image.get_all(private=True)
                return render.adminsinglepost(resl,images)
            elif method == "getsingleimage":
                id = data.get("id","-1")
                resl = m.Image.by_id(id)
                return render.adminsingleimage(resl)
            elif method == "getsinglecomment":
                id = data.get("id","-1")
                resl = m.Comment.by_id(id)
                return render.adminsinglecomment(resl)
            elif method == "getuserdata":
                return render.adminuser(m.User.firstuser())
            elif method == "editpost":
                (resl,msg) = m.Post.update_from_input(data,session.uid)
                if resl != None:
                    flash("success","Succes, blog entry updated! (id = %s)" % resl.id)
                else:
                    flash("error",msg)
                return web.seeother(admin_url)             
            elif method == "editimage":
                (resl,msg) = m.Image.update_from_input(data)
                if resl != None:
                    flash("success","Succes, image updated! (id = %s)" % resl.id)
                else:
                    flash("error",msg)
                return web.seeother(admin_url)
            elif method == "deletecomment":
                id = data.get("id","-1")
                msg = m.Comment.remove(id)
                return msg
            elif method == "editcomment":
                msg = m.Comment.update_from_input(data)
                return msg
            elif method == "edituser":
                (resl,msg) = m.User.update_from_input(data)
                blog_data(update=True)
                if resl != None:
                    flash("success","Succes, user %s updated!" % resl.name)
                else:
                    flash("error",msg)
                return web.seeother(admin_url)
            else:
                flash("error","Unkown method: %s" % method)
                return web.seeother(admin_url)

        
class Index:
    def GET(self):
        data = web.input()
        #by default we show page 1
        #pages less than 1 show page 1
        #when we are one page 2, next = 3, prev = 1
        prev,next = calcprevnext(data)
        posts = m.Post.get_recent(page=next,max=10)
        content = render.blog_teasers(posts,"?n=%s" % (prev-1),"?n=%s" % (next+1))
        return render.index(blog_data().title,content,None,None)

class ByCategory:
    def GET(self):
        data = web.input()
        cat= websafe(data.get("cat",""))
        subcat = websafe(data.get("subcat",""))
        
        prev,next = calcprevnext(data)
        #special selector for "By Tag" , which is a "custom" category
        #this is effectively a page refresh, but lets do it
        if (cat == "By Tag"):
            if (subcat == None):
                #user clicked on the "By Tag" link, not the tag itself
                #send them to the homepage
                return web.seeother(urls[0])
            posts = m.Post.by_tag(subcat,page=next,max=10)
            content = render.blog_teasers(posts,"tags?tag=%s&n=%s" % (subcat,(prev-1)),
                                                "tags?tag=%s&n=%s" % (subcat,(next+1)))
            return render.index("Blog Posts for tag %s" % subcat, content, "By Tag",subcat)
        
        else:
            posts = m.Post.by_category(cat,subcat,page=next,max=10)
            content = render.blog_teasers(posts,"bycategory?cat=%s&subcat=%s&n=%s" % (cat,subcat,(prev-1)),
                                                "bycategory?cat=%s&subcat=%s&n=%s" % (cat,subcat,(next+1)))
            return render.index("%s / %s" % (cat,subcat),content,cat,subcat)
        
class Tags:
    def GET(self):
        data = web.input()
        tag = websafe(data.get("tag",None))
        if tag == None:
            flash("error","Sorry, no blog posts for tag %s" % tag)
            return web.seeother(urls[0])
        prev,next = calcprevnext(data) 
        #if we drop down here, we have a good tag
        posts = m.Post.by_tag(tag,page=next,max=10)
        content = render.blog_teasers(posts,"tags?tag=%s&n=%s" % (tag,(prev-1)),
                                            "tags?tag=%s&n=%s" % (tag,(next+1)))
        
        return render.index("Blog Posts for tag %s" % tag, content, "By Tag",tag)

class Search:
    def GET(self):
        data = web.input()
        if "q" not in data:
            flash("error","Search Error, query empty...")
            return web.seeother(urls[0])
        query = websafe(data["q"])
        #short querys are a heachache, lets avoid them
        if len(query) < 3:
            flash("error","Search string \"%s\" is too short." % query)
            return web.seeother(urls[0])
        prev,next = calcprevnext(data)
        #if we drop in here, qo query
        posts = m.Post.search(query,page=next,max=10)
        content = render.blog_teasers(posts,"search?q=%s&n=%s" % (query,(prev-1)),
                                            "search?q=%s&n=%s" % (query,(next+1)))
        return render.index("Search results for \"%s\"" % query, content, "Search Results","\"%s\""% query)

class IndexFull:
    def GET(self):
        #return the newest post
        post = m.Post.nth_most_recent(1)
        if post == None:
            return web.seeother(urls[0])
        
        count,comments = m.Comment.get_comments(post.id,False)
        #for next and prev links
        try:
            next = m.Post.get_next(post.created_at,1).get()
        except:
            next = None
        try:
            prev = m.Post.get_prev(post.created_at,1).get()
        except:
            prev = None
            
        return render.blogdetail(post,count,comments,next,prev,session.logged_in)


class Preview:
    def POST(self):
        if session.logged_in == False:
            logger.info("Attempt to get preview page while not logged in!?")
            return web.notfound()
        else:
            data = web.input(nifile={})
            (resl,msg) = m.Post.update_from_input(data,session.uid)
            if resl == None:
                flash("There was a problem previewing: %s" % msg)
                return web.seeother(urls[0])
            
            post = resl
            flash("success","Below is a preview of your posting. To save this switch to the other tab and click \"Update Post\"")
            count,comments = m.Comment.get_comments(post.id,False)
            #for next and prev links
            try:
                next = m.Post.get_next(post.created_at,1).get()
            except:
                next = None
            try:
                prev = m.Post.get_prev(post.created_at,1).get()
            except:
                prev = None
                
            return render.blogdetail(post,count,comments,next,prev,session.logged_in)
            
            
class BlogPost:
    def GET(self):
        pid = -1
        try:
            pid = websafe(web.input().pid)
            post = m.Post.by_id(pid)
            if post == None:
                raise Exception
        except:
            flash("error", "Sorry, that post doesn't exist!")
            return web.seeother(urls[0])

        #for next and prev links
        try:
            next = m.Post.get_next(post.created_at,1).get()
        except:
            next = None
        try:
            prev = m.Post.get_prev(post.created_at,1).get()
        except:
            prev = None
            
        count,comments = m.Comment.get_comments(post.id,False)
        return render.blogdetail(post,count,comments,next,prev,session.logged_in)
class About:
    def GET(self):
        #TODO: Eventually if we support multple users, fix this
        user = m.User.by_id(1)
        return render.about(user)
    
class ContactMe:
    @csrf_protected # Verify this is not CSRF, or fail
    def POST(self):
        data = web.input()
        try:
            if (websafe(data.get("email","")) != "n0m0r3sp4m@n0p3.0rg"):
                #failure, return him to homepage with a flash msg
                flash("error","Sorry, you failed the spam test, post not accepted. Turn on javascript.")
                return web.seeother(urls[0])
            else:
                web.sendmail(websafe(data.cemail), m.User.by_id(1).email, "Blog About Page Contact from: %s" % websafe(data.name), websafe(data.message))
                flash("success","Thanks for Contacting me!")
        except Exception,e:
            flash("error","Sorry, there was a problem, message not sent")

        return web.seeother(urls[0])
    
class Credits:
    def GET(self):
        return render.fullpageindex("Credits and Attribution",render.makecredits(m.Image.get_all()),"")    




#TODO, maybe at some point AJAXify this
#so we can post a comment without a page load
class AddComment:
    def GET(self):
        return web.seeother(urls[0])

    @csrf_protected # Verify this is not CSRF, or fail
    def POST(self):
        data = web.input()
        ip = web.ctx.ip
        #verify our uber anti-spam technique 
        #(that the user has javascript turned on :) )
        if (websafe(data.get("email","")) != "n0m0r3sp4m@n0p3.0rg"):
            #failure, return him to homepage with a flash msg
            flash("error","Sorry, you failed the spam test, post not accepted. Turn on javascript.")
            logger.warn("New comment SPAM test failed by %s" % ip) 
            return web.seeother(urls[0])
        
        postid = websafe(int(data.get("pid","-1")))
        text = websafe(data.get("message",None))
        if text == None or len(text) < 1:
            flash("error","Please add some text to that comment!")
            #TODO: can we use web.py to get the url referrer and send them back there?
            return web.seeother("post?pid=%s" % postid)
        if len(text) > config.MAX_COMMENT:
            flash("error","Comment length of %d too large, max %d characters" % (len(text),config.MAX_COMMENT))
            return web.seeother("post?pid=%s" % postid)
        
        
        #spam check passed, continue
        postid = int(websafe(data.get("pid",-1)))
        parentid = int(websafe(data.get("replyto",-1)))
        title = websafe(data.get("title","Comment"))
        if session.logged_in == False:
            author = websafe(data.get("name","Anonymous"))
            email = websafe(data.get("e","none@none.net"))
        else:
            user = m.User.by_id(session.uid)
            author = user.name
            email = user.email
        c1 = m.Comment.new(postid,parentid,title,author,text,email,session.logged_in,ip,web.sendmail)
        if c1 != None:
            flash("success","Thanks for joining the discussion!")
        else:
            flash("error","There was an error with your comment")
        return web.seeother("post?pid=%d" % postid)
    
def set_auth(user):
    #set session info
    session.logged_in = True
    session.uid = user.id
    session.username = user.email
    session.dispname = user.name

    
#we can use next as the input to DB pagination queries
#so we cant decrement by 1 in this function
def calcprevnext(data):
        try:
            next = int(websafe(data.get("n","1")))
        except:
            next = 1
        if next == 1:
            prev = 2
        else: 
            prev = next
        return (prev,next)
# Set a custom internal error message
def internalerror():
    logger.error("Internal error:",exc_info=True)
    msg = """
    We're sorry, an internal error occurred has. Please try your request again by
    hitting back on your web browser. You can also <a href="/"> go back
     to the main page.</a>
    """
    return web.internalerror(msg)

def notfound():
    #logger.error("404 Not found error has occurred")
    #return the homepage with not found
    
    return web.notfound(render.fullpageindex("404 Error Not Found","<p>404 Error: The page you have requested was not found!</p>",""))
 
#add our 404 handler
app.notfound = notfound 
   
# Setup the application's error handler
app.internalerror = web.debugerror if web.config.debug else internalerror

if config.EMAIL_ERRORS and config.email_errors.to_address:
    app.internalerror = web.emailerrors(config.email_errors.to_address,
                                        app.internalerror,
                                        config.email_errors.from_address)


# Adds a wsgi callable for uwsgi
application = app.wsgifunc()
if __name__ == "__main__":
    app.run()
