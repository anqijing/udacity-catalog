from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Moviecategory, Movieitem
engine = create_engine('sqlite:///moviecatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

user1 = User(email='anqi@email.com', username='Anqi')
session.add(user1)
session.commit()

action = Moviecategory(name='Action movie')
session.add(action)
session.commit()

adventure = Moviecategory(name='Adventure movie')
session.add(adventure)
session.commit()

war = Moviecategory(name='War movie')
session.add(war)
session.commit()

comedy = Moviecategory(name='Comedy movie')
session.add(comedy)
session.commit()

musical = Moviecategory(name='Musical movie')
session.add(musical)
session.commit()

science = Moviecategory(name='Science movie')
session.add(science)
session.commit()


actionmovie1 = Movieitem(name="The Bourne Ultimatum ", 
	director="Paul Greengrass", 
	moviecategory = action,
	user=user1,
	description="Jason Bourne dodges a ruthless CIA official and his agents from a new assassination program while searching for the origins of his life as a trained killer.")
session.add(actionmovie1)
session.commit()

actionmovie2 = Movieitem(name="Mission: Impossible", 
	director="Brian De Palma", 
	moviecategory = action,
	user=user1,
	description="An American agent, under false suspicion of disloyalty, must discover and expose the real spy without the help of his organization.")
session.add(actionmovie2)
session.commit()

actionmovie3 = Movieitem(name="Casino Royala", 
	director="Martin Campbell",
	moviecategory = action,
	user=user1,
	description="Armed with a license to kill, Secret Agent James Bond sets out on his first mission as 007, and must defeat a private banker to terrorists in a high stakes game of poker at Casino Royale, Montenegro, but things are not what they seem.")
session.add(actionmovie3)
session.commit()
