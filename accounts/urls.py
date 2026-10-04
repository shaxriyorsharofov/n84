from django.urls import path
from .views import SignUpView, VerifyCodeView, GetNewCodeView, ChangeInfoView,\
    TokenRefreshView,ChangePhotoView, LoginView
urlpatterns = [
    path('signup/', SignUpView.as_view()),
    path('verify/', VerifyCodeView.as_view()),
    path('new-code/', GetNewCodeView.as_view()),
    path('change-info/', ChangeInfoView.as_view()),
    path('change-image/', ChangePhotoView.as_view()),
    path('token-refresh/', TokenRefreshView.as_view()),
    path('login/', LoginView.as_view()),
]
