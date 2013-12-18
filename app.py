from collections import defaultdict

import web
import datetime
import config
import model as m
import hashlib

VERSION = "0.0.1"

#if you change urls, make sure url[0]  is your homepage / index.!!
urls = (
    r'/', 'Index',
    r'/newest', 'IndexFull',
    r'/post', 'BlogPost',
    r'/about', 'About',
    r'/credits','Credits',
    r'/bycategory',"ByCategory",
    r'/newcomment',"AddComment",
    r'/contactme', 'ContactMe',
    r'/tags', 'Tags',
    r'/search', 'Search',
    r'/admin','Admin')

app = web.application(urls, globals())

sinit = {
        'flash'     : defaultdict(list),
        'logged_in' : False,
        'vcount'    : 0,
        }

# Allow session to be reloadable in development mode.
if web.config.get('_session') is None:
    session = web.session.Session(app, web.session.DiskStore('sessions'),
                                  initializer=sinit)

    web.config._session = session
else:
    session = web.config._session


def flash(group, message):
    session.flash[group].append(message)


def flash_messages(group=None):
    if not hasattr(web.ctx, 'flash'):
        web.ctx.flash = session.flash
        session.flash = defaultdict(list)
    if group:
        return web.ctx.flash.get(group, [])
    else:
        return web.ctx.flash

render = web.template.render('templates/',
                             #base='base',
                             cache=config.cache)
t_globals = web.template.Template.globals
t_globals['datestr'] = web.datestr
t_globals['app_version'] = lambda: VERSION + ' - ' + config.env
t_globals['flash_messages'] = flash_messages
t_globals['render'] = lambda t, *args: render._template(t)(*args)
t_globals['get_recent_posts'] = m.Post.get_recent
t_globals['pretty_date'] = m.print_dates
t_globals['fav_posts'] = m.Post.get_favs
t_globals['next_posts'] = m.Post.get_next
t_globals['recent_posts'] = m.Post.recent_posts
t_globals['popular_posts'] = m.Post.most_popular
t_globals['dt_now'] = datetime.datetime.now
t_globals['hashlib'] = hashlib


#get statistics

#TODO: Update this under certain conditions
#like when a new post / comment is created
t_globals['blog_data'] = m.BlogData.get(update = True)


class Admin:
    def POST(self):
        data = web.input()
        print data
    def GET(self):
        if session.logged_in == False:
            #show login page
            return render.fullpageindex("Please Login to Continue",render.login())
        else:
            return render.fullpageindex("Admin Interface",render.admin())
class Index:
    def GET(self):

        data = web.input()
        #by default we show page 1
        #pages less than 1 show page 1
        #when we are one page 2, next = 3, prev = 1
        prev,next = calcprevnext(data)
        posts = m.Post.get_recent(page=next,max=10)
        content = render.blog_teasers(posts,"?n=%s" % (prev-1),"?n=%s" % (next+1))
        return render.index("mox1's Blog",content,None,None)

class ByCategory:
    def GET(self):
        data = web.input()
        cat= data.get("cat","")
        subcat = data.get("subcat","")
        print "By Category // %s // %s //" % (cat,subcat)
        
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
        tag = data.get("tag",None)
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
        query = data['q']
        #short querys are a heachache, lets avoid them
        if len(query) < 3:
            flash("error","Search string \"%s\" is too short." % q)
            return web.seeother(ursl[0])
        prev,next = calcprevnext(data)
        #if we drop in here, qo query
        posts = m.Post.search(query,page=next,max=10)
        content = render.blog_teasers(posts,"search?q=%s&n=%s" % (query,(prev-1)),
                                            "search?q=%s&n=%s" % (query,(next+1)))
        return render.index("Search results for %s" % query, content, "Search Results",query)

class IndexFull:
    def GET(self):
        #return the newest post
        post = m.Post.nth_most_recent(1)
        count,comments = m.Comment.get_comments(post.id)
        #for next and prev links
        try:
            next = m.Post.get_next(post.created_at,1).get()
        except:
            print "Ahhh error on next!"
            next = None
        try:
            prev = m.Post.get_prev(post.created_at,1).get()
        except:
            print "Add error prev!!!!"
            prev = None
            
        return render.blogdetail(post,count,comments,next,prev)

class BlogPost:
    def GET(self):
        pid = -1
        try:
            pid = web.input().pid
        except:
            flash("error", "Sorry, that post doesn't exist!")
            return web.seeother("/")
        post = m.Post.by_id(pid)
        #for next and prev links
        try:
            next = m.Post.get_next(post.created_at,1).get()
        except:
            print "Ahhh error on next!"
            next = None
        try:
            prev = m.Post.get_prev(post.created_at,1).get()
        except:
            print "Add error prev!!!!"
            prev = None
            
        count,comments = m.Comment.get_comments(post.id)
        return render.blogdetail(post,count,comments,next,prev)
class About:
    def GET(self):
        return render.about(m.User.by_id(1))
    
class ContactMe:
    def POST(self):
        data = web.input()
        print data
        try:
            web.sendmail(data.email, m.User.by_id(1).email, "Blog About Page Contact from: %s" % data.name, data.message)
            flash("error","Thanks for Contacting me!")
        except Exception,e:
            flash("error","Sorry, there was a problem, message not sent")

        return web.seeother(url[0])
    
class Credits:
    def GET(self):
        return render.fullpageindex("Credits and Attribution",render.makecredits(m.Credit.get_all()))    




#TODO, maybe at some point AJAXify this
#so we can post a comment without a page load
class AddComment:
    def GET(self):
        return web.seeother(urls[0])
     
    def POST(self):
        data = web.input()
        print data
        #verify our uber anti-spam technique 
        #(that the user has javascript turned on :) )
        if (data.get("email","") != "n0m0r3sp4m@n0p3.0rg"):
            #failure, return him to homepage with a flash msg
            flash("error","Sorry, you failed the spam test, post not accepted")
            return web.seeother(url[0])
        
        postid = int(data.get("pid",-1))
        text = data.get("message",None)
        if text == None:
            flash("error","Please add some text to that comment!")
            #TODO: can we use web.py to get the url referrer and send them back there?
            return web.seeother('post?pid=%d' % postid)
        #spam check passed, continue
        postid = int(data.get("pid",-1))
        parentid = int(data.get("replyto",-1))
        title = data.get("title","Comment")
        author = data.get("name","Anonymous")
        email = data.get("e","none@none.net")
        c1 = m.Comment.new(postid,parentid,title,author,text,email)
        flash("success","Thanks for joining the discussion!" )
        return web.seeother('post?pid=%d' % postid)
    
    
    
def set_auth(user):
    #set session info
    session.logged_in = True
    session.user = user
    session.username = user.username
    session.dispname = user.displayname

    

#we can use next as the input to DB pagination queries
#so we cant decrement by 1 in this function
def calcprevnext(data):
        try:
            next = int(data.get("n","1"))
        except:
            next = 1
        if next == 1:
            prev = 2
        else: 
            prev = next
        return (prev,next)
# Set a custom internal error message
def internalerror():
    msg = """
    An internal server error occurred. Please try your request again by
    hitting back on your web browser. You can also <a href="/"> go back
     to the main page.</a>
    """
    return web.internalerror(msg)


# Setup the application's error handler
app.internalerror = web.debugerror if web.config.debug else internalerror

if config.email_errors.to_address:
    app.internalerror = web.emailerrors(config.email_errors.to_address,
                                        app.internalerror,
                                        config.email_errors.from_address)




# Adds a wsgi callable for uwsgi
application = app.wsgifunc()
if __name__ == "__main__":
    app.run()
