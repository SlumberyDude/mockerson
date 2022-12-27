from fastapi import FastAPI, Depends, APIRouter, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import bcrypt
import jwt

from config import JWT_SECRET

from models import User
from db import users_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')
# subapi = APIRouter()

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/add_item/{item_id}")
def add_item(item_id: int):
    return {"item_id": item_id}

# @subapi.get('')
# async def subapi_get(request: Request):
#     return {'i_am': request.url.path}

# @app.post('/register_endpoint', response_model=User)
# async def register_endpoint():
#     ...

async def authentificate_user(username: str, password: str):
    user = users_db.get(username.lower()) # lower username is my key
    if user is None:
        return False
    print('user from db hash: ', user['password_hash'])
    if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        return False
    return user

@app.post('/token')
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # verify that the from_data is correct
    # form_data is gonna be the username and password
    user = await authentificate_user(form_data.username, form_data.password)

    if not user:
        return {'error': 'invalid creditnails'}

    print('got user in the form of ', type(user))
    token = jwt.encode(user, JWT_SECRET)
    return {'access_token': token, 'token_type': 'bearer'}
    

@app.post('/register_user')
async def register_user(input_user: User):
    # look for the user in database
    item = users_db.get(input_user.username.lower())
    if item is None:
        hash_pass = bcrypt.hashpw(input_user.password_hash.encode('utf-8'), bcrypt.gensalt())
        u = User(
            username=input_user.username,
            password_hash=hash_pass
        )
        users_db.put(data=u.dict(), key=u.username.lower(), expire_in=300)
        return {'Message': 'Registration success. Welcome, {}!'\
            .format(input_user.username)}
    else:
        return {'Message': 'Registration Failed. The user {} is already exists.'\
            .format(input_user.username)}

@app.post('/login')
async def login_user():
    ...