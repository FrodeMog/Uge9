import json
import pandas as pd
import pymysql
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_classes import *

class DatabaseUtils:

    def __init__(self):
        # Load database information from db_info.json
        with open('db_info.json') as f:
            db_info = json.load(f)

        # Define the database URL
        DATABASE_URL = f"mysql+pymysql://{db_info['username']}:{db_info['password']}@{db_info['hostname']}/{db_info['db_name']}"

        # Create a SQLAlchemy engine
        engine = create_engine(DATABASE_URL)

        # Create a SQLAlchemy ORM session factory
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        self.engine = engine
        self.SessionLocal = SessionLocal

    def setup_db(self):
        self.clean_db()
        self.create_schemas_and_tables()
        self.populate_db()

    def populate_db(self):
        db = self.SessionLocal()

        # Read the CSV file
        try:
            df = pd.read_csv('Cereal.csv', sep=';', skiprows=[1])
        except pd.errors.ParserError:
            print("Error while reading the CSV file.")

        # Clean the data. ratings has 2 decimal points, we just take first number
        df['rating'] = df['rating'].apply(lambda x: float(x.split('.')[0]))

        # Insert the data into the database
        db.bulk_insert_mappings(Cereal, df.to_dict('records'))
        db.commit()
        db.close()

    def clean_db(self):
        from db_classes import Base
        Base.metadata.drop_all(bind=self.engine)

    def create_schemas_and_tables(self):
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

        from db_classes import Base
        # Create all tables in the database
        Base.metadata.create_all(bind=self.engine)