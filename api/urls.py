from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from api import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register('user', views.UserViewset)

urlpatterns = [
    url('auth/', include('rest_auth.urls')),
    url('auth/registration/', include('rest_auth.registration.urls'))
] + router.urls