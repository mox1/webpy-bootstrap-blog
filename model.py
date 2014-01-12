import logging
logger = logging.getLogger("")
import hashlib
from datetime import datetime
import traceback
import peewee as pw
from playhouse.signals import Model, pre_save
from peewee import SqliteDatabase
import config
import operator
import re

DoesNotExist = pw.DoesNotExist
SelectQuery = pw.SelectQuery


#we need these two lines or SQLite will complain about interthread access
db = SqliteDatabase('peewee.db',threadlocals=True)
db.connect()

def better_get(self, **kwargs):
    if kwargs:
        return self.filter(**kwargs).get()
    clone = self.paginate(1, 1)
    try:
        return clone.execute().next()
    except StopIteration:
        raise self.model_class.DoesNotExist(
            'instance matching query does not exist:\nSQL: %s\nPARAMS: %s' % (
                self.sql()))

pw.SelectQuery.get = better_get


#http://stackoverflow.com/questions/4984647/accessing-dict-keys-like-an-attribute-in-python
#used to access dict elements with a .
class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

class BaseModel(Model):
    created_at = pw.DateTimeField(default="now()",null=False)
    id = pw.PrimaryKeyField()
    
    class Meta:
        database = db

    def update_fields(self, **kwargs):
        for field, value in kwargs.items():
            setattr(self, field, value)
        return self.save()

class Image(BaseModel):
    url = pw.CharField(max_length=4096,null=False)
    alt = pw.CharField(max_length=512,null=True)
    title = pw.CharField(max_length=1024,null=False,default="Default Title")
    author = pw.CharField(max_length=1024,null=True)
    link = pw.CharField(max_length=4096,null=False)
    license = pw.CharField(max_length=1024,null=False)
    @staticmethod
    def update_from_input(data):
        try:
            imageid = data["uimageid"]
            image = Image.get(Image.id==int(imageid))
            url = data["uiurl"]
            alt = data["uialt"]
            title = data["uititle"]
            author = data["uiauthor"]
            link = data["uilink"]
            license = data["uilic"]
        except KeyError,e:
            traceback.print_exc()
            return (None,"Required Field missing: %s" % e.message)
        except Exception,e:
            traceback.print_exc()
            return (None,"Sorry there was an error: %s" % e.message)
        
        image.url = url
        image.alt = alt
        image.title = title
        image.author = author
        image.link = link
        image.license = license
        image.save()
        return (image,"Successfully updated image: \"%s\"" % title)
    
    @staticmethod
    def new_from_input(data):
        try:
            url = data["niurl"]
            alt = data["nialt"]
            title = data["nititle"]
            author = data["niauthor"]
            link = data["nilink"]
            license = data["nilic"]
        except KeyError,e:
            traceback.print_exc()
            return (None,"Required Field missing: %s" % e.message)
        except Exception,e:
            traceback.print_exc()
            return (None,"Sorry there was an error: %s" % e.message)
        
        
        image = Image.create(url=url,alt=alt,title=title,author=author,link=link,license=license)
        return (image,"Successfully created new image: \"%s\"" % title)
    
    @staticmethod
    def get_all():
        return Image.select()
    
    @staticmethod
    def by_id(id):
        u = None
        try:
            u=Image.get(Image.id == id)
        except: 
            return None
        return u

    
    
class User(BaseModel):
    name = pw.CharField(max_length=200, null=False)
    email = pw.CharField(max_length=200, null=False)
    about = pw.TextField(null=False,default="I'm the owner of this Blog")
    contact_html = pw.TextField(null=False,default="<a href=\"mailto:changethis@localhost.local\">changethis@localhost.local</a>" )
    crypted_password = pw.CharField(max_length=40, null=False)
    salt = pw.CharField(max_length=40, null=False)
    remember_token = pw.CharField(max_length=64, null=True)
    
    @staticmethod
    def is_setup():
        if User.select(User.id).count() > 0:
            return True
        else:
            return False
    
    @staticmethod
    def update_from_input(data):
        
        try:
            userid = data["userid"]
            user = User.get(User.id==int(userid))
            name = data["name"]
            email = data["email"]
            about = data["about"]
            contact_html = data["contact_html"]
            #lets see if user wants to update password
            p1 = data.get("p1","")
            p2 = data.get("p2","")
            if len(p1) > 1 and (p1 == p2):
                #yep update password
                user.password = p1
            else:
                user.password = None
            user.name = name
            user.email = email
            user.about = about
            user.contact_html = contact_html
            user.save()
             
        except KeyError,e:
            traceback.print_exc()
            return (None,"Required Field missing: %s" % e.message)
        except Exception,e:
            traceback.print_exc()
            return (None,"Sorry there was an error: %s" % e.message)
        
        user.save()
        return (user,"Successfully updated user!")
    
        
    
    @staticmethod 
    def firstuser():
        try:
            resl = User.select().limit(1).execute()
            for x in resl:
                pass
            return x
        except Exception:
            return None
        
    @staticmethod
    def attempt_auth(username,pw):
        try:
            #check if user already exists
            u = User.get(User.email == username)
        except User.DoesNotExist:
            return (None, "Bad username or password")
        resl = u.authenticate(pw)
        if resl == True:
            #update last login time
            #u.last_login = datetime.now()
            #u.save()
            return (u, "Successfully Logged in as %s" % username)
        else:
            return (None,"Bad username or password")

    @staticmethod
    def new_from_input(data):
        try:
            name = data["username"]
            email = data["email"]
            password = data["pass1"]
        except KeyError,e:
            traceback.print_exc()
            return (None,"Required Field missing: %s" % e.message)
        except Exception,e:
            traceback.print_exc()
            return (None,"Sorry there was an error: %s" % e.message)
        
        user = User.create_user(name=name,email=email,password=password)
        return (user,"User %s created!" % name)
    

    @staticmethod
    def create_user(name,email,password,about=""):
        try:
            #check if user already exists
            User.get(User.name == name)
        except User.DoesNotExist:
            #nope , create him
            #the @pre_save thingy below will auto salt and hash the password
            user = User.create(name=name,email=email,password=password,created_at=datetime.now(),about=about)
            #users chang change all of this in the admin page, just create it now
            #This call can safely be made multiple times, it is just a no-op for users 2+
            BlogData.initialize(title="My Blog",adminurl="admin",owner=user.id)
            return user
            
    @staticmethod
    def by_id(id):
        u = None
        try:
            u=User.get(User.id == id)
        except: 
            return None
        return u
    
    @staticmethod
    def by_name(name):
        u = None
        try:
            u=User.get(User.name == name)
        except: 
            return None
        return u
    
    def authenticate(self, password):
        return self.crypted_password == crypt_password(password,
                                                       self.salt)

    def __unicode__(self):
        return unicode(self.name)

class Post(BaseModel):
    image = pw.ForeignKeyField(Image,null=True)
    small_image = pw.ForeignKeyField(Image,related_name="small_image")
    title = pw.CharField(max_length=200, null=False)
    #comma separated list of "tags"
    tags = pw.TextField(null=True)
    author = pw.ForeignKeyField(User)
    updated = pw.DateTimeField(null=True)
    category = pw.CharField(max_length=256,null=True)
    subcategory = pw.CharField(max_length=256,null=True)
    html = pw.TextField(null=False)
    prev_html = pw.TextField(null=True)
    favorite = pw.BooleanField(default=False)
    public = pw.BooleanField(default=True)
    views = pw.IntegerField(null=False,default=0)
    #Post moderation options for comments
    #0 = no moderation (all comments allowed)
    #1 = moderated (admin must approve comments)
    #2 = disabled (no new comments allowed)
    moderate = pw.IntegerField(null=False,default=0)
        
    #data is web.input, mapping is
    # title = data.nptitle
    # title_img = data.nptitleimg
    # image = data.npimgsel
    # small_image = data.npimgsmsel
    # big_img = data.npimg
    # tags = data.nptags
    # category = data.npcat
    # subcategory = data.npsubcat
    # html = data.nphtml
    # favorite = data.npfav
    # public = data.nppriv
    @staticmethod
    def update_from_input(data,userid):
        try:
            postid = data["upostid"]
            post = Post.get(Post.id==int(postid))
            title = data["uptitle"]
            image = data["upimgsel"]
            small_image = data["upimgsmsel"]
            tags = data["uptags"]
            cat = data["upcat"]
            scat = data["upsubcat"]
            html = data["uphtml"]
            mod = int(data["upmod"])
            if data.get("upfav","false") == "true":
                fav = True
            else:
                fav = False
            if data.get("uppriv","false") == "true":
                public = False
            else:
                public = True
        except KeyError,e:
            traceback.print_exc()
            return (None,"Required Field missing: %s" % e.message)
        except Exception,e:
            traceback.print_exc()
            return (None,"Sorry there was an error: %s" % e.message)
        
        #updat all fields
        post.title = title
        post.image = image
        post.small_image = small_image
        post.tags = tags
        post.category = cat
        post.subcategory = scat
        #lets just save the old post, for user screw-ups
        post.prev_html = post.html
        post.html = html
        post.favorite = fav
        post.public = public
        post.updated = datetime.now()
        post.moderate = mod
        post.save()
        return (post,"Successfully updated post!")
    
    
    @staticmethod
    def all(evenprivate=False):
        if evenprivate == True:
            return Post.select().order_by(Post.views.desc())
        else:
            return Post.select().where(Post.public==True).order_by(Post.views.desc())
    #return the n most popular post, pased on views
    #TODO: Determine the performance of this query
    @staticmethod
    def most_popular(n):
        return Post.select().where(Post.public==True).order_by(Post.views.desc()).limit(n)
    
    #TODO: optimize this in some way, kludgy and slow, but works
    @staticmethod
    def search(query,page=1,max=10):
        search_str = "%s%s%s" % (config.db_wildcard,query,config.db_wildcard)
        posts = Post.select().where( (Post.html % search_str) | (Post.title % search_str) |\
                                     (Post.category % search_str) | (Post.subcategory % search_str) ).order_by(Post.created_at.desc()).paginate(page,max)
        return posts
    
    @staticmethod
    def by_category(cat,subcat,page=1,max=10):
        posts = None
        if subcat == "":
            posts = Post.select().where((Post.category == cat) & (Post.public==True)).order_by(Post.created_at.desc()).paginate(page,max)
        else:   
            posts = Post.select().where((Post.category == cat) & (Post.subcategory == subcat) & (Post.public==True)).order_by(Post.created_at.desc()).paginate(page,max)
            
        return posts
    
    @staticmethod
    def by_tag(tag,page=1,max=10):
        search_str = "%s%s%s" % (config.db_wildcard,tag,config.db_wildcard)
        posts = Post.select().where((Post.tags % search_str) & (Post.public==True)).order_by(Post.created_at.desc()).paginate(page,max)
        return posts
    
    @staticmethod
    #get the next amt posts afer date
    def get_next(date,amt=5):
        posts = Post.select().where((Post.created_at > date) & (Post.public==True)).order_by(Post.created_at.desc()).limit(amt)
        return posts
    @staticmethod
    #get the previous amt posta before date
    def get_prev(date,amt=5):
        posts = Post.select().where((Post.created_at < date) & (Post.public==True)).order_by(Post.created_at.desc()).limit(amt)
        return posts
    
    @staticmethod
    def get_favs(amt=5):
        posts = Post.select().where((Post.favorite == True) & (Post.public==True)).order_by(Post.created_at.desc()).limit(amt)
        return posts
    @staticmethod
    def nth_most_recent(n):
        posts = Post.select().where(Post.public==True).order_by(Post.created_at.desc()).limit(n)
        item = None
        for item in posts:
            pass
        return item
    @staticmethod
    def recent_posts(n):
        return Post.select().where(Post.public==True).order_by(Post.created_at.desc()).limit(n)

    
    #data is web.input, mapping is
    # title = data.nptitle
    # title_img = data.nptitleimg
    # image = data.npimgsel
    # small_image = data.npimgsmsel
    # big_img = data.npimg
    # tags = data.nptags
    # category = data.npcat
    # subcategory = data.npsubcat
    # html = data.nphtml
    # favorite = data.npfav
    # public = data.nppriv
    @staticmethod
    def new_from_input(data,userid):
        try:
            title = data["nptitle"]
            image = data["npimgsel"]
            small_image = data["npimgsmsel"]
            tags = data["nptags"]
            cat = data["npcat"]
            scat = data["npsubcat"]
            html = data["nphtml"]
            mod = int(data["npmod"])
            if data.get("npfav","false") == "true":
                fav = True
            else:
                fav = False
            if data.get("nppriv","false") == "true":
                public = False
            else:
                public = True
        except KeyError,e:
            traceback.print_exc()
            return (None,"Required Field missing: %s" % e.message)
        except Exception,e:
            traceback.print_exc()
            return (None,"Sorry there was an error: %s" % e.message)
        
        post = Post.new(title=title,tags=tags,author_id=userid,image=image,
                        small_image=small_image,html=html,cat=cat,subcat=scat,fav=fav,public=public,moderate=mod)
        return (post,"Successfully created new post!")
    
    
    @staticmethod
    def new(title,tags,author_id,html,image,small_image,cat=None,subcat=None,fav = False,public=True,moderate=0):
        #get user by id
        user = User.by_id(author_id)
        p = Post.create(title=title,tags=tags,author=user,html=html,
                        image=image,small_image=small_image,created_at=datetime.now(),
                        favorite=fav,category=cat,subcategory=subcat,moderate=moderate)
        return p
    
    #every time this is called, a pageview count is updated"
    #only call this when you actually render the post
    @staticmethod
    def by_id(id):
        p = None
        try:
            p=Post.select().where((Post.id==id) & (Post.public==True) ).get()
        except Exception:
            traceback.print_exc()
            return None
        #Naive hit count
        p.views += 1
        p.save()
        return p
    
    @staticmethod
    def get_recent(page=1,max=10):
        return Post.select().where(Post.public==True).order_by(Post.created_at.desc()).paginate(page,max)
    
    #This should *NEVER* be called on each page hit, it is an expensive query/op
    #cached inside BlogData below
    @staticmethod
    def all_tags():
        tag_map = {}
        tags = Post.select(Post.tags).where(Post.public==True)
        for taglist in tags:
            for tag in taglist.tags.split(","):
                cur = tag_map.get(tag,0)
                tag_map[tag] = cur+1
        sorted_x = sorted(tag_map.iteritems(), key=operator.itemgetter(1),reverse=True)
        return sorted_x


class Comment(BaseModel):
    title = pw.CharField(max_length=512,default="Comment")
    author = pw.CharField(max_length=512,null=False)
    auth_url = pw.CharField(max_length=2048,null=True)
    ip = pw.CharField(max_length=20,null=True)
    post = pw.ForeignKeyField(Post,null=False)
    text = pw.TextField(max_length=16656,null=False)
    email = pw.CharField(max_length=1024,null=False,default="none@none.net")
    parent = pw.ForeignKeyField('self',related_name='children',null=True)
    rank = pw.IntegerField(null=False,default=0)
    indent = pw.IntegerField(null=False,default=0)
    from_admin = pw.BooleanField(null=False,default=False)
    #0 = displayed 
    #1-4 Future use?
    #5 = in moderation Q
    #6+ future use 
    status = pw.IntegerField(null=False,default=0)

    @staticmethod
    def update_from_input(data):
        try:
            commentid = data["cid"]
            comment = Comment.get(Comment.id ==int(commentid))
            title = data["title"]
            author = data["name"]
            email = data["email"]
            text = data["message"]
            status = int(data["status"])
        except KeyError,e:
            traceback.print_exc()
            return (None,"Required Field missing: %s" % e.message)
        except Exception,e:
            traceback.print_exc()
            return (None,"Sorry there was an error: %s" % e.message)
        
        comment.title = title
        comment.author = author
        comment.email = email
        comment.text = text
        comment.status = status
        comment.save()
        return "Successfully updated comment \"%s\" by \"%s\"" % (title,author)
            
    @staticmethod
    def by_id(id):
        u = None
        try:
            u=Comment.get(Comment.id == id)
        except: 
            return None
        return u


    @staticmethod
    def remove(postid):
        try:
            pid = int(postid)
            com = Comment.get(Comment.id == pid)
            rank = com.rank
            indent = com.indent
            gp = com.parent
            #we need to "fix" this posts descendants indentation, do that now
            with db.transaction():            
                Comment.recur_del(com)
                #we also need to find our children and fix the "parent" to our parent (from grandparent to parent)
                Comment.update(parent = gp).where(Comment.parent == pid).execute()
                #remove comment fom db
                com.delete_instance()
                #update rank of all comments below this
                Comment.update(rank = Comment.rank - 1).where(Comment.rank > rank).execute()

            return "Comment successfully deleted"
        except Exception, e:
            traceback.print_exc()
            return "Error removing comment: %s" % e
         
    @staticmethod
    def recur_del(comment):
        if comment == None or comment.id == None or comment.id < 0:
            return
        else:
            comment.indent -= 1
            #comment.rank -= 1
            comment.save()
        children = Comment.select().where(Comment.parent == comment.id).execute()
        if children == None:
            return
        for c in children:
            Comment.recur_del(c)

    @staticmethod
    def get_comments(postid,show_mod):
        if show_mod == False:
            count = Comment.select().where(Comment.post == postid & Comment.status == 0).order_by(Comment.rank.asc()).count()
            comments = Comment.select().where(Comment.post == postid & Comment.status == 0).order_by(Comment.rank.asc())
        else:
            count = Comment.select().where(Comment.post == postid).order_by(Comment.rank.asc()).count()
            comments = Comment.select().where(Comment.post == postid).order_by(Comment.rank.asc())  
                 
        return (count,comments)

    @staticmethod
    def new(postid,parentid,title,author,text,email="none@none.net",admin=False,ip=None):
        #1st get post, check if comments are allowed
        post = Post.by_id(postid)
        if (post == None) or (post.moderate == 2):
            return None
        #put this post into a "review by admin state"
        if post.moderate ==1:
            status = 5
        else:
            status = 0
        
        #never moderate admin posts
        if admin == True:
            status = 0
        #we need to convert \n into <br>
        text = newline_to_break(text)
        rank = 0
        indent = 0
        lastcomment = None
        if parentid == -1:
            #just insert at the end, 
            c = Comment.select().where(Comment.post == postid).order_by(Comment.rank.desc()).limit(1).execute()
            for lastcomment in c:
                pass
            if lastcomment != None:
                rank = lastcomment.rank+1
            else:
                #this must be the first comment
                pass
            return Comment.create(title=title,author=author,post=postid,text=text,
                                  rank=rank,indent=indent,email=email,created_at=datetime.now(),from_admin=admin,status=status,ip=ip)
        else:
            parent=Comment.get(Comment.id==parentid)
            start_rank = parent.rank
            #update all old posts whose rank are greater than parent
            Comment.update(rank=Comment.rank + 1).where(Comment.rank > start_rank).execute()
            #insert at rank of parent + 1 aka where we just made room
            new_comment = Comment.create(email=email,parent=parent,title=title,
                                         author=author,post=postid,text=text,rank=start_rank+1,indent=parent.indent+1,
                                         created_at=datetime.now(),from_admin=admin,status=status,ip=ip)
            

            return new_comment

#this class / table performs 2 function
# 1. it is used as an optimization
#    holding the results of other queries that rarely change
# 2. Holding static data (blog title, admin page, etc, etc
# It really should only have 1 row
class BlogData(BaseModel):
    #informational fields 
    title = pw.CharField(max_length=512,default="My Blog")
    adminurl = pw.CharField(max_length=4096,default="blogstrap-admin")
    contactline = pw.TextField(null=False,default="""I'm happy to hear from my readers. Thoughts, feedback, critique - all welcome! Drop me a line:""")
    owner = pw.ForeignKeyField(User,null=True)
    #statistical blog fields, will be updated from time to time
    total_posts = pw.IntegerField(null=False,default=0)
    total_comments = pw.IntegerField(null=False,default=0)
    total_authors = pw.IntegerField(null=False,default=0)
    #csv of the 10 most popular tags on the site
    popular_tags = pw.TextField(null=False,default="")
    
    @staticmethod
    def is_setup():
        if BlogData.select(BlogData.id).count() > 0:
            return True
        else:
            return False
    
    @staticmethod
    def initialize(title,adminurl,owner):
        #just insert 1 row of defaults
        if BlogData.select(BlogData.id).count() > 0:
            #we already have a row, go away
            return None
        return BlogData.create(title=title,adminurl=adminurl,owner=owner,created_at=datetime.now())
    
    @staticmethod
    def update_info_from_input(data):
        try:
            title = data["title"]
            adminurl = data["adminurl"]
            contactline = data["contact"]
        except KeyError,e:
            traceback.print_exc()
            return (None,"Required Field missing: %s" % e.message)
        except Exception,e:
            traceback.print_exc()
            return (None,"Sorry there was an error: %s" % e.message)
        bdata = BlogData.select().limit(1).get()
        bdata.title = title
        #slashes really hose the adminurl, remove them
        adminurl = adminurl.replace("/","").replace("\\","")
        bdata.adminurl = adminurl
        bdata.contactline = contactline
        bdata.save()
        return (bdata,"Successfully updated blog data! Note: admin url is currently set to: /admin/%s " % adminurl)
    @staticmethod
    def update_stats():
        try:
            bdata = BlogData.select().limit(1).get()
        except:
            #BlogData doesnt have any data yet
            return
        
        tp = Post.select(Post.id).count()
        tc = Comment.select(Comment.id).count()
        ta = Post.select(Post.author).distinct().count() 
        #all_tags returns a list of tuples [(tag,cnt),(tag,cnt)]
        popular_tagstr = ""
        for tag,cnt in Post.all_tags()[0:10]:
            popular_tagstr += "%s," % tag
        if(len(popular_tagstr) > 1):
            popular_tagstr = popular_tagstr[:-1]
        bdata.total_posts = tp
        bdata.total_comments = tc
        bdata.total_authors = ta
        bdata.popular_tags = popular_tagstr
        bdata.save()
        
    #cached in a global variable most of the time
    #update at various times (when admin updates global settings
    #at requested interval
    @staticmethod
    def get(update=False):
        if update == True:
            BlogData.update_stats()
        
        try:
            bd = BlogData.select().limit(1).get()
        except:
            #BlogData isnt setup, return some simple default values
            bd =   AttrDict({"title" : "Blog",
                             "total_posts" : 0, 
                             "total_comments" : 0, 
                             "total_authors" : 0, 
                             "popular_tags" : "",
                             "adminurl" : "admin",
                             "owner" : None,
                             "contactline": ""})
        
        return bd

def newline_to_break(text):
    #first re
    #normalize newlines
    out = text.replace("\r\n", "\n")
    #convert \n to <br> while replacing multipls with a single <br>
    out = re.sub("\n+","<br>",out)
    return out
    

def print_dates(d):
    return d.strftime("%B %d %Y ")        
        
    
def create_salt(email):
    return hashlib.md5("--%s--%s--" % (datetime.now(),
                                       email)).hexdigest()


def crypt_password(password, salt):
    return hashlib.md5("--%s--%s--" % (salt, password)).hexdigest()


# Fix reloading during development :-/
try:
    pre_save.disconnect(name='crypt_password_before_save')
except:
    pass


def day_suffix(dom):
    if (dom % 100 > 10) and (dom % 100 < 14):
        return str(dom)+"th"
    x = dom % 10
    if dom == 1:  return str(dom)+"st"
    elif dom == 2:  return str(dom)+"nd"
    elif dom == 3:  return str(dom)+"rd"
    else: return str(dom)+"th"

#input a datetime
#output str, formatted according to config.TIME_FORMAT
def datetime_str(d,short=True):
    if short == True:
        try:
            return datetime.strftime(d,config.TIME_FORMAT)
        except Exception:
            return "Mon, Jan 1 1900"
    else:
        #try:
        ds = day_suffix(d.day)
        return datetime.strftime(d,config.LONG_TIME_FORMAT % ds)
        #except:
        traceback.print_exc()
        return "Monday, January 1st 1900"

#input a datetime
#ouput str, formatted as days hours minutes ago
def datetime_ago(d):
    now = datetime.now()
    delta = now - d
    out_str = ""
    #if we are older than 1 day, just print years, days
    if delta.days > 1:
        #yes were ignoring leap year here, this is for display only
        years,days = divmod(delta.days,365)
        if years > 1:
            out_str += "%d years " % years
        elif years == 1:
            out_str += "1 year "
            
        if days > 1:
            out_str += "%d days" % days
        elif days == 1:
            out_str += "1 day"
        else:
            #remove the space we added
            out_str = out_str[:-1]
    #print hours and minutes
    else:
        hours, rem = divmod(delta.seconds, 3600)
        mins,secs = divmod(rem, 60)
        if hours > 1:
            out_str += "%d hours " % hours
        elif hours == 1:
            out_str += "1 hour "
            
        if mins > 1:
            out_str += "%d minutes" % mins
        elif mins == 1:
            out_str += "1 minute"
        else:
            #remove the space we added
            out_str = out_str[:-1]
            
    return out_str + " ago"
            
    
#update comment display order when posting
#see :http://evolt.org/node/4047/
#@pre_save(sender=Comment)
#def update_ranks(model_class,instance,created):
#    if not instance.rank:
#        return
#    if created == True:
#        Comment.update(rank=Comment.rank + 1).where(Comment.rank > instance.rank)
#    else:
#        print "in update_rank, but created was false"

@pre_save(sender=User)
def crypt_password_before_save(model_class, instance, created):
    if not instance.password:
        return
    if not instance.salt:
        instance.salt = create_salt(instance.email)
    instance.crypted_password = crypt_password(instance.password,
                                               instance.salt)
