from django.urls import path

from myapp.views import homepage, login_f, logout_user, predict_page, register

urlpatterns = [
    path('', login_f, name='login_f'),
    path('register', register, name='register'),
    path('home', homepage, name='homepage'),
    path('logout', logout_user, name='logout_user'),
    path('predict', predict_page, name='predict_page'),
]
