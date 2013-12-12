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
    r'/tags', 'Tags')

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
        flash("success", """Welcome! Application code lives in app.py,
        models in model.py, tests in test.py, and seed data in seed.py.""")

        return render.index("Home",m.Post.get_recent(4),None,None)

class ByCategory:
    def GET(self):
        data = web.input()
        cat= data.get("cat",None)
        subcat = data.get("subcat",None)
        print "By Category // %s // %s //" % (cat,subcat)
        
        #special selector for "By Tag" , which is a "custom" category
        #this is effectively a page refresh, but lets do it
        if (cat == "By Tag"):
            if (subcat == None):
                #use clicked on the "By Tag" link, not the tag itself
                #send them to the homepage
                return web.seeother(urls[0])
            posts = m.Post.by_tag(subcat)
            return render.index("Posts for tag %s" % subcat, posts, "By Tag",subcat)
        
        else:
            posts = m.Post.by_category(cat,subcat)
            return render.index("%s / %s" % (cat,subcat),posts,cat,subcat)
        
class Tags:
    def GET(self):
        data = web.input()
        tag = data.get("tag",None)
        if tag == None:
            flash("error","Sorry, no blog posts for tag %s" % tag)
            return web.seeother(urls[0]) 
        #drop down, we have a good tag
        posts = m.Post.by_tag(tag)
        return render.index("Posts for tag %s" % tag, posts, "By Tag",tag)
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
