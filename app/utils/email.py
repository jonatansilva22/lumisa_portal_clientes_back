from pydantic import EmailStr, ValidationError


def is_valid_email(email: str) -> bool:
    #Verifica si ``email`` es una dirección de email válida según pydantic
    try:
        EmailStr.validate(email)
        return True
    except ValidationError:
        return False
