from django.contrib.auth.models import User
from projectGreen.models import Profile, Submission, Upvote, Challenge, ActiveChallenge

from datetime import datetime as dt
import math

SCORES = {'submission':10, 'upvote':{'given':1, 'recieved':2}}

def set_points(username: str, points_value: int):
    '''
    Sets the points of a user's profile
    '''
    user = User.objects.get(username=username)
    try:
        profile = Profile.objects.get(user=user)
        profile.points = points_value
    except Profile.DoesNotExist:
        profile = Profile(user=user, points=points_value)
    profile.save()

def add_points(username: str, points_to_add: int):
    '''
    Increments a user's points in their profile
    '''
    user = User.objects.get(username=username)
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        profile = Profile(user=user, points=0)
    points = profile.points
    points += points_to_add
    profile.points = points
    profile.save()

def minutes_late_calc(reference_time: dt, submission_time: dt) -> int:
    '''
    Calculates minutes passed since reference_time
    https://stackoverflow.com/questions/5259882/subtract-two-times-in-python
    '''
    minutes_late = dt.combine(dt.min, submission_time) - dt.combine(dt.min, reference_time)
    return minutes_late.minute

def punctuality_scaling(time_for_challenge: int, minutes_late: int):
    '''
    Used to scale points based on "lateness" of submission
    max ~= sqrt(time_for_challenge); min = 1
    '''
    return round(math.sqrt(max(time_for_challenge-minutes_late, 0)+1))

def recalculate_user_points(username: str):
    '''
    Calculates the total points for a user based on submissions and interactions
    '''
    points = 0
    upvotes_given = Upvote.objects.filter(voter_username=username, submission__reported=False)
    points += len(upvotes_given)*SCORES['upvote']['given']
    upvotes_recieved = Upvote.objects.filter(submission__username=username, submission__reported=False)
    points += len(upvotes_recieved)*SCORES['upvote']['recieved']
    # interactions only counted on non-reported submissions
    submissions = Submission.objects.filter(username=username)
    for sub in submissions:
        if sub.reported:
            # no points for reported submission
            continue
        time_for_challenge = sub.active_challenge.challenge.time_for_challenge
        points += SCORES['submission'] * punctuality_scaling(time_for_challenge, sub.minutes_late)
    set_points(username, points)

def upvote_callback(submission: Submission, voter_username: str, create_upvote_instance: bool=True):
    '''
    Creates upvote object in database (conditional flag) and syncronises points
    '''
    if create_upvote_instance:
        u = Upvote(submission=submission, voter_username=voter_username)
        u.save()
    add_points(submission.username, SCORES['upvote']['recieved'])
    add_points(voter_username, SCORES['upvote']['given'])

def submission_callback(username: str, a_challenge: ActiveChallenge, minutes_late: dt, create_submission_instance: bool=True):
    '''
    Creates submission object in database (conditional flag) and syncronises points
    '''
    if create_submission_instance:
        s = Submission(username=username, active_challenge=a_challenge, minutes_late=minutes_late)
        s.save()
    time_for_challenge = a_challenge.challenge.time_for_challenge
    add_points(username, SCORES['submission']*punctuality_scaling(time_for_challenge, minutes_late))


# TODO concurrently remove points when post is reported
def remove_upvote(upvote: Upvote, delete_instance: bool=True):
    '''
    Removes upvote object in database (conditional flag) and syncronises points
    '''
    if not upvote.submission.reported:
        add_points(upvote.voter_username, -SCORES['upvote']['given'])
        add_points(upvote.submission.username, -SCORES['upvote']['recieved'])
    if delete_instance: upvote.delete()

def remove_submission(submission: Submission, delete_instance: bool=True):
    '''
    Removes upvote object in database (conditional flag) and syncronises points
    '''
    if not submission.reported:
        time_for_challenge = submission.active_challenge.challenge.time_for_challenge
        points_to_remove = SCORES['submission'] * punctuality_scaling(time_for_challenge, submission.minutes_late)
        add_points(submission.username, -points_to_remove)
    if delete_instance: submission.delete()