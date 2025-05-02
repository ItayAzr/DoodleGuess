import jwt
import secrets
import dotenv
from dotenv import load_dotenv

def create_key():
    dotenv.set_key('key.env','SECRET_KEY', str(secrets.token_hex(32)))

def get_key():
    load_dotenv('key.env')
    return os.getenv('SECRET_KEY')

# generates token for the user
def generate_token(username):
    payload = {
        "user_id": username,
    }
    token = jwt.encode(payload, get_key(), algorithm="HS256")
    return token

def save_token(username, token):
    data = {
        username: token
    }
    with open('Tokens.json', 'w') as f:
        json.dump(data, f, indent=4)
