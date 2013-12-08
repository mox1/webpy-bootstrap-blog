# -*- coding: UTF-8 -*-
from config import logger
import model as m

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
    models = [m.User,m.Post]
    for t in reversed(models):
        logger.debug("Dropping %s" % t)
        t.drop_table(True)
    for t in models:
        logger.debug("Creating {}.\n\tColumns: {}".format(
            t, ", ".join(t._meta.columns.keys())))
        t.create_table(True)



def seed():
    init()
    u = m.User.create_user(name='testuser',email='test@example.com',password='testy')
    print u
    m.Post.new_post(title="1st Post!",tags="blog,intro,example",author_id=u.id,html=html1,img="<img src=\"static/img/cat.png\" alt=\"A Cat\">",bimg="<img src=\"static/img/hands-big.png\" alt=\"Hands\" class=\"img-responsive\">")
    m.Post.new_post(title="What a wonderful Thing",tags="intro,wonder,cat",author_id=u.id,html=html2,img="<img src=\"static/img/cat.png\" alt=\"A Cat\">",bimg="<img src=\"static/img/hands-big.png\" alt=\"Hands\" class=\"img-responsive\">")
    m.Post.new_post(title="Yet another Example Post",tags="example,post,dog",author_id=u.id,html=html2,img="<img src=\"static/img/cat.png\" alt=\"A Cat\">",bimg="<img src=\"static/img/hands-big.png\" alt=\"Hands\" class=\"img-responsive\">")
    m.Post.new_post(title="Why thingX sucks",tags="thingX,rant",author_id=u.id,html=html2,img="<img src=\"static/img/cat.png\" alt=\"A Cat\">",bimg="<img src=\"static/img/hands-big.png\" alt=\"Hands\" class=\"img-responsive\">")

if __name__ == "__main__":
    seed()
