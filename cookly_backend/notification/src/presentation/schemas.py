from pydantic import BaseModel


class EmailConfirmationSchema(BaseModel):
    email: str
    email_confirmation_token: str
