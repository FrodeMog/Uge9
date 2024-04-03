from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys
sys.path.append("database")
from db_pydantic_classes import *
from db_classes import *
from typing import List, Annotated
import uvicorn
from werkzeug.security import check_password_hash
#uvicorn main:app --reload
#npx create-react-app storage-app
#http://localhost:8000/docs