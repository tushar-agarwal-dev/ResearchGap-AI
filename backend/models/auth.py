from pydantic import BaseModel, EmailStr


class AuthRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
