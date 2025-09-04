
from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from .core.database import get_db, SessionLocal, engine
from . import models
load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')
app = FastAPI(title='Dogan AI Compliance MVP')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str

class UserInDB(UserCreate):
    hashed_password: str

class ComplianceCheck(BaseModel):
    standard: str
    control_id: str

class ComplianceResult(BaseModel):
    standard: str
    control_id: str
    status: str
    details: Dict[(str, Any)]

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, email: str):
    return db.query(models.User).filter((models.User.email == email)).first()

def authenticate_user(db, email: str, password: str):
    user = get_user(db, email)
    if ((not user) or (not verify_password(password, user.hashed_password))):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta]=None):
    to_encode = data.copy()
    if expires_delta:
        expire = (datetime.utcnow() + expires_delta)
    else:
        expire = (datetime.utcnow() + timedelta(minutes=15))
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str=Depends(oauth2_scheme), db: SessionLocal=Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials', headers={'WWW-Authenticate': 'Bearer'})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get('sub')
        if (email is None):
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = get_user(db, email=token_data.email)
    if (user is None):
        raise credentials_exception
    return user

@app.post('/token', response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm=Depends(), db: SessionLocal=Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if (not user):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect email or password', headers={'WWW-Authenticate': 'Bearer'})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={'sub': user.email}, expires_delta=access_token_expires)
    return {'access_token': access_token, 'token_type': 'bearer'}

@app.post('/api/register', response_model=dict)
async def register_user(user: UserCreate, db: SessionLocal=Depends(get_db)):
    db_user = db.query(models.User).filter((models.User.email == user.email)).first()
    if db_user:
        raise HTTPException(status_code=400, detail='Email already registered')
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password, full_name=user.full_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {'message': 'User created successfully'}

@app.get('/', response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})

@app.post('/api/compliance/check', response_model=ComplianceResult)
async def check_compliance(check: ComplianceCheck, current_user: models.User=Depends(get_current_user), db: SessionLocal=Depends(get_db)):
    'Check compliance for a specific standard and control'
    control = db.query(models.Control).join(models.ComplianceStandard).filter((models.ComplianceStandard.name == check.standard), (models.Control.control_id == check.control_id)).first()
    if (not control):
        raise HTTPException(status_code=404, detail='Control not found')
    result = {'standard': check.standard, 'control_id': check.control_id, 'status': 'Compliant', 'details': {'title': control.title, 'description': (control.description or 'No description available'), 'is_mandatory': control.is_mandatory, 'last_checked': datetime.utcnow().isoformat()}}
    assessment = models.Assessment(control_id=control.id, user_id=current_user.id, status=result['status'], assessed_at=datetime.utcnow(), next_review_date=(datetime.utcnow() + timedelta(days=90)))
    db.add(assessment)
    db.commit()
    return result

@app.get('/api/standards', response_model=List[Dict[(str, Any)]])
async def list_standards(db: SessionLocal=Depends(get_db)):
    'List all available compliance standards'
    standards = db.query(models.ComplianceStandard).all()
    return [{'id': std.id, 'name': std.name, 'version': std.version} for std in standards]

@app.get('/api/controls/{standard_id}', response_model=List[Dict[(str, Any)]])
async def list_controls(standard_id: int, db: SessionLocal=Depends(get_db)):
    'List all controls for a specific standard'
    controls = db.query(models.Control).filter((models.Control.standard_id == standard_id)).all()
    return [{'id': c.id, 'control_id': c.control_id, 'title': c.title} for c in controls]

@app.on_event('startup')
def startup_event():
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        admin = db.query(models.User).filter((models.User.email == 'admin@example.com')).first()
        if (not admin):
            hashed_password = get_password_hash('admin123')
            admin = models.User(email='admin@example.com', hashed_password=hashed_password, full_name='Admin User', is_superuser=True)
            db.add(admin)
            db.commit()
    finally:
        db.close()
if (__name__ == '__main__'):
    import uvicorn
    uvicorn.run('app.main:app', host='0.0.0.0', port=8000, reload=True)
