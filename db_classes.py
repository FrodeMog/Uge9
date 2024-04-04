from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Enum, desc, delete, update
from sqlalchemy.orm import declarative_base, validates
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import re
from sqlalchemy.future import select
from fastapi import HTTPException

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
        
    @classmethod
    async def upsert(cls, session, username, password, id=None, **kwargs):
        try:
            user = await User.authenticate_admin(User, session, username, password)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        if id:
            # Update existing row
            stmt = update(cls).where(cls.id == id).values(**kwargs)
            await session.execute(stmt)
        else:
            # Check if a row with the same name already exists
            name = kwargs.get('name')
            existing_row = (await session.execute(select(cls).where(cls.name == name))).scalar_one_or_none()
            if existing_row:
                raise ValueError(f"A row with the name '{name}' already exists.")
            
            # Create new row
            row = cls(**kwargs)
            session.add(row)
            await session.commit()
            return row

        # Refresh the row to get the updated instance
        row = (await session.execute(select(cls).where(cls.id == id))).scalar_one_or_none()
        return row
        
    @classmethod
    async def add(cls, session, **kwargs):
        row = cls(**kwargs)
        session.add(row)
        await session.commit()
        return row
    
    async def authenticate(self, session, username, password):
        user = (await session.execute(select(User).where(User.username == username))).scalar_one_or_none()
        if not user:
            raise ValueError("Invalid username or password")
        if not check_password_hash(user.password, password):
            raise ValueError("Invalid username or password")
        return user
    
    async def authenticate_admin(self, session, username, password):
        user = (await session.execute(select(User).where(User.username == username))).scalar_one_or_none()
        if not user:
            raise ValueError("Invalid username or password")
        if not check_password_hash(user.password, password):
            raise ValueError("Invalid username or password")
        if not user.is_admin:
            raise ValueError("User is not an admin")
        return user
    
    @classmethod
    async def delete(cls, session, id, username, password):
        try:
            user = await User.authenticate_admin(User, session, username, password)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        try:
            row = (await session.execute(select(cls).where(cls.id == id))).scalar_one()
            await session.delete(row)
            await session.commit()
        except NoResultFound:
            raise HTTPException(status_code=404, detail=f"No {cls.__name__} found with id: {id}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    @classmethod
    async def get_by_field_value(cls, session, field, value, comparison: str = 'eq', order: str = 'asc'):
        comparison_mapping = {
            'eq': getattr(cls, field) == value,
            'gt': getattr(cls, field) > value,
            'lt': getattr(cls, field) < value,
            'gte': getattr(cls, field) >= value,
            'lte': getattr(cls, field) <= value,
            'ne': getattr(cls, field) != value,
        }
        order_mapping = {
            'asc': getattr(cls, field).asc(),
            'desc': getattr(cls, field).desc()
        }
        if comparison not in comparison_mapping:
            raise ValueError(f"Invalid comparison operator: {comparison}, Valid values are: \'eq\'=equal, \'gt\'=greater than, \'lt\'=less than, \'gte\'=greater than or equal to, \'lte\'=less than or equal to, \'ne\'=not equal")
        if order not in order_mapping:
            raise ValueError(f"Invalid order: {order}, Valid values are: 'asc' and 'desc'")
        
        query = select(cls).where(comparison_mapping[comparison])
        if order == 'asc':
            query = query.order_by(getattr(cls, field))
        elif order == 'desc':
            query = query.order_by(desc(getattr(cls, field)))
            
        result = await session.execute(query)
        return result.scalars().all()
    
    @classmethod
    async def get_by_field_sorted(cls, session, field, order='asc'):
        order_mapping = {
            'asc': getattr(cls, field).asc(),
            'desc': getattr(cls, field).desc()
        }
        if order not in order_mapping:
            raise ValueError(f"Invalid order: {order}, Valid values are: 'asc' and 'desc'")

        if order == 'asc':
            order_func = getattr(cls, field).asc()
        elif order == 'desc':
            order_func = getattr(cls, field).desc()

        result = await session.execute(select(cls).order_by(order_func))
        return result.scalars().all()
    
    @classmethod
    async def get_by_id(cls, session, id):
        try:
            result = await session.execute(select(cls).where(cls.id == id))
            return result.scalar_one()
        except NoResultFound:
            raise ValueError(f"No {cls.__name__} found with id: {id}")

    @classmethod
    async def get_all(cls, session):
        result = await session.execute(select(cls))
        return result.scalars().all()

class Cereal(BaseModel):
    __tablename__ = 'cereals'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
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
    def create_user(cls, username, password, email, is_admin=False):
        user = cls(username=username, password=generate_password_hash(password), email=email, is_admin=is_admin)
        return user
    
    @classmethod
    def check_password(self, password):
        if not isinstance(self.password, str):
            raise ValueError("Invalid password")
        return check_password_hash(self.password, password)
