from django.contrib import admin
from projectGreen.models import User, Challenge, ActiveChallenge
from projectGreen.send_email import send_email

def get_user_emails():
    user_emails = []
    user_objects = User.objects.all()
    for user_info in user_objects:
        user_emails.append(user_info.email)
    return user_emails


@admin.action(description='Publish challenge')
def publish_challenge(modeladmin, request, queryset):
    # Sender, recipients and message subject
    from_email = "djangotestemail31@gmail.com"
    mailing_list = get_user_emails()
    challenge_description = queryset[0].description
    msg_subject = "New BeGreen challenge is out: " + challenge_description

    # Credentials
    username = 'djangotestemail31@gmail.com'  
    password = 'nrsrhztfmmwyqzey'

    # Send message
    send_email(from_email, username, password, mailing_list, msg_subject)


class UsersAdmin(admin.ModelAdmin):
    list_display = ['email', 'username', 'display_name', 'is_superuser']
    ordering = ['email']
    actions = []

class ChallengesAdmin(admin.ModelAdmin):
    list_display = ['challenge_id', 'description']
    ordering = ['challenge_id']
    actions = [publish_challenge]

class ActiveChallengesAdmin(admin.ModelAdmin):
    list_display = ['challenge_id', 'challenge_date', 'is_expired']
    ordering = ['challenge_id']
    actions = []

    

admin.site.register(Challenge, ChallengesAdmin)
admin.site.register(ActiveChallenge, ActiveChallengesAdmin)
