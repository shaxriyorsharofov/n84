from django.shortcuts import render
from .serializer import SignUpserializer, ChangeInfoSerializer, \
    LoginSerializer, ChangePhotoSerializer
from rest_framework.response import Response
from .models import CustomUser, Verify, NEW, CODE_VERIFY, VIA_EMAIL, VIA_PHONE
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework import permissions
from datetime import datetime
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
# Create your views here.


class SignUpView(CreateAPIView):
    serializer_class = SignUpserializer
    queryset = CustomUser.objects.all()
    
    
class VerifyCodeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        code = request.data.get('code')
        user = request.user
        
        current_code = user.codes.all().filter(code=code, used=False, expire_time__gte=datetime.now()).first()
        
        if current_code is None:
            raise ValidationError('Kod xato yoki eskirgan')

        if user.auth_status == NEW:
            current_code.used = True
            current_code.save()
            
            user.auth_status = CODE_VERIFY
            user.save()
                        
        return Response({
            'auth_status': user.auth_status,
            'msg': "code_verify"
        })
        
        
class GetNewCodeView(APIView):
    def get(self, request):
        user = request.user
        
        codes = user.codes.all().filter(used=False, expire_time__gte=datetime.now()).exists()
        
        if codes:
            raise ValidationError('Sizda hali activa kod bor')
        
        if user.auth_status == NEW:
            if user.auth_type == VIA_EMAIL:
                code = user.generate_code(user.auth_type)
                print(f'CODE EMAIL: {code} ===========================')

                #send_mail(user.email, code)
                
            elif user.auth_type == VIA_PHONE:
                code = user.generate_code(user.auth_type)
                print(f'CODE PHONE: {code} ===========================')
                #send_phone(user.phone_number, code)
        
            return Response({
                "msg": 'Code yuborildi',
                'auth_type': user.auth_type
            })
            
        return Response({
                    "msg": 'Siz oldin email yoki telefon raqam kiriting',
                })
        
        
class ChangeInfoView(UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangeInfoSerializer
    queryset = CustomUser.objects.all()
    
    def get_object(self):
        return self.request.user
    
    
class ChangePhotoView(UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangePhotoSerializer
    queryset = CustomUser.objects.all()
    parser_classes = [MultiPartParser, FormParser]
    
    def get_object(self):
        return self.request.user    

    
class TokenRefreshView(APIView):
    def get(self, request):
        refresh = request.data.get('refresh')
        try:
            refresh_token = RefreshToken(refresh)
        except:
            raise ValidationError('Token eskirgan yoki xato')
        
        return Response({
            'access': str(refresh_token.access_token)
        })
        
        
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        serialzier = LoginSerializer(data=request.data)
        serialzier.is_valid(raise_exception=True)
        return Response(serialzier.data)
        
        
    
class ProfileUpdateView():
    pass

class PasswordChangeView():
    pass

class LogoutView():
    pass

class ForgotPasswordView():
    pass

class ResetPasswordView():
    pass




