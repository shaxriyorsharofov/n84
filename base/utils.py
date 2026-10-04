import re
from rest_framework.exceptions import ValidationError

phone_regex = re.compile(r'^\+998\d{9}$')
email_regex = re.compile(r'^[a-zA-Z0-9_.%+-[ ]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
username_regex = re.compile(r"^[a-zA-Z0-9_.]{3,30}$")

def email_or_phone_regex(user_input):
    if re.fullmatch(phone_regex, user_input):
        return 'phone'
    
    elif re.fullmatch(email_regex, user_input):
        return 'email'
    
    
    raise ValidationError('Email yoki telefon raqam xato kiritdingiz')
    
    
def input_type(user_input):
    if re.fullmatch(phone_regex, user_input):
        return 'phone'
    
    elif re.fullmatch(email_regex, user_input):
        return 'email'
    
    elif re.fullmatch(username_regex, user_input):
        return 'username'
    
    
    raise ValidationError('Email yoki telefon raqam xato kiritdingiz')   



