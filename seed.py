# -*- coding: UTF-8 -*-
from config import logger
import model as m
import sys

html1 = """
<p> Hello Friends, Welcome to my blog. This is my first post! </p>
<p> Here is a second paragraph, with some other stuff. This is <strong>important!</strong></p>
<p> Check out this <a href="http://www.google.com">New Website!</a></p>

"""

html2 = """
Bacon ipsum dolor sit amet esse duis pastrami anim, pancetta fatback capicola officia tenderloin. Meatloaf culpa ut, bacon sed sausage jerky cillum est ham ad laboris ham hock dolore. Venison ut enim, aliqua elit frankfurter et incididunt consequat culpa nostrud in. Ground round venison commodo do capicola. Id commodo laborum proident nostrud cillum duis shoulder. Shank spare ribs pastrami, jowl jerky eiusmod proident tongue occaecat enim doner pancetta capicola t-bone.

Id est labore, frankfurter sausage ex do dolore adipisicing aliquip shankle deserunt. Dolore culpa flank ad. Shankle pork loin chuck dolore short loin, pork sunt aliqua eiusmod brisket deserunt ut id. Id commodo laborum proident nostrud cillum duis shoulder. Shank spare ribs pastrami, jowl jerky eiusmod proident tongue occaecat enim doner pancetta capicola t-bone.

Cillum beef ribs ullamco incididunt pork belly nostrud tail et reprehenderit mollit tempor shoulder. Leberkas brisket elit, short ribs ham beef ribs enim nostrud sunt sirloin. Do esse capicola shoulder, nostrud pig non officia ribeye in cillum. Nisi ham hock ex nulla laborum minim tempor beef, frankfurter velit. Ex spare ribs eiusmod do dolore adipisicing jowl beef ut. Aute proident pork chop capicola. Enim fatback meatball kielbasa esse. Id commodo laborum proident nostrud cillum duis shoulder. Shank spare ribs pastrami, jowl jerky eiusmod proident tongue occaecat enim doner pancetta capicola t-bone. Id commodo laborum proident nostrud cillum duis shoulder. Shank spare ribs pastrami, jowl jerky eiusmod proident tongue occaecat enim doner pancetta capicola t-bone.

Capicola chuck in filet mignon prosciutto turkey. Ut tri-tip eiusmod pariatur. Ball tip drumstick fugiat bacon, ribeye reprehenderit dolore sausage beef kielbasa. Ex beef magna culpa labore swine venison pancetta eu irure meatball bresaola frankfurter exercitation.

Aliqua fatback tenderloin ex biltong laborum minim ut swine bresaola exercitation. Beef corned beef short loin ea. Nulla ullamco eiusmod ball tip enim, ut turkey officia tail ut tenderloin id anim. Tri-tip chuck ham hock beef pancetta pork loin. Sint ham hock aliquip sausage. Excepteur incididunt ea, eu tongue filet mignon hamburger. Ut ea nostrud short loin.

Does your lorem ipsum text long for something a little meatier? Give our generator a try… it’s tasty!
"""


def init():
    models = [m.User,m.Post,m.Image,m.Comment,m.BlogData]
    for t in reversed(models):
        logger.debug("Dropping %s" % t)
        t.drop_table(True)
    for t in models:
        logger.debug("Creating {}.\n\tColumns: {}".format(
            t, ", ".join(t._meta.columns.keys())))
        t.create_table(True)



def seed():
    init()
    about = """
             <span class="about-large">I’m a <span class="about-italic">linux server administrator</span> and <span class="about-italic">reliability expert</span>. <br> <img src="static/img/about-me.png" alt="Willy Wonka" class="about-portrait img-responsive"></span>
            <span class="about-medium">I hold a Bachelor of Science in Information Technology and have 13 years of experience in the IT business.</span> 
            <span class="about-small"> I also contribute to various open source projects including 
            <span class="about-italic">linux-kernel</span>, <span class="about-italic">emacs</span>, <span class="about-italic">node.js</span> and 
            <span class="about-italic">homebrew</span>. I use this Blog to share my experiences and my knowledge with the world.</span>
            <br><br>
            <span class="about-small">You can reach me via-email: <span class="about-italic">user at gmail dot com</span> or use the form below.</span>
    """    
    #add dummy user
    u = m.User.create_user(name='testuser',email='test@example.com',password='testy',about=about)
    
        #Initialize BlogData table, always has 1 row
    m.BlogData.initialize(title="My Testing Blog",adminurl="testadmin",owner=u.id)
    
    #add dummy Images
    img_cat = m.Image.create(url="static/img/cat.png",
                    alt='Cat',
                    title="Innocence",
                    author="""<a href="http://500px.com/RKingston" target="_blank">Rochelle Kingston</a>""",
                    link="""<a href="http://500px.com/photo/39364720" target="_blank">http://500px.com/photo/39364720</a>""",
                    license="""<a href="http://creativecommons.org/licenses/by/3.0/deed.en_US" target="_blank">CC BY 3.0</a>""",
                    )
    img_hands = m.Image.create(url="static/img/hands.png",
                    alt='Hands',
                    title="The Dirt of Coal-sm",
                    author="""<a href="http://500px.com/NadavYacobi" target="_blank">Nadav Yacobi</a>""",
                    link="""<a href="http://500px.com/photo/30720921" target="_blank">http://500px.com/photo/30720921</a>""",
                    license="""<a href="http://creativecommons.org/licenses/by/3.0/deed.en_US" target="_blank">CC BY 3.0</a>""",
                    )
    img_handb = m.Image.create(url="static/img/hands-big.png",
                    alt='Hands',
                    title="The Dirt of Coal-big",
                    author="""<a href="http://500px.com/NadavYacobi" target="_blank">Nadav Yacobi</a>""",
                    link="""<a href="http://500px.com/photo/30720921" target="_blank">http://500px.com/photo/30720921</a>""",
                    license="""<a href="http://creativecommons.org/licenses/by/3.0/deed.en_US" target="_blank">CC BY 3.0</a>""",
                    )
    img_bike = m.Image.create(url="static/img/bike.png",
                    alt='Bike',
                    title="Reserved",
                    author="""<a href="http://500px.com/MartinHricko" target="_blank">Martin Hricko</a>""",
                    link="""<a href="http://500px.com/photo/8849012" target="_blank">http://500px.com/photo/8849012</a>""",
                    license="""<a href="http://creativecommons.org/licenses/by/3.0/deed.en_US" target="_blank">CC BY 3.0</a>""",
                    )
    img_voilin = m.Image.create(url="static/img/violin.png",
                    alt='Violin',
                    title="Passion",
                    author="""<a href="http://500px.com/MartinHricko"  target="_blank">Martin Hricko</a>""",
                    link="""<a href="http://500px.com/photo/20808109" target="_blank">http://500px.com/photo/20808109</a>""",
                    license="""<a href="http://creativecommons.org/licenses/by/3.0/deed.en_US" target="_blank">CC BY 3.0</a>""",
                    )
    img_guy = m.Image.create(url="static/img/smartguy.png",
                    alt='SmartGuy',
                    title="Stranger #7",
                    author="""<a href="http://500px.com/enthuan" target="_blank">Antoine Robiez</a>""",
                    link="""<a href="http://500px.com/photo/36102156" target="_blank">http://500px.com/photo/36102156</a>""",
                    license="""<a href="http://creativecommons.org/licenses/by/3.0/deed.en_US" target="_blank">CC BY 3.0</a>""",
                    )
    #add some dummy posts
    m.Post.new(title="1st Post!",tags="blog,intro,example",author_id=u.id,html=html1,
               cat="General",subcat="Rants",image=img_handb,small_image=img_hands)
    #m.Post.new(title="What a wonderful Thing",tags="intro,wonder,cat",author_id=u.id,html=html2,img="<img src=\"static/img/cat.png\" alt=\"A Cat\">",bimg="<img src=\"static/img/hands-big.png\" alt=\"Hands\" class=\"img-responsive\">",cat="General",subcat="Misc",fav=True)
    #m.Post.new(title="Yet another Example Post",tags="example,post,dog",author_id=u.id,html=html2,img="<img src=\"static/img/cat.png\" alt=\"A Cat\">",bimg="<img src=\"static/img/hands-big.png\" alt=\"Hands\" class=\"img-responsive\">",cat="Python",subcat="Django")
    #m.Post.new(title="Why thingX sucks",tags="thingX,rant",author_id=u.id,html=html2,img="<img src=\"static/img/cat.png\" alt=\"A Cat\">",bimg="<img src=\"static/img/hands-big.png\" alt=\"Hands\" class=\"img-responsive\">",cat="Robots")
    
    #new
    c1 = m.Comment.new(1,-1,"First Post!","BillyBob","nt")
    #reply
    c2 = m.Comment.new(1,c1.id,"First Reply!","Jane","Bob, you suck!")
    #new
    c3 = m.Comment.new(1,-1,"Great Idea","SuperMan","I love it, oh my gosh it totally rocks")
    #sub-reply
    c4 = m.Comment.new(1,c2.id,"Sub Reply","IhateJane","Jane, your crazy!!! Bob rocks!!!!")
    

if __name__ == "__main__":
    print "This will ERASE the database and place some test data inside. For testing / DEV only!!!"
    x = raw_input("Continue (type YES)?")
    if x != "YES":
        print "Canceled"
        sys.exit(0)
    seed()
