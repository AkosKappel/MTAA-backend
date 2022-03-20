from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.database import Base


# association table
calls_users = Table(
    'calls_users', Base.metadata,
    Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('call_id', ForeignKey('calls.id', ondelete='CASCADE'), primary_key=True)
)

users_contacts = Table(
    'users_contacts', Base.metadata,
    Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('contact_id', ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
)


class Call(Base):
    __tablename__ = 'calls'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    date = Column(DateTime(timezone=True))
    duration = Column(Integer)
    owner_id = Column(Integer, ForeignKey('users.id'))

    owner = relationship('User', back_populates='owned_calls', cascade='all,delete')
    users = relationship('User', secondary=calls_users, back_populates='calls', cascade='all,delete')

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f'Call(id={self.id}, title={self.title}, owner_id={self.owner.id})'


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    password_salt = Column(String)
    profile_picture = Column(String)

    owned_calls = relationship('Call', back_populates='owner', cascade='all,delete')
    calls = relationship('Call', secondary=calls_users, back_populates='users', cascade='all,delete')
    contacts = relationship('User', secondary=users_contacts, back_populates='contacts', cascade='all,delete',
                            primaryjoin=(users_contacts.c.user_id == id),
                            secondaryjoin=(users_contacts.c.contact_id == id))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f'User({self.id=}, {self.email=})'
