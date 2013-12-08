from collections import defaultdict

import web

import config
import model as m


VERSION = "0.0.1"

urls = (
    r'/', 'Index',
    r'/post', 'BlogPost')

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


class Index:
    def GET(self):
        #flash("success", """Welcome! Application code lives in app.py,
        #models in model.py, tests in test.py, and seed data in seed.py.""")
        return render.index("Testing")

class BlogPost:
    def GET(self):
        pid = -1
        try:
            pid = web.input().pid
        except:
            flash("failure", "Sorry, that post doesn't exist!")
            return web.seeother("/")
        post = m.Post.by_id(pid)
        return render.blogdetail(post,render.comments())
        
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
