from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from db_pydantic_classes import *
from db_classes import *
from typing import List
import uvicorn
from sqlalchemy.ext.asyncio import AsyncSession
from db_classes import Cereal 
from db_connect import DatabaseConnect
from db_utils import DatabaseUtils
from typing import List
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
async def get_cereals(session: AsyncSession = Depends(get_db)):
    cereals = await Cereal.get_all(session)
    return [CerealBase.from_orm(cereal) for cereal in cereals]

@app.get("/cereals/{cereal_id}", response_model=CerealBase)
async def get_cereal_by_id(cereal_id: int, session: AsyncSession = Depends(get_db)):
    cereal = await Cereal.get_by_id(session, cereal_id)
    if cereal is None:
        raise HTTPException(status_code=404, detail="Cereal not found")
    return CerealBase.from_orm(cereal)

@app.get("/cereals/{field}/{value}", response_model=List[CerealBase])
async def get_cereal_by_field_value(field: str, value: str, comparison: Optional[str] = 'eq', session: AsyncSession = Depends(get_db)):
    cereals = await Cereal.get_by_field_value(session, field, value, comparison)
    if not cereals:
        raise HTTPException(status_code=404, detail="Cereal not found")
    return [CerealBase.from_orm(cereal) for cereal in cereals]

db_utils = DatabaseUtils()
db_utils.setup_db()

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)