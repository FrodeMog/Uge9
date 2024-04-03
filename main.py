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
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import pandas as pd
from sqlalchemy.orm import Session
from db_classes import Cereal 
import pymysql
from db_connect import DatabaseConnect
from db_utils import DatabaseUtils
#uvicorn main:app --reload
#npx create-react-app storage-app
#http://localhost:8000/docs

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

async def get_db():
    db_connect = await DatabaseConnect.connect_from_config()
    session = await db_connect.get_new_session()
    try:
        yield session
    finally:
        await db_connect.close()

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.get("/cereals", response_model=List[CerealBase])
async def read_cereals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    cereals = await Cereal.get_all(db)
    return cereals

db_utils = DatabaseUtils()
db_utils.setup_db()

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)