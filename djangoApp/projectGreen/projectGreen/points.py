from django.contrib.auth.models import User
from projectGreen.models import Profile, Submission, Upvote, Challenge, ActiveChallenge

from datetime import datetime as dt
import math

SCORES = {'submission':10, 'upvote':{'given':1, 'recieved':2}}

def set_points(username: str, points_value: int):
    user = User.objects.get(username=username)
    try:
        profile = Profile.objects.get(user=user)
        profile.points = points_value
    except Profile.DoesNotExist:
        profile = Profile(user=user, points=points_value)
    profile.save()

def add_points(username: str, points_to_add: int):
    user = User.objects.get(username=username)
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        profile = Profile(user=user, points=0)
    points = profile.points
    points += points_to_add
    profile.points = points
    profile.save()

def punctuality_scaling(time_for_challenge: int, minutes_late: int):
    return round(math.sqrt(max(time_for_challenge-minutes_late, 0)+1))

def recalculate_user_points(username: str):
    points = 0
    upvotes_given = Upvote.objects.filter(voter_username=username)
    points += len(upvotes_given)*SCORES['upvote']['given']
    upvotes_recieved = Upvote.objects.filter(submission__username=username)
    points += len(upvotes_recieved)*SCORES['upvote']['recieved']
    submissions = Submission.objects.filter(username=username)
    for sub in submissions:
        time_for_challenge = sub.active_challenge.challenge.time_for_challenge
        points += SCORES['submission'] * punctuality_scaling(time_for_challenge, sub.minutes_late)
    set_points(username, points)
    # TODO add consideration for reported posts

def upvote_callback(submission: Submission, voter_username: str, create_upvote_instance: bool=True):
    if create_upvote_instance:
        u = Upvote(submission=submission, voter_username=voter_username)
        u.save()
    add_points(submission.username, SCORES['upvote']['recieved'])
    add_points(voter_username, SCORES['upvote']['given'])

def submission_callback(username: str, a_challenge: ActiveChallenge, submission_time: dt, create_submission_instance: bool=True):
    #https://stackoverflow.com/questions/5259882/subtract-two-times-in-python
    minutes_late = dt.combine(dt.min, submission_time) - dt.combine(dt.min, a_challenge.date)
    minutes_late = minutes_late.minute
    if create_submission_instance:
        s = Submission(username=username, active_challenge=a_challenge, minutes_late=minutes_late)
        s.save()
    time_for_challenge = a_challenge.challenge.time_for_challenge
    add_points(username, SCORES['submission']*punctuality_scaling(time_for_challenge, minutes_late))


# TODO need callbacks for removing submissions / upvotes