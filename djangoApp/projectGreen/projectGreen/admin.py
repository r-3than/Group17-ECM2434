from django.contrib import admin
from projectGreen.models import Challenge, ActiveChallenge
from projectGreen.send_email import send_email

@admin.action(description='Publish challenge')
def publish_challenge(modeladmin, request, queryset):
    # Sender, recipients and message subject
    from_email = "djangotestemail31@gmail.com"
    to_list = [
        "djangotestemail31@gmail.com",
        "grosdino2003@gmail.com",
        "emailtest4626@gmail.com"
    ]
    challenge_description = queryset[0].description
    msg_subject = "New challenge is out: " + challenge_description

    # Credentials
    username = 'djangotestemail31@gmail.com'  
    password = 'nrsrhztfmmwyqzey'

    # Send message
    send_email(from_email, username, password, to_list, msg_subject)
  

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
