"""projectGreen URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from projectGreen.views import flag_submission, home,challenge, like_submission,submit,uploadphoto, specific_group_access

urlpatterns = [
    path('', challenge, ),
    path('home/', home, name='home'),
    path('submit/',submit,name="camera"),
    path('uploadphoto/',uploadphoto),
    path('like_submission/',like_submission),
    path('flag_submission/',flag_submission),
    path('specific_group_access', specific_group_access, ),
    path('admin/', admin.site.urls),
    path('microsoft_authentication/', include('microsoft_authentication.urls')),
    
]
