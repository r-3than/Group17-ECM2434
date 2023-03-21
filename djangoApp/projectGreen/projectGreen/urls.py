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
from projectGreen.views import *

urlpatterns = [
    # Pages:
    # Initial Process:
    path('', challenge),
    path('submit/', submit, name='submit'),
    
    # Feeds:
    path('home/', home, name='home'),
    path('friends-feed/',friends_feed, name='friends-feed'),
    
    # Account Management:
    path('history/', history, name='history'),
    path('friends/', friends, name='friends'),
    
    # Other:
    path('post/', post, name='post'),
    path('leaderboard/', leaderboard, name='leaderboard'),


    # Functions:
    # Posts:
    path('uploadphoto/', uploadphoto),
    path('like_submission/', like_submission),
    path('flag_submission/', flag_submission),

    # Comments:
    path('create-comment/', create_comment, name='create-comment'),
    path('flag_comment/', flag_comment),
    
    # Friends:
    path('addFriend/', addFriend, name='addFriend'),
    path('removeFriend/', removeFriend, name='removeFriend'),
    path('acceptFriendRequest/', acceptFriendRequest, name='acceptFriendRequest'),
    path('declineFriendRequest/', declineFriendRequest, name='declineFriendRequest'),

    # Accounts:
    path('deleteAccount/', deleteAccount, name='deleteAccount'),
    path('signout/', signout, name='signout'),

    # Emails:
    path('unsubscribe/', unsubscribeFromEmails, name='unsubscribe'),
    path('resubscribe/', resubscribeToEmails, name='resubscribe'),

    # Other:
    path('specific_group_access', specific_group_access, ),
    path('admin/', admin.site.urls),
    path('microsoft_authentication/', include('microsoft_authentication.urls')),
]
