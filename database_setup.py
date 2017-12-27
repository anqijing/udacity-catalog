from sqlalchemy import Column, ForeignKey, Integer, String, Enum, Date, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
import random
import string
import os
import sys

# generate secret key
secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))

Base = declarative_base()

engine = create_engine('sqlite:///moviecatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# query movie items for a specific category
def queryMovies(name):
    movies = session.query(Movieitem).filter_by(category_name=name).all()
    item = []
    for movie in movies:
    	item.append(movie.serialize)
    return item

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    email = Column(String(32), index=True)
    username = Column(String)
    picture = Column(String)
    email = Column(String)

    @property
    def serialize(self):
	    """Return object data in easily serializeable format"""
	    return {
	    	'id': self.id,
	        'name': self.name,
	    }

class Moviecategory(Base):
	__tablename__ = 'moviecategory'

	id = Column(Integer, primary_key=True)
	name = Column(String, nullable=False)

	@property
	def serialize(self):
	    """Return object data in easily serializeable format"""
	    return {
	    	'id': self.id,
	        'name': self.name,
	        'items': queryMovies(self.name),
	    }

class Movieitem(Base):
	__tablename__ = 'movieitem'

	id = Column(Integer, primary_key = True)
	name = Column(String, nullable = False)
	director = Column(String)
	description = Column(String)
	category_name = Column(String, ForeignKey('moviecategory.name'))
	moviecategory = relationship(Moviecategory)
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User)

	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
		'moviecategory': self.moviecategory.name,
		'description': self.description,
		'name': self.name,
		}