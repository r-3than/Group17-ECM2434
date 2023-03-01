from django.contrib import admin
from django.contrib.auth.models import User
from projectGreen.models import Profile, Challenge, ActiveChallenge, Submission, Upvote

#from projectGreen.send_email import send_email
from projectGreen.settings import EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
from datetime import datetime
from projectGreen.points import recalculate_user_points # correct version; import callbacks from here

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
        recalculate_user_points(user.username)

## callbacks to go here; i dont wanna do all this importing its a mess

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

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['username', 'challenge_date', 'minutes_late']
    ordering = ['username']
    actions = []

class UpvoteAdmin(admin.ModelAdmin):
    list_display = ['submission_username', 'submission_date', 'voter_username']
    ordering = ['submission_username']
    actions = []

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Challenge, ChallengesAdmin)
admin.site.register(ActiveChallenge, ActiveChallengesAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(Upvote, UpvoteAdmin)