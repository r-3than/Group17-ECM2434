from django.contrib import admin
from django.contrib.auth.models import User
from projectGreen.models import Profile, Challenge, ActiveChallenge, Submission, Upvote

#from projectGreen.send_email import send_email
from projectGreen.settings import EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
from datetime import datetime
from projectGreen.points import recalculate_user_points # correct version; import callbacks from here

@admin.action(description='Publish challenge')
def publish_challenge(modeladmin, request, queryset):
    date = datetime.now().strftime('%Y-%m-%d')
    try:
        ActiveChallenge.objects.get(challenge_date=date)
        print('Challenge has already been set today')
        return
    except ActiveChallenge.DoesNotExist:
        ac = ActiveChallenge(challenge_date=datetime.now(), challenge=queryset[0])
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
    list_display = ['id', 'description']
    ordering = ['id']
    actions = [publish_challenge]

class ActiveChallengesAdmin(admin.ModelAdmin):
    list_display = ['date', 'get_challenge_id', 'get_challenge_description', 'get_time_for_challenge', 'is_expired']
    ordering = ['date']
    actions = []

    @admin.display(ordering='challenge__id', description='challenge_id')
    def get_challenge_id(self, active_challenge):
        return active_challenge.challenge.id
    
    @admin.display(ordering='challenge__description', description='description')
    def get_challenge_description(self, active_challenge):
        return active_challenge.challenge.description
    
    @admin.display(ordering='challenge__time_for_challenge', description='time_for_challenge')
    def get_time_for_challenge(self, active_challenge):
        return active_challenge.challenge.time_for_challenge


class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['username', 'get_challenge_date', 'minutes_late']
    ordering = ['username']
    actions = []

    @admin.display(ordering='challenge__challenge_date', description='challenge_date')
    def get_challenge_date(self, submission):
        return submission.active_challenge.date

class UpvoteAdmin(admin.ModelAdmin):
    list_display = ['get_submission', 'voter_username']
    ordering = ['voter_username'] # get_submission_username
    actions = []

    @admin.display(ordering='submission__submission', description='submission')
    def get_submission(self, upvote):
        return upvote.submission

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Challenge, ChallengesAdmin)
admin.site.register(ActiveChallenge, ActiveChallengesAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(Upvote, UpvoteAdmin)