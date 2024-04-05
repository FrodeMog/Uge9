from fastapi import FastAPI, HTTPException, status, Depends, Security, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, APIKeyHeader
from fastapi.staticfiles import StaticFiles

from db_pydantic_classes import *
from db_classes import *
from db_connect import DatabaseConnect
from db_utils import DatabaseUtils

from sqlalchemy.ext.asyncio import AsyncSession

from jose import JWTError, jwt
from passlib.context import CryptContext

from datetime import datetime, timedelta
import json
from typing import List, Dict, Tuple, Any, Optional
import os

import uvicorn
#uvicorn main:app --reload
#npx create-react-app storage-app
#http://localhost:8000/docs

with open('jwt_info.json') as f:
    jwt_info = json.load(f)

SECRET_KEY = jwt_info['secret_key']
ALGORITHM = jwt_info['algorithm']
ACCESS_TOKEN_EXPIRE_MINUTES = jwt_info['access_token_expire_minutes']

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
API_KEY_NAME = "User_Authentication"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)


app = FastAPI()
app.mount("/cereal-pictures", StaticFiles(directory="Cereal Pictures"), name="cereal-pictures")

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

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_db)):
    user = await User.authenticate(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "is_admin": user.is_admin}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = (await session.execute(select(User).where(User.username == token_data.username))).scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user

async def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="User is not an admin")
    return current_user

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.get("/cereals/{id}/picture")
async def get_cereal_picture(id: int, response_type: str = "redirect", session: AsyncSession = Depends(get_db)):
    cereal = await Cereal.get_by_id(session, id)
    if cereal is None:
        raise HTTPException(status_code=404, detail="Cereal not found")

    # Remove spaces from the cereal name
    cereal_name_no_spaces = cereal.name.replace(" ", "")

    # Check all files in the directory
    for filename in os.listdir("Cereal Pictures"):
        # Remove spaces from the filename and compare with the cereal name
        if filename.replace(" ", "").startswith(cereal_name_no_spaces):
            if response_type.lower() == "redirect":
                url_filename = filename.replace(" ", "%20")
                return RedirectResponse(url=f"/cereal-pictures/{url_filename}")
            elif response_type.lower() == "file":
                return FileResponse(path=f"Cereal Pictures/{filename}", filename=filename)
            else:
                raise HTTPException(status_code=400, detail="Invalid response_type. Available types are 'redirect' and 'file'.")

    raise HTTPException(status_code=404, detail="Cereal picture not found")

@app.get("/cereals", response_model=List[CerealInDB])
async def get_cereals(session: AsyncSession = Depends(get_db)):
    result = await Cereal.get_all(session)
    if result:
        return [CerealInDB.from_orm(cereal) for cereal in result]
    else:
        raise HTTPException(status_code=500, detail="Operation failed: Unknown error")

@app.get("/cereals/{id}", response_model=CerealInDB)
async def get_cereal_by_id(id: int, session: AsyncSession = Depends(get_db)):
    cereal = await Cereal.get_by_id(session, id)
    if cereal:
        return CerealInDB.from_orm(cereal)
    else:
        raise HTTPException(status_code=500, detail="Operation failed: Unknown error")

@app.get("/cereals/sorted/{field}", response_model=List[CerealInDB])
async def get_cereal_by_field_sorted(field: str, order: Optional[str] = 'asc', session: AsyncSession = Depends(get_db)):
    result = await Cereal.get_by_field_sorted(session, field, order)
    if result:
        return [CerealInDB.from_orm(cereal) for cereal in result]
    else:
        raise HTTPException(status_code=500, detail="Operation failed: Unknown error")

@app.get("/cereals/{field}/{value}", response_model=List[CerealInDB])
async def get_cereal_by_field_value(field: str, value: str, comparison: Optional[str] = 'eq', order: Optional[str] = 'asc', session: AsyncSession = Depends(get_db)):
    result = await Cereal.get_by_field_value(session, field, value, comparison, order)
    if result:
        return [CerealInDB.from_orm(cereal) for cereal in result]
    else:
        raise HTTPException(status_code=500, detail="Operation failed: Unknown error")

@app.post("/cereals/filter", response_model=List[CerealInDB])
async def get_cereal_by_filters(
    filter: FilterExample = Body(...),
    session: AsyncSession = Depends(get_db)
):
    result = await Cereal.get_by_filters(session, filter.filters, filter.order)
    if result:
        return [CerealInDB.from_orm(cereal) for cereal in result]
    else:
        raise HTTPException(status_code=500, detail="Operation failed: Unknown error")

@app.post("/cereals", response_model=CerealInDB)
async def upsert_cereal(cereal: CerealBase, current_user: User = Depends(get_current_admin_user), id: Optional[int] = None, session: AsyncSession = Depends(get_db)):
    result = await Cereal.upsert(session=session, id=id, **cereal.dict())
    if result:
        return CerealInDB.from_orm(result)
    else:
        raise HTTPException(status_code=500, detail="Operation failed: Unknown error")
    
@app.delete("/cereals/{id}")
async def delete_cereal(id: int, current_user: User = Depends(get_current_admin_user), session: AsyncSession = Depends(get_db)):
    await Cereal.delete(session, id)
    return {"message": f"Cereal with id {id} deleted successfully"}

db_utils = DatabaseUtils()
db_utils.setup_db()

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)