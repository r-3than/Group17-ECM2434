from django.contrib import admin
from django.contrib.auth.models import User
from projectGreen.models import Profile, Friend, Challenge, ActiveChallenge, Submission, Upvote
from datetime import datetime
from projectGreen.points import recalculate_user_points # correct version; import callbacks from here


@admin.action(description='Publish challenge')
def publish_challenge(modeladmin, request, queryset):
    date = datetime.now().strftime('%Y-%m-%d')
    try:
        ActiveChallenge.objects.get(date=date)
        print('Challenge has already been set today')
        return
    except ActiveChallenge.DoesNotExist:
        ac = ActiveChallenge(date=datetime.now(), challenge=queryset[0])
        ac.save()

    message = 'A new challenge has been posted! \n'+queryset[0].description+'\nDate: '+date

    for user in User.objects.all():
        try:
            user.email_user('Time to BeGreen!',message, 'djangotestemail31@gmail.com')
        except:
            print("Message to ", user.email, "failed to send.")


@admin.action(description='Resynchronise Points')
def recalculate_points(modeladmin, request, queryset):
    for user in queryset:
        Profile.recalculate_user_points(user.username)

@admin.action(description='Report Submission(s)')
def report_submission(modeladmin, request, queryset):
    for submission in queryset:
        submission.report_submission()

@admin.action(description='Approve Submission(s)')
def approve_submission(modeladmin, request, queryset):
    for submission in queryset:
        submission.review_submission(True)

    for user in User.objects.all():
        try:
            user.email_user('Time to BeGreen!','A new challenge has been posted! \n'+queryset[0].description+'\nDate: '+date, from_email)
        except:
            print("Message to ", user.email, "failed to send.")


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False

class UserAdmin(admin.ModelAdmin):
    inlines = [ ProfileInline ]
    list_display = ['email', 'username', 'is_superuser', 'get_points', 'get_friends']
    ordering = ['email']
    actions = [recalculate_points]

    @admin.display(ordering='profile__points', description='Points')
    def get_points(self, user):
        return user.profile.points
    
    @admin.display(ordering='', description='Friends')
    def get_friends(self, user):
        return Friend.get_friend_usernames(user.username)

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
    list_display = ['username', 'get_challenge_date', 'submission_time', 'get_minutes_late', 'get_submission']
    ordering = ['username']
    actions = [report_submission, approve_submission, deny_submission]

    @admin.display(ordering='challenge__challenge_date', description='challenge_date')
    def get_challenge_date(self, submission):
        return submission.active_challenge.date
    
    @admin.display(description='minuites_late')
    def get_minutes_late(self, submission):
        return submission.get_minutes_late()
    
    @admin.display(description='Photo')
    def get_submission(self, submission):
        if submission.photo_bytes != None:
            return 'data:image/png;base64,${decoded}'.format(decoded=submission.photo_bytes.decode)
        else:
            return '[no image found]'

class UpvoteAdmin(admin.ModelAdmin):
    list_display = ['get_submission', 'voter_username']
    ordering = ['voter_username']
    actions = []

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['username', 'get_challenge_date', 'minutes_late']
    ordering = ['username']
    actions = []

    @admin.display(ordering='challenge__challenge_date', description='challenge_date')
    def get_challenge_date(self, submission):
        return submission.challenge.challenge_date

class UpvoteAdmin(admin.ModelAdmin):
    list_display = ['get_submission_username', 'get_submission_date', 'voter_username']
    ordering = ['voter_username'] # get_submission_username
    actions = []

    @admin.display(ordering='submission__submission_username', description='submission_username')
    def get_submission_username(self, upvote):
        return upvote.submission.username
    
    @admin.display(ordering='submission__submission_date', description='submission_date')
    def get_submission_date(self, upvote):
        return upvote.submission.challenge_date

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Challenge, ChallengesAdmin)
admin.site.register(ActiveChallenge, ActiveChallengesAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(Upvote, UpvoteAdmin)
admin.site.register(Friend)