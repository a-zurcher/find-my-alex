from pydantic import BaseModel, Field, EmailStr


class UserSchema(BaseModel):
    username: str = Field()
    password: str = Field()
    email: EmailStr = Field()

    class Config:
        schema_extra = {
            "example": {
                "username": "username",
                "password": "password",
                "email": "email"
            }
        }


class UserLoginSchema(BaseModel):
    username: str = Field()
    password: str = Field()
    email: EmailStr = Field()

    class Config:
        schema_extra = {
            "example": {
                "username": "username",
                "password": "password",
                "email": "email"
            }
        }
