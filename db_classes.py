from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import declarative_base, relationship, validates
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import re

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if value is None and not self.__table__.c[key].nullable:
                raise ValueError(f"{key} cannot be null")
            if isinstance(self.__table__.c[key].type, String) and self.__table__.c[key].type.length is not None and len(value) > self.__table__.c[key].type.length:
                raise SQLAlchemyError(f"{key} must be less than {self.__table__.c[key].type.length} characters")
            setattr(self, key, value)

    def __repr__(self):
        return str({column.name: getattr(self, column.name) for column in self.__table__.columns if hasattr(self, column.name)})
    
class Cereal(BaseModel):
    __tablename__ = 'cereals'

    name = Column(String, primary_key=True)
    mfr = Column(Enum('A', 'G', 'K', 'N', 'P', 'Q', 'R'), nullable=False)
    type = Column(Enum('C', 'H'), nullable=False)
    calories = Column(Integer, nullable=False)
    protein = Column(Integer, nullable=False)
    fat = Column(Integer, nullable=False)
    sodium = Column(Integer, nullable=False)
    fiber = Column(Float, nullable=False)
    carbo = Column(Float, nullable=False)
    sugars = Column(Integer, nullable=False)
    potass = Column(Integer, nullable=False)
    vitamins = Column(Integer, nullable=False)
    shelf = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    cups = Column(Float, nullable=False)
    rating = Column(Float, nullable=False)

    @validates
    def validate_mfr(self, key, mfr):
        if mfr not in ['A', 'G', 'K', 'N', 'P', 'Q', 'R']:
            raise ValueError("Invalid manufacturer")
        return mfr

    @validates
    def validate_type(self, key, type):
        if type not in ['C', 'H']:
            raise ValueError("Invalid type")
        return type
    
    @classmethod
    def get_cereal(cls, name):
        return cls.query.get(name)
    
    @classmethod
    def get_all_cereals(cls):
        return cls.query.all()


class User(BaseModel):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    @validates('username')
    def validate_username(self, key, username):
        if len(username) < 3:
            raise ValueError("Username must be at least 3 characters long")
        if not re.match("^[A-Za-z0-9_]+$", username):
            raise ValueError("Username can only contain letters, numbers, and underscores")
        return username.lower()

    @validates('email')
    def validate_email(self, key, email):
        pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if not re.match(pattern, email):
            raise ValueError("Invalid email address")
        return email
    
    @classmethod
    def create_user(cls, username, email, password):
        user = cls(username=username, email=email, password=generate_password_hash(password))
        return user
    
    @classmethod
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    @classmethod
    def get_user(cls, username):
        return cls.query.filter_by(username=username).first()
    
    @classmethod
    def get_all_users(cls):
        return cls.query.all()
    
    @classmethod
    def get_user_by_email(cls, email):
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def get_user_by_id(cls, user_id):
        return cls.query.get(user_id)