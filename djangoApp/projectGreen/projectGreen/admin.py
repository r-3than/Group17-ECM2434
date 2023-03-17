
'''
Main Author:
    TN - Full admin views
Sub-Author:
    LB - Initial Challenge model view; code review
'''
import base64
from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.html import format_html
from projectGreen.models import Profile, Friend, Challenge, ActiveChallenge, Submission, Upvote, Comment
from datetime import datetime
import logging

LOGGER = logging.getLogger('django')

@admin.action(description='Publish challenge')
def publish_challenge(modeladmin, request, queryset):
    date = datetime.now().strftime('%Y-%m-%d')
    try:
        ActiveChallenge.objects.get(date=date)
        print('Challenge has already been set today')
        return
    except ActiveChallenge.DoesNotExist:
        ActiveChallenge.objects.all().is_expired = True
        ac = ActiveChallenge(date=datetime.now(), challenge=queryset[0])
        ac.save()

    message = 'A new challenge has been posted! \n'+queryset[0].description+'\nDate: '+date

    for user in User.objects.all():
        try:
            user.email_user('Time to BeGreen!',message, 'djangotestemail31@gmail.com')
        except:
            LOGGER.error("Message to ", user.email, "failed to send.")


@admin.action(description='Resynchronise Points')
def recalculate_points(modeladmin, request, queryset):
    for user in queryset:
        Profile.recalculate_user_points_by_username(user.username)

@admin.action(description='Resynchronise Points')
def recalculate_points_from_profile(modeladmin, request, queryset):
    for profile in queryset:
        profile.recalculate_user_points()

@admin.action(description='Report Submission(s)')
def report_submission(modeladmin, request, queryset):
    for submission in queryset:
        submission.report_submission()

@admin.action(description='Approve Submission(s)')
def approve_submission(modeladmin, request, queryset):
    for submission in queryset:
        submission.review_submission(True)

@admin.action(description='Remove Submission(s)')
def deny_submission(modeladmin, request, queryset):
    for submission in queryset:
        submission.review_submission(False)

@admin.action(description='Report Comment(s)')
def report_comment(modeladmin, request, queryset):
    for comment in queryset:
        comment.report_comment()

@admin.action(description='Approve Comment(s)')
def approve_comment(modeladmin, request, queryset):
    for comment in queryset:
        comment.review_comment(True)

@admin.action(description='Remove Comment(s)')
def deny_comment(modeladmin, request, queryset):
    for comment in queryset:
        comment.review_comment(False)

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False

class UserAdmin(admin.ModelAdmin):
    inlines = [ ProfileInline ]
    list_display = ['email', 'username', 'is_superuser', 'get_points', 'get_friends']
    ordering = ['email']
    actions = [recalculate_points]

    @admin.display(ordering='profile__points', description='Points')
    def get_points(self, user) -> int:
        return user.profile.points
    
    @admin.display(ordering='', description='Friends')
    def get_friends(self, user) -> list[str]:
        return Friend.get_friend_usernames(user.username)
    
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['get_username', 'points', 'number_of_submissions_removed', 'number_of_comments_removed', 'number_of_false_reports']
    ordering = ['number_of_submissions_removed', 'number_of_comments_removed', 'number_of_false_reports']
    actions = [recalculate_points_from_profile]

    @admin.display(description='username')
    def get_username(self, profile) -> str:
        return profile.user.username

class ChallengesAdmin(admin.ModelAdmin):
    list_display = ['id', 'description', 'time_for_challenge', 'latitude', 'longitude', 'allowed_distance']
    ordering = ['id']
    actions = [publish_challenge]

class ActiveChallengesAdmin(admin.ModelAdmin):
    list_display = ['date', 'get_challenge_id', 'get_challenge_description', 'get_time_for_challenge', 'get_latitude', 'get_longitude', 'get_allowed_distance', 'is_expired']
    ordering = ['date']
    actions = []

    @admin.display(ordering='challenge__id', description='challenge_id')
    def get_challenge_id(self, active_challenge) -> int:
        return active_challenge.challenge.id
    
    @admin.display(ordering='challenge__description', description='description')
    def get_challenge_description(self, active_challenge) -> str:
        return active_challenge.challenge.description
    
    @admin.display(ordering='challenge__time_for_challenge', description='time_for_challenge')
    def get_time_for_challenge(self, active_challenge) -> int:
        return active_challenge.challenge.time_for_challenge
    
    @admin.display(ordering='challenge__latitude', description='latitude')
    def get_latitude(self, active_challenge) -> int:
        return active_challenge.challenge.latitude
    
    @admin.display(ordering='challenge__longitude', description='longitude')
    def get_longitude(self, active_challenge) -> int:
        return active_challenge.challenge.longitude
    
    @admin.display(ordering='challenge__allowed_distance', description='allowed_distance')
    def get_allowed_distance(self, active_challenge) -> int:
        return active_challenge.challenge.allowed_distance
    
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['username', 'get_challenge_date', 'submission_time', 'get_minutes_late', 'get_submission', 'reported', 'reviewed']
    ordering = ['-reported', 'reviewed', 'username']
    actions = [report_submission, approve_submission, deny_submission]

    @admin.display(ordering='challenge__challenge_date', description='challenge_date')
    def get_challenge_date(self, submission) -> datetime:
        return submission.active_challenge.date
    
    @admin.display(description='minuites_late')
    def get_minutes_late(self, submission) -> int:
        return submission.get_minutes_late()
    
    @admin.display(description='Photo')
    def get_submission(self, submission) -> str:
        ''' Fixed by ER '''
        if submission.photo_bytes != None:
            photo_url=base64.b64encode(submission.photo_bytes).decode("utf-8")
            return format_html("<img src='data:image/png;base64,{decoded}'>".format(decoded=photo_url))
        else:
            return '[no image found]'

class UpvoteAdmin(admin.ModelAdmin):
    list_display = ['get_submission', 'voter_username']
    ordering = ['voter_username']
    actions = []

    @admin.display(ordering='submission__submission', description='submission')
    def get_submission(self, upvote) -> Submission:
        return upvote.submission
    
class CommentAdmin(admin.ModelAdmin):
    list_display = ['get_submission', 'comment_username', 'content', 'reported', 'reviewed']
    ordering = ['-reported', 'reviewed', 'comment_username']
    actions = [report_comment, approve_comment, deny_comment]

    @admin.display(ordering='submission__submission', description='submission')
    def get_submission(self, comment) -> Submission:
        return comment.submission


admin.site.unregister(User)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(User, UserAdmin) # no view for game master
admin.site.register(Challenge, ChallengesAdmin) # game master retains modification perms
admin.site.register(ActiveChallenge, ActiveChallengesAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(Upvote, UpvoteAdmin) # no view for game master
admin.site.register(Comment, CommentAdmin)
admin.site.register(Friend) # no view for game master
# otherwise, game master can view but not modify
# admin has all perms