from django.contrib import admin
from django.contrib.auth.models import User
from projectGreen.models import Profile, Challenge, ActiveChallenge
#from projectGreen.send_email import send_email
from projectGreen.settings import EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
from datetime import datetime

'''
def get_user_emails():
    user_emails = []
    user_objects = User.objects.all()
    for user_info in user_objects:
        user_emails.append(user_info.email)
    return user_emails
'''

@admin.action(description='Publish challenge')
def publish_challenge(modeladmin, request, queryset):
    date = datetime.now().strftime('%Y-%m-%d')
    try:
        ActiveChallenge.objects.get(challenge_date=date)
        print('Challenge has already been set today')
        return
    except ActiveChallenge.DoesNotExist:
        ac = ActiveChallenge(challenge_date=datetime.now(), challenge_id=queryset[0].challenge_id)
        ac.save()

    # Sender, recipients and message subject
    from_email = "djangotestemail31@gmail.com"

    # Credentials
    username = EMAIL_HOST_USER
    password = EMAIL_HOST_PASSWORD

    for user in User.objects.all():
        try:
            user.email_user('Time to BeGreen!','A new challenge has been posted! \n'+queryset[0].description+'\nDate: '+date, from_email)
        except:
            print("Message to ", user.email, "failed to send.")


@admin.action(description='Resynchronise Points')
def recalculate_points(modeladmin, request, queryset):
    for user in queryset:
        try:
            profile = Profile.objects.get(user=user)
            profile.points = 10
        except Profile.DoesNotExist:
            profile = Profile(user=user, points=10)
        profile.save()

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False

class UserAdmin(admin.ModelAdmin):
    inlines = [ ProfileInline ]
    list_display = ['email', 'username', 'is_superuser', 'get_points'] # 'display_name'
    ordering = ['email']
    actions = [recalculate_points]

    @admin.display(ordering='profile__points', description='Points')
    def get_points(self, user):
        return user.profile.points

class ChallengesAdmin(admin.ModelAdmin):
    list_display = ['challenge_id', 'description']
    ordering = ['challenge_id']
    actions = [publish_challenge]

class ActiveChallengesAdmin(admin.ModelAdmin):
    list_display = ['challenge_id', 'challenge_date', 'is_expired']
    ordering = ['challenge_id']
    actions = []

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Challenge, ChallengesAdmin)
admin.site.register(ActiveChallenge, ActiveChallengesAdmin)
