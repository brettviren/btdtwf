import json
import hashlib
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Table
import sqlalchemy.types as types
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

from sqlalchemy import Column, Integer, String, Enum
Base = declarative_base()

class JSONBLOB(types.TypeDecorator):

    impl = String

    def process_bind_param(self, value, dialect):
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        return json.loads(value)

    def copy(self, **kw):
        return JSONBLOB(self.impl.length)    


class Type(Base):
    __tablename__ = 'types'
    id = Column(Integer, primary_key=True)
    name = Column(String, default='')
    desc = Column(String, default='')

    results = relationship("Result", back_populates="type")


def hashit(dat):
    j = json.dumps(dat)
    s = hashlib.sha1()
    s.update(j.encode("utf-8"))
    return s.hexdigest()

class Paramset(Base):
    __tablename__ = 'paramsets'
    id = Column(Integer, primary_key=True)
    name = Column(String, default='')
    created = Column(types.TIMESTAMP, default=datetime.now)
    params = Column(JSONBLOB)
    
    tasks = relationship("Task", back_populates="paramset")

    @hybrid_property
    def signature(self):
        print ('params type: %s' % type(self.params))
        if not hasattr(self, '_signature'):
            if not self.params:
                return
            self._signature = hashit([(k,v) for k,v in sorted(self.params.items())])
        return self._signature



result_set_result = Table(
    "result_set_result", Base.metadata,
    Column('resultset_id', Integer, ForeignKey('resultsets.id'), primary_key=True),
    Column('result_id', Integer, ForeignKey('results.id'), primary_key=True)
)


class Result(Base):
    __tablename__ = 'results'
    id = Column(Integer, primary_key=True)
    name = Column(String, default='')
    created = Column(types.TIMESTAMP, default=datetime.now)

    type = relationship("Type", back_populates="results")
    type_id = Column(Integer, ForeignKey("types.id"))

    tasks = relationship("Task", back_populates="result")


class Resultset(Base):
    __tablename__ = 'resultsets'

    id = Column(Integer, primary_key=True)
    name = Column(String, default='')
    created = Column(types.TIMESTAMP, default=datetime.now)

    results = relationship("Result", secondary=result_set_result, backref="resultsets")

    tasks = relationship("Task", back_populates="resultset")

    
class Function(Base):
    __tablename__ = 'functions'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    version = Column(String)
    desc = Column(String, default='')


class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    name = Column(String, default='')
    note = Column(String, default='')
    created = Column(types.TIMESTAMP, default=datetime.now)

    resultset_id = Column(Integer, ForeignKey("resultsets.id"))
    resultset = relationship("Resultset", back_populates="tasks")

    paramset_id = Column(Integer, ForeignKey("paramsets.id"))
    paramset = relationship("Paramset", back_populates="tasks")
    
    result_id = Column(Integer, ForeignKey("results.id"))
    result = relationship("Result", back_populates="tasks")
