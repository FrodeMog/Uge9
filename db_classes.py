from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Enum, desc, delete, update, inspect, and_
from sqlalchemy.orm import declarative_base, validates
from sqlalchemy.exc import SQLAlchemyError, NoResultFound, IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import re
from sqlalchemy.future import select
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from functools import wraps

def error_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        session = kwargs.get('session')
        try:
            return await func(*args, **kwargs)
        except HTTPException as e:
            raise e
        except IntegrityError as e:
            if session:
                await session.rollback()
            raise HTTPException(status_code=400, detail="A row with the same unique field value already exists.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    return wrapper

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
    @error_handler
    async def add(cls, session, **kwargs):
        # Create new row
        row = cls(**kwargs)
        session.add(row)
        await session.commit()
        return row

    @classmethod
    @error_handler
    async def update(cls, session, id, **kwargs):
        # Check if a row with the given id exists
        existing_row = (await session.execute(select(cls).where(cls.id == id))).scalar_one_or_none()
        if not existing_row:
            raise HTTPException(status_code=404, detail=f"No {cls.__name__} found with id {id}")

        # Update existing row
        stmt = update(cls).where(cls.id == id).values(**kwargs)
        await session.execute(stmt)
        await session.commit()

        # Refresh the row to get the updated instance
        row = (await session.execute(select(cls).where(cls.id == id))).scalar_one_or_none()
        return row

    @classmethod
    @error_handler
    async def delete(cls, session, id):
        row = (await session.execute(select(cls).where(cls.id == id))).scalar_one_or_none()
        if row is None:
            raise HTTPException(status_code=404, detail=f"No {cls.__name__} found with id {id}")
        await session.delete(row)
        await session.commit()

    @classmethod
    @error_handler
    async def upsert(cls, session, id=None, **kwargs):
        if id:
            return await cls.update(session, id, **kwargs)
        else:
            return await cls.add(session, **kwargs)

    @classmethod
    @error_handler
    async def get_by_filters(cls, session, filters: dict, order: str = 'asc'):
        comparison_mapping = {
            'eq': lambda field, value: getattr(cls, field) == value,
            'gt': lambda field, value: getattr(cls, field) > value,
            'lt': lambda field, value: getattr(cls, field) < value,
            'gte': lambda field, value: getattr(cls, field) >= value,
            'lte': lambda field, value: getattr(cls, field) <= value,
            'ne': lambda field, value: getattr(cls, field) != value,
        }
        comparison_descriptions = {
            'eq': 'equal',
            'gt': 'greater than',
            'lt': 'less than',
            'gte': 'greater than or equal to',
            'lte': 'less than or equal to',
            'ne': 'not equal',
        }
        order_mapping = {
            'asc': lambda field: getattr(cls, field).asc(),
            'desc': lambda field: getattr(cls, field).desc()
        }
        order_descriptions = {
            'asc': 'ascending',
            'desc': 'descending',
        }

        conditions = []
        for field, (comparison, value) in filters.items():
            if not hasattr(cls, field):
                raise HTTPException(status_code=400, detail=f"Invalid order: {order}, Valid values are: {', '.join(f'{k}={v}' for k, v in order_descriptions.items())}")
            if comparison not in comparison_mapping:
                raise HTTPException(status_code=400, detail=f"Invalid comparison operator: {comparison}, Valid values are: {', '.join(f'{k}={v}' for k, v in comparison_descriptions.items())}")
            conditions.append(comparison_mapping[comparison](field, value))

        query = select(cls).where(and_(*conditions))

        if filters and order in order_mapping:
            query = query.order_by(order_mapping[order](list(filters.keys())[0]))

        result = await session.execute(query)
        results = result.scalars().all()

        if not results:
            raise HTTPException(status_code=404, detail=f"No {cls.__name__} found with given filters")
        return results

    @classmethod
    @error_handler
    async def get_by_field_value(cls, session, field, value, comparison: str = 'eq', order: str = 'asc'):
        if not hasattr(cls, field):
            raise HTTPException(status_code=400, detail=f"Invalid field: {field}")
        
        comparison_mapping = {
            'eq': getattr(cls, field) == value,
            'gt': getattr(cls, field) > value,
            'lt': getattr(cls, field) < value,
            'gte': getattr(cls, field) >= value,
            'lte': getattr(cls, field) <= value,
            'ne': getattr(cls, field) != value,
        }
        comparison_descriptions = {
            'eq': 'equal',
            'gt': 'greater than',
            'lt': 'less than',
            'gte': 'greater than or equal to',
            'lte': 'less than or equal to',
            'ne': 'not equal',
        }
        
        order_mapping = {
            'asc': getattr(cls, field).asc(),
            'desc': getattr(cls, field).desc()
        }
        order_descriptions = {
            'asc': 'ascending',
            'desc': 'descending',
        }
        
        if comparison not in comparison_mapping:
            raise HTTPException(status_code=400, detail=f"Invalid comparison operator: {comparison}, Valid values are: {', '.join(f'{k}={v}' for k, v in comparison_descriptions.items())}")
        if order not in order_mapping:
            raise HTTPException(status_code=400, detail=f"Invalid order: {order}, Valid values are: {', '.join(f'{k}={v}' for k, v in order_descriptions.items())}")
        
        query = select(cls).where(comparison_mapping[comparison])
        if order == 'asc':
            query = query.order_by(getattr(cls, field))
        elif order == 'desc':
            query = query.order_by(desc(getattr(cls, field)))
        
        result = await session.execute(query)
        results = result.scalars().all()

        if not results:
            raise HTTPException(status_code=404, detail=f"No {cls.__name__} found with field {field} {comparison_descriptions[comparison]} {value}")
        return results

    @classmethod
    @error_handler
    async def get_by_field_sorted(cls, session, field, order='asc'):
        if not hasattr(cls, field):
            raise HTTPException(status_code=400, detail=f"Invalid field: {field}")
        order_mapping = {
            'asc': getattr(cls, field).asc(),
            'desc': getattr(cls, field).desc()
        }
        order_descriptions = {
            'asc': 'ascending',
            'desc': 'descending',
        }
        if order not in order_mapping:
            raise HTTPException(status_code=400, detail=f"Invalid order: {order}, Valid values are: {', '.join(f'{k}={v}' for k, v in order_descriptions.items())}")

        if order == 'asc':
            order_func = getattr(cls, field).asc()
        elif order == 'desc':
            order_func = getattr(cls, field).desc()

        result = await session.execute(select(cls).order_by(order_func))
        if not result.scalars().all():
            raise HTTPException(status_code=404, detail=f"No {cls.__name__} found")
        return result.scalars().all()
    
    @classmethod
    @error_handler
    async def get_by_id(cls, session, id):
        result = (await session.execute(select(cls).where(cls.id == id))).scalar_one_or_none()
        if result is None:
            raise HTTPException(status_code=404, detail=f"No {cls.__name__} found with id {id}")
        return result

    @classmethod
    @error_handler
    async def get_all(cls, session):
        result = (await session.execute(select(cls))).scalars().all()
        if not result:
            raise HTTPException(status_code=404, detail=f"No {cls.__name__} found")
        return result

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
    async def authenticate(cls, username: str, password: str, session: AsyncSession):
        user = await session.execute(select(cls).where(cls.username == username))
        user = user.scalars().first()
        if user and user.check_password(password):
            return user
        return None
    
    def check_password(self, password):
        if not isinstance(self.password, str):
            raise ValueError("Invalid password")
        return check_password_hash(self.password, password)
