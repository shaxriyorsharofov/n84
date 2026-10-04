from rest_framework import serializers
from .models import CustomUser, Verify, VIA_EMAIL, VIA_PHONE, CODE_VERIFY, DONE,\
    PHOTO_DONE, NEW
from rest_framework.exceptions import ValidationError
from base.utils import email_or_phone_regex, input_type
from django.contrib.auth import authenticate
from django.db.models import Q
from datetime import datetime


class SignUpserializer(serializers.ModelSerializer):
    
    phone_number_email = serializers.CharField(required=True, write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['id', 'auth_status', 'auth_type', 'phone_number_email']
        read_only_fields = fields
        
    
    def validate(self, attrs):
        phone_number_email = attrs.get('phone_number_email')        
        
        phone_number_or_email = email_or_phone_regex(phone_number_email)
        
        if phone_number_or_email == 'email':
            data = {
                'email': phone_number_email,
                'auth_type': VIA_EMAIL
            }
            
        elif phone_number_or_email == 'phone':
            data = {
                    'phone_number': phone_number_email,
                    'auth_type': VIA_PHONE
                    }
            
        else: 
            raise ValidationError('Telefon yoki email xato (s)')
        
        user = CustomUser.objects.filter(Q(email=phone_number_email) | Q(phone_number=phone_number_email)).first()


        if user and user.auth_status in [NEW, CODE_VERIFY]:
            self.check_limit(user)
            user.delete()
            

        return data #={'email': 'wqefqewfgqegqerg', 'auth_type': 'email'}
        

    def check_limit(self, user):
        code = user.codes.all().filter(used=False, expire_time__gte = datetime.now()).exists()
        if code:
            raise ValidationError("Sizda hali aktiva kod bor shudan foydalaning")
        
        return True
        

    def create(self, validated_data):
        print(validated_data, '=========================')
        user = CustomUser(**validated_data)
        user.save()
         
        if validated_data['auth_type'] == VIA_EMAIL:
            code = user.generate_code(validated_data['auth_type'])
            print(f'CODE EMAIL: {code} ===========================')
            # send_code(validated_data['email'], code)
            
        elif validated_data['auth_type'] == VIA_PHONE:
            code = user.generate_code(validated_data['auth_type'])
            print(f'CODE PHONE: {code} ===========================')
            # send_code(validated_data['email'], code)
        
        else:
            raise ValidationError('EMail yoki telefon raqam xato')
            
        return user
    
    
    def to_representation(self, instance):
        
        token = instance.token()
        data = super().to_representation(instance)
        return {
            'data': data,
            'token': token
        }
        
        
class ChangeInfoSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'password', 'confirm_password']
        required_fields = ['first_name', 'last_name', 'username', 'password', 'confirm_password']
        
        
    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        
        if password != confirm_password:
            raise ValidationError('parollar mos emas')
        
        return attrs
    
    
    def update(self, instance, validated_data):
        
        if instance.auth_status == CODE_VERIFY:
        
            instance.first_name = validated_data['first_name']
            instance.last_name = validated_data['last_name']
            instance.username = validated_data['username']
            instance.password = instance.set_password(validated_data['password'])
            instance.auth_status = DONE

            return super().update(instance, validated_data)
        raise ValidationError('Akkountingizni tasdiqlashingiz kerak')
    

class ChangePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['photo']

    def update(self, instance, validated_data):
        # 1. Holatni tekshirish
        if instance.auth_status != DONE:
            raise ValidationError({'detail': "To'liq ro'yxatdan o'tmagansiz"})

        photo = validated_data.get('photo')
        if photo:
            instance.photo = photo
            instance.auth_status = PHOTO_DONE
            instance.save()
            return instance

        return super().update(instance, validated_data)    
                    
            
class LoginSerializer(serializers.Serializer):
    user_input = serializers.CharField(required = True)
    password = serializers.CharField(write_only = True)
    
    def validate(self, data):
        user_input = data.get('user_input')
        password = data.get('password')
        user = self.get_object(user_input)
        
        if user.auth_status in [NEW, CODE_VERIFY]:
            raise ValidationError('Siz toliq royxatdan otmagansiz')
        
        
        current_user = authenticate(username=user.username, password=password)
        
        if current_user is None:
            raise ValidationError('Login yoki parol xato')
        
        data['user'] = current_user
        
        return data
       
        
        
    def get_object(self, user_input):
        user_input_type = input_type(user_input)
        if user_input_type == 'username':
            user = CustomUser.objects.filter(username=user_input).first()
        elif user_input_type == 'email':
            user = CustomUser.objects.filter(email=user_input).first()
        elif user_input_type == 'phone':
            user = CustomUser.objects.filter(phone_number=user_input)
            
        else:
            raise ValidationError('Login xato')
        
        
        return user
    
    
    def to_representation(self, instance):

        user = instance['user']
        
        return {
            'token': user.token()
        }
        
        
        
    
#909998877
#998909998877
#+998909998877