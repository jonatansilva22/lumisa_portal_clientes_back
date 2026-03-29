from pydantic import BaseModel, EmailStr


class Login(BaseModel):
    email: EmailStr
    password: str



class Token(BaseModel):
    access_token: str


class UserResponse(BaseModel):
    id: int
    name: str
    last_name: str
    email: str
    image_url: str | None = None
    role_id: int
    company_id: int | None = None
    active: bool

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
