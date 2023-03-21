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

from projectGreen import views

urlpatterns = [
    # Pages:
    # Initial Process:
    path('', views.challenge),
    path('submit/', views.submit, name='submit'),

    # Feeds:
    path('university-feed/', views.university_feed, name='university-feed'),
    path('friends-feed/', views.friends_feed, name='friends-feed'),

    # Account Management:
    path('history/', views.history, name='history'),
    path('friends/', views.friends, name='friends'),

    # Other:
    path('post/', views.post, name='post'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),


    # Functions:
    # Posts:
    path('uploadphoto/', views.upload_photo),
    path('like_submission/', views.like_submission),
    path('flag_submission/', views.flag_submission),

    # Comments:
    path('create-comment/', views.create_comment, name='create-comment'),
    path('flag_comment/', views.flag_comment),

    # Friends:
    path('addFriend/', views.add_friend, name='addFriend'),
    path('removeFriend/', views.remove_friend, name='removeFriend'),
    path('acceptFriendRequest/', views.accept_friend_request, name='acceptFriendRequest'),
    path('declineFriendRequest/', views.decline_friend_request, name='declineFriendRequest'),

    # Accounts:
    path('deleteAccount/', views.delete_account, name='deleteAccount'),
    path('signout/', views.signout, name='signout'),

    # Emails:
    path('unsubscribe/', views.unsubscribe_from_emails, name='unsubscribe'),
    path('resubscribe/', views.resubscribe_to_emails, name='resubscribe'),

    # Other:
    path('specific_group_access', views.specific_group_access, ),
    path('admin/', admin.site.urls),
    path('microsoft_authentication/', include('microsoft_authentication.urls')),
]
