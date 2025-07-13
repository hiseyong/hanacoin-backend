from pydantic import BaseModel

class SignupRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class SignupResponse(BaseModel):
    msg: str
    private_key: str
    wallet_address: str
    wallet_public_key: str

class LoginResponse(BaseModel):
    msg: str
    access_token: str
    token_type: str

class UserInfoResponse(BaseModel):
    id: int
    username: str
    wallet_address: str
    wallet_public_key: str