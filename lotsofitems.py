from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, Item

engine = create_engine('sqlite:///categoryitem.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Category for Soccer
category1 = Category(name="Soccer")
session.add(category1)
session.commit()

# Category for Basketball
category2 = Category(name="Basketball")
session.add(category2)
session.commit()

# Category for Baseball
category3 = Category(name="Baseball")
session.add(category3)
session.commit()

# Category for Frisbee
category4 = Category(name="Frisbee")
session.add(category4)
session.commit()

# Category for Snowboarding
category5 = Category(name="Snowboarding")
session.add(category5)
session.commit()

# Category for Rock Climbing
category6 = Category(name="Rock Climbing")
session.add(category6)
session.commit()

# Category for Foosball
category7 = Category(name="Foosball")
session.add(category7)
session.commit()

# Category for Skating
category8 = Category(name="Skating")
session.add(category8)
session.commit()

# Category for Hockey
category9 = Category(name="Hockey")
session.add(category9)
session.commit()

# Item Soccer Cleats for Soccer
item1 = Item(name="Soccer Cleats", description='''Football boots, called
 cleats or soccer shoes in North America,[1] are an item of footwear worn
 when playing football. Those designed for grass pitches have studs on the
 outsole to aid grip. From simple and humble beginnings football boots
 have come a long way and today find themselves subject to much research,
 development, sponsorship and marketing at the heart of a multi-national
 global industry.''', category=category1)
session.add(item1)
session.commit()

# Item Jersey for Soccer
item2 = Item(name="Jersey", description='''A jersey is an item of knitted
 clothing, traditionally in wool or cotton, with sleeves, worn as a
 pullover, as it does not open at the front, unlike a cardigan. It is
 usually close-fitting and machine knitted in contrast to a guernsey that
 is more often hand knit with a thicker yarn. The word is usually used
 interchangeably with sweater.''', category=category1)
session.add(item2)
session.commit()

# Item Jersey for Baseball
item3 = Item(name="Bat", description='''A baseball bat is a smooth wooden
 or metal club used in the sport of baseball to hit the ball after it is
 thrown by the pitcher.''', category=category3)
session.add(item3)
session.commit()

# Item Frisbee for Frisbee
item4 = Item(name="Frisbee", description='''A frisbee (also called a flying
 disc or simply a disc) is a gliding toy or sporting item that is generally
 plastic and roughly 20 to 25 centimetres (8 to 10 in) in diameter with a
 lip,[1] used recreationally and competitively for throwing and catching, for
 example, in flying disc games. The shape of the disc, an airfoil in
 cross-section, allows it to fly by generating lift as it moves through the
 air while spinning.''', category=category4)
session.add(item4)
session.commit()

# Item Shinguards for Soccer
item5 = Item(name="Shinguards", description='''A shin guard or shin pad is a
 piece of equipment worn on the front of a player's shin to protect them from
 injury. These are commonly used in sports including association football
 (soccer), baseball, ice hockey, field hockey, lacrosse, rugby, cricket, and
 other sports. This is due to either being required by the rules/laws of the
 sport or worn voluntarily by the participants for protective measures.''',
category=category1)
session.add(item5)
session.commit()

# Item Two Shinguards for Soccer
item6 = Item(name="Two Shinguards", description='''A shin guard or shin pad is
 a piece of equipment worn on the front of a player's shin to protect them
 from injury. These are commonly used in sports including association football
 (soccer), baseball, ice hockey, field hockey, lacrosse, rugby, cricket, and
 other sports. This is due to either being required by the rules/laws of the
 sport or worn voluntarily by the participants for protective measures.''',
category=category1)
session.add(item6)
session.commit()

# Item Snowboard for Snowboarding
item7 = Item(name="Snowboard", description='''Snowboards are boards that are
 usually the width of one's foot longways, with the ability to glide on snow.
''', category=category5)
session.add(item7)
session.commit()

# Item Goggles for Snowboarding
item8 = Item(name="Goggles", description='''Goggles, or safety glasses, are
 forms of protective eyewear that usually enclose or protect the area
 surrounding the eye in order to prevent particulates, water or chemicals
 from striking the eyes.''', category=category5)
session.add(item8)
session.commit()

# Item Stick for Hockey
item9 = Item(name="Stick", description='''A hockey stick is a piece of
 equipment used by the players in most forms of hockey to move the ball
 or puck.''', category=category9)
session.add(item9)
session.commit()

print "added menu items!"
