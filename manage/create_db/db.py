# -*- coding: utf-8 -*-

from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, and_
from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import sessionmaker

# declare metadata
Base = declarative_base()

# DB Entity Class
class PropertiesFile(Base):    
    # Table Column
    id   = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256))
    
    properties = relationship('Property', uselist=True, backref='properties_files')
    comments = relationship('Comment', uselist=True, backref='comments')

    # Table Title
    __tablename__ = 'properties_files'
    
    def __repr__(self):
        return '<PropertiesFile(%d, %s)>' %(self.id, self.name)

class Property(Base):
    # Table Column
    id           = Column(Integer, primary_key=True, autoincrement=True)
    name         = Column(String(256))
    fileId       = Column(Integer, ForeignKey('properties_files.id'))
    line         = Column(Integer)
    value        = Column(String(1000), default='')
    hasArgs      = Column(Boolean, default=False)
    isMultiline  = Column(Boolean, default=False)
    isTranslated = Column(Boolean, default=False)

    # Table Title
    __tablename__ = 'properties'
    
    # Talbe Attributes
    __table_args__ = (
                UniqueConstraint('name', 'fileId', name='unique_idx_name_fileId'),
                )
    
    def __repr__(self):
        return '<Property(%d, %s, %d, %d, %s, %d)>' %(self.id, self.name, self.fileId, self.line, self.value, self.isTranslated)

class Comment(Base):
    # Table Column
    id          = Column(Integer, primary_key=True, autoincrement=True)
    content     = Column(String(256))
    fileId      = Column(Integer, ForeignKey('properties_files.id'))
    line        = Column(Integer)
    
    # Table Title
    __tablename__ = 'comments'
    
    def __repr__(self):
        return '<Comment(%d, %s, %d)>'.format(self.id, self.fileId, self.fileId)

# DB Session Wrapper Class
class SessionWrapper(object):
    def __init__(self, dbfilepath, encoding=None, echo=False):
        print('connect to {0}'.format(dbfilepath))
        sqlitepath = 'sqlite:///'+str(dbfilepath)
        if encoding:
            sqlitepath += '?' + encoding
        self._engine = create_engine(sqlitepath, echo=echo)
        Base.metadata.create_all(self._engine)
        self._sessionmaker = sessionmaker(bind=self._engine)
        self._session = self._sessionmaker()

    def add(self, record):
        self._session.add(record)
    
    def delete(self, record):
        self._session.delete(record)

    def commit(self):
        self._session.commit()
    
    def close(self):
        self._session.close()
    
    def deletePropertiesFiles(self):
        result = self._session.query(PropertiesFile)
        if result:
            result.delete()
    
    def deleteProperties(self):
        result = self._session.query(Property)
        if result:
            result.delete()

    def deleteComments(self):
        result = self._session.query(Comment)
        if result:
            result.delete()

    def getAllFiles(self):
        return self._session.query(PropertiesFile).all()
    
    def queryPropertiesFileById(self, id):
        return self._session.query(PropertiesFile).\
            filter(PropertiesFile.id==id).\
            first()        
    
    def queryPropertiesFileByName(self, filename):
        return self._session.query(PropertiesFile).\
            filter(PropertiesFile.name==filename).\
            first()
    
    def queryProperties(self, filename, order=Property.line):
        return self._session.query(Property).\
            join(PropertiesFile).\
            filter(PropertiesFile.name==filename).\
            order_by(order).\
            all()

    def queryProperty(self, filename, name):
        return self._session.query(Property).\
            join(PropertiesFile).\
            filter(and_(PropertiesFile.name==filename, Property.name==name)).\
            first()
    
    def queryComments(self, filename, order=Comment.line):
        return self._session.query(Comment).\
            join(PropertiesFile).\
            filter(PropertiesFile.name==filename).\
            order_by(order).\
            all()

    
    
