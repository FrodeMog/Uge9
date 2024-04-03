import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from db_pydantic_classes import *
from db_classes import *
from typing import List, Annotated
import uvicorn
from werkzeug.security import check_password_hash
import pymysql
#uvicorn main:app --reload
#npx create-react-app storage-app
#http://localhost:8000/docs

import pandas as pd
from sqlalchemy.orm import Session
from db_classes import Cereal  # Import your Cereal class

def setup_engine_and_session():
    # Load database information from db_info.json
    with open('db_info.json') as f:
        db_info = json.load(f)

    # Define the database URL
    DATABASE_URL = f"mysql+pymysql://{db_info['username']}:{db_info['password']}@{db_info['hostname']}/{db_info['db_name']}"

    # Create a SQLAlchemy engine
    engine = create_engine(DATABASE_URL)

    # Create a SQLAlchemy ORM session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    return engine, SessionLocal

def populate_db():
    engine, SessionLocal = setup_engine_and_session()

    # Start a new session
    db = SessionLocal()

    # Read the CSV file
    try:
        df = pd.read_csv('Cereal.csv', sep=';', skiprows=[1])
    except pd.errors.ParserError:
        print("Error while reading the CSV file.")
        
    # Iterate over the rows of the DataFrame
    for index, row in df.iterrows():
        # Clean the 'rating' value
        rating = float(row['rating'].replace('.', '', 1))
        # Create a new Cereal object
        cereal = Cereal(
            name=row['name'],
            mfr=row['mfr'],
            type=row['type'],
            calories=row['calories'],
            protein=row['protein'],
            fat=row['fat'],
            sodium=row['sodium'],
            fiber=row['fiber'],
            carbo=row['carbo'],
            sugars=row['sugars'],
            potass=row['potass'],
            vitamins=row['vitamins'],
            shelf=row['shelf'],
            weight=row['weight'],
            cups=row['cups'],
            rating=rating  # Use the cleaned 'rating' value
        )

        # Add the Cereal object to the session
        db.add(cereal)

    # Commit the session
    db.commit()

    # Close the session
    db.close()

def init():
    # Load database information from db_info.json
    with open('db_info.json') as f:
        db_info = json.load(f)

    # Connect to the MySQL server (without specifying the database)
    connection = pymysql.connect(host=db_info['hostname'],
                                 user=db_info['username'],
                                 password=db_info['password'])

    try:
        with connection.cursor() as cursor:
            # Create databases (if they don't exist)
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_info['db_name']}")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_info['test_db_name']}")

        # Commit the changes
        connection.commit()
    finally:
        connection.close()

    engine, SessionLocal = setup_engine_and_session()
    
    populate_db()

    # Import your Base from db_classes
    from db_classes import Base
    # Create all tables in the database
    Base.metadata.create_all(bind=engine)


app = FastAPI()

origins = [
    "http://localhost:3000",  # React's default port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

init()

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)