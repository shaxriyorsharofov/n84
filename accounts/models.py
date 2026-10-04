from django.db import models
from base.models import BaseModel
from django.contrib.auth.models import AbstractUser
from datetime import datetime, timedelta
from shop.settings import EMAIL_EXPIRATION_TIME, PHONE_EXPIRATION_TIME
import uuid
import random
from rest_framework_simplejwt.tokens import RefreshToken
# Create your models here.


NEW, CODE_VERIFY, DONE, PHOTO_DONE = ('new', 'code_verify', 'done', 'photo_done')
VIA_EMAIL, VIA_PHONE  = ('via_email', 'via_phone')
CUSTOMER, SELLER = ('customer', 'seller')

class CustomUser(BaseModel, AbstractUser):
    
    USER_ROLE = (
        (CUSTOMER, CUSTOMER),
        (SELLER, SELLER)
    )
    AUTH_TYPE = (
        (VIA_EMAIL, VIA_EMAIL),
        (VIA_PHONE, VIA_PHONE)
    )
    AUTH_STATUS = (
        (NEW, NEW),
        (CODE_VERIFY, CODE_VERIFY),
        (DONE, DONE),
        (PHOTO_DONE, PHOTO_DONE)
    )
    
    user_role = models.CharField(max_length=120, choices=USER_ROLE, default=CUSTOMER)
    auth_type = models.CharField(max_length=120, choices=AUTH_TYPE)
    auth_status = models.CharField(max_length=120, choices=AUTH_STATUS, default=NEW)
    phone_number = models.CharField(max_length=13, unique=True, null=True, blank=True)
    email = models.EmailField(max_length=133, unique=True, null=True, blank=True)
    photo = models.ImageField(upload_to='accounts/', blank=True, null=True)
    
    
    def generate_code(self, verify_type):
        
        code = random.randint(1000, 9999)
        
        Verify.objects.create(
            code=code,
            verify_type=verify_type,
            user=self
        )
        
        return code
        
        
        

    def check_username(self):
        if not self.username:
            ud = str(uuid.uuid4())
            temp_username = 'username' + ud[int(ud.rfind('-')) + 1 : ]
            while CustomUser.objects.filter(username=temp_username).exists():
                temp_username += str(random.randint(0, 10))
            self.username = temp_username
        
    def check__password(self):
        if not self.password:
            ud = str(uuid.uuid4())
            temp_password = 'password' + ud[int(ud.rfind('-')) + 1 : ]
            self.password = temp_password  
        
    def check_hashing_pass(self):
        if not self.password.startswith('pbkdf2_sha256'):
            self.set_password(self.password)
        
    def check_email_normalize(self):
        if self.email:
            temp_email = self.email.lower()
            self.email = temp_email
            
    def token(self):
        refresh_token =  RefreshToken.for_user(self)
        
        return {
            'refresh_token': str(refresh_token),
            'access_token': str(refresh_token.access_token)
        }
        
    
    def save(self, *args, **kwargs):
        self.check_username()
        self.check__password()
        self.check_hashing_pass()
        self.check_email_normalize()
        
        super().save(*args, **kwargs)
    
    

class Verify(BaseModel):
    VERIFY_TYPE = (
        (VIA_EMAIL, VIA_EMAIL),
        (VIA_PHONE, VIA_PHONE)
    )
    verify_type = models.CharField(max_length=120, choices=VERIFY_TYPE)
    code = models.CharField(max_length=4)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='codes')
    expire_time = models.DateTimeField()
    used = models.BooleanField(default=False)
    
    def __str__(self):
        return f"code: {self.code} | user: {self.user.username}"
    
    def save(self, *args, **kwargs):
        if self.verify_type == VIA_EMAIL:
            self.expire_time = datetime.now() + timedelta(minutes=EMAIL_EXPIRATION_TIME)# 12:50 12:53
        else:
            self.expire_time = datetime.now() + timedelta(minutes=PHONE_EXPIRATION_TIME)#12;50 12;52
            
        super().save(*args, **kwargs)
        
    
    
    
     