from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import SQLALCHEMY_DATABASE_URI
from models import User
from utils import logger, collector


engine = create_engine(SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

logs = logger.get_logger(__name__)
app = FastAPI()


@app.get('/')
@app.post('/')
async def get_root():
    return JSONResponse(content={"success": True, "msg": "Server is running"})


class UserAttributes(BaseModel):
    user_agent: str
    user_ip: str
    referrer: Optional[str] = None
    panel_clid: Optional[str] = None
    initiator: Optional[str] = None
    service_tag: Optional[str] = None


def save_user_to_db(user_data: dict):
    '''
    Save user to database.
    '''
    db = SessionLocal()
    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    logs.info(f"User saved with ID [{user.id}]")


@app.post('/save_user')
async def save_user(user_attributes: UserAttributes, request: Request):
    '''
    Generate user data from received and save it to database.
    '''
    logs.info(f"Received user data: {user_attributes}")
    user_data = collector.collect_parameters(user_attributes, request)
    save_user_to_db(user_data)
    
    return JSONResponse(
        content={
            "success": True, 
            "msg": "User saved successfully",
            "user_data": user_data
            }
        )


@app.get("/save_user")
@app.get("/search_user")
async def not_allowed_method():
    return JSONResponse(
        content={
            "success": False,
            "msg": "GET method not allowed. Use POST method instead.",
        },
        status_code=405,
    )


@app.get('/users')
@app.post('/users')
async def get_users():
    '''
    Get all users from database.
    '''
    db = SessionLocal()
    users = db.query(User).order_by(User.created_at.desc()).all()
    db.close()
    return JSONResponse(
        content={
            "success": True, 
            "users": [user.model_dump() for user in users]
            }
        )


@app.post('/search_user')
async def search_user(user_attributes: UserAttributes):
    '''
    Search user by unique_id generated from user data.
    '''
    logs.info(f"Searching user with data: {user_attributes}")
    search_key = collector.generate_search_key(user_attributes)
    if not search_key:
        return JSONResponse(
            content={
                "success": False, 
                "msg": "Error generating search key"
                },
            status_code=500
        )
    
    db = SessionLocal()
    user = db.query(User).filter(User.unique_id == search_key).order_by(User.created_at.desc()).first()
    db.close()
    
    if user:
        return JSONResponse(
            content={
                "success": True, 
                "user_data": user.model_dump()
                }
            )
    else:
        return JSONResponse(
            content={
                "success": False, 
                "msg": "User not found"
                },
            status_code=404
        )
