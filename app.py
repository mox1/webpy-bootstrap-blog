from collections import defaultdict

import web
import datetime
import config
import model as m


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
    r'/search', 'Search')

app = web.application(urls, globals())


# Allow session to be reloadable in development mode.
if web.config.get('_session') is None:
    session = web.session.Session(app, web.session.DiskStore('sessions'),
                                  initializer={'flash': defaultdict(list)})

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
t_globals['dt_now'] = datetime.datetime.now



#FIX_ME: This will never update with new posts,
#Consider this a temporary solution during beta here
all_tags = m.Post.all_tags()
#just use top 5 most popular tags
t_globals['tags'] = all_tags[0:5]


class Index:
    def GET(self):
        data = web.input()
        #by default we show page 1
        #pages less than 1 show page 1
        #when we are one page 2, next = 3, prev = 1
        prev,next = calcprevnext(data)
        posts = m.Post.get_recent(page=next,max=10)
        return render.index("mox1's Blog",posts,None,None,"?n=%s" % (prev-1),"?n=%s" % (next+1))

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
            return render.index("Blog Posts for tag %s" % subcat, posts, "By Tag",subcat,"tags?tag=%s&n=%s" % (subcat,(prev-1)),"tags?tag=%s&n=%s" % (subcat,(next+1)))
        
        else:
            posts = m.Post.by_category(cat,subcat,page=next,max=10)
            return render.index("%s / %s" % (cat,subcat),posts,cat,subcat,
                                "bycategory?cat=%s&subcat=%s&n=%s" % (cat,subcat,(prev-1)),"bycategory?cat=%s&subcat=%s&n=%s" % (cat,subcat,(next+1)))
        
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
        return render.index("Blog Posts for tag %s" % tag, posts, "By Tag",tag,"tags?tag=%s&n=%s" % (tag,(prev-1)),"tags?tag=%s&n=%s" % (tag,(next+1)))

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
        #if we drop in here, qo query
        posts = m.Post.search(query)
        return render.index("Search results for %s" % query, posts, "Search Results",query)

class IndexFull:
    def GET(self):
        #return the newest post
        post = m.Post.nth_most_recent(1)
        return render.blogdetail(post,render.comments())

class BlogPost:
    def GET(self):
        pid = -1
        try:
            pid = web.input().pid
        except:
            flash("error", "Sorry, that post doesn't exist!")
            return web.seeother("/")
        post = m.Post.by_id(pid)
        count,comments = m.Comment.get_comments(post.id)
        return render.blogdetail(post,render.comments(count,comments))
        
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

        return web.seeother("/")
    
class Credits:
    def GET(self):
        return render.credits(render.makecredits(m.Credit.get_all()))    
    
class AddComment:
    def GET(self):
        data = web.input()
        
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
