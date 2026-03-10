import re


def password_strength(password: str) -> bool:
    #Validador simple de fuerza de contraseña.

    #Requiere al menos 8 caracteres y al menos un dígito.
    
    if len(password) < 8:
        return False
    if not re.search(r"\d", password):
        return False
    return True
