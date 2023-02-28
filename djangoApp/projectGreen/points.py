from queries import Queries
from datetime import datetime as dt
import math

from projectGreen.settings import MICROSOFT
DOMAIN = MICROSOFT['valid_email_domains'][0] # = 'exeter.ac.uk'

SCORES = {'submission':10, 'upvote':{'given':1, 'recieved':2}}

def username_to_email(username: str) -> str:
    return username + '@' + DOMAIN

def email_to_username(email: str) -> str:
    #return email.split('@')[0]
    return email.strip('@'+DOMAIN)

''' OLD
def recalculate_user_points(username: str) -> int:
    email = username_to_email(username)
    points = 0

    result = Queries.fetch_query("SELECT * FROM Upvote WHERE email='{email}';".format(email))
    # fetches all upvotes given by a user
    points += len(result) * SCORES['upvote']['given']
    result = Queries.fetch_query("SELECT photoPath FROM Submission WHERE email='{email}';".format(email))
    # fetches photoPath (identifier) for all user's submissions
    submissions = [result[i][0] for i in range(len(result))]
    points += len(submissions) * SCORES['submission']
    for path in submissions:
        result = Queries.fetch_query("SELECT * FROM Upvote WHERE photoPath='{path}';".format(path))
        # fetches all upvotes on each submission
        points += len(result) * SCORES['upvote']['recieved']
    
    return points
'''

def recalculate_user_points(username: str) -> int: # new database structure; TODO get functions for these queries
    '''
    Calculated the total points for the user, based on submissions and interactions
    To be used on database initialization, or in the case of a desynchronous database
    '''
    points = 0
    result = Queries.fetch_query("SELECT * FROM Upvote WHERE username='{username}';".format(username))
    # fetches all upvotes given by a user
    points += len(result) * SCORES['upvote']['given']
    result = Queries.fetch_query("SELECT username, challenge_date, minuites_late FROM Submission WHERE username='{username}';".format(username))
    # fetches photoPath (identifier) for all user's submissions
    submissions = [result[i][0:1] for i in range(len(result))] # check this line
    for username, challenge_date, minuites_late in submissions:
        time_for_challenge = Queries.fetch_query("SELECT time_frame_minuites FROM ActiveChallenges WHERE challenge_date='{challenge_date}';".format(challenge_date))[0]
        points += SCORES['submission'] * math.sqrt(math.max(time_for_challenge-minuites_late, 0)+1) # punctuality scaling for submission points
        result = Queries.fetch_query("SELECT * FROM Upvote WHERE username='{username}' AND challenge_date='{challenge_date}';".format(username, challenge_date))
        # fetches all upvotes on each submission
        points += len(result) * SCORES['upvote']['recieved']
    return points

""" MORE OLD CODE
def upvote_callback(email: str, photo_path: str):
    '''
    To be triggered by an upvote event:
        - Adds vote to the database
        - Updates the points of the user making the upvote
        - Updates popularity metric for the submission recieving the upvote
    '''
    # update table
    add_vote(email, photo_path)
    # add to user points
    user_points = recalculate_user_points(email.split('@')[0])
    user_points += SCORES['upvote']
    # update interaction sum for submission
    target_user = Queries.fetch_query("SELECT email FROM Submission WHERE photoPath='{photo_path}';".format(photo_path))
    target_user = target_user.split('@')
    ''' FOR POPULARITY METRIC
    target_user_friends = Queries.fetch_query("SELECT * FROM Friends WHERE email='{target_user}' OR friendEmail='{target_user}';".format(target_user))
    target_user_points = recalculate_user_points(target_user.split('@')[0])
    lamdba_user = math.log( 1 + len(target_user_friends) ) * math.sqrt(target_user_points / SCORES['submission'])
    '''

def upvote_user_submission(self_username: str, target_username: str):
    photo_path = Queries.fetch_query("SELECT photoPath FROM Submission WHERE email='{email}';".format(email=username_to_email(target_username)))
    upvote_callback(username_to_email(self_username), photo_path)
"""

def upvote_callback(submission_username: str, submission_date: dt, voter_username: str):
    '''
    To be triggered by an upvote event:
        - Adds vote to the database
        - Updates the points of the user making the upvote
        - Updates popularity metric for the submission recieving the upvote
    '''
    # update table
    Queries.modify_query("INSERT INTO Upvote VALUES ('{submission_username}', '{submission_date}', '{voter_username}');".format(submission_username, submission_date.strtime('%Y-%m-%d'), voter_username))
    # add to users points
    user_points = Queries.fetch_query("SELECT points FROM Users WHERE username='{username}';".format(username=submission_username))[0] # correct index ??
    user_points += SCORES['upvote']['recieved']
    Queries.modify_query("UPDATE Users SET points={points} WHERE username='{username}';".format(points=user_points, username=submission_username))
    user_points = Queries.fetch_query("SELECT points FROM Users WHERE username='{username}';".format(username=voter_username))[0]
    user_points += SCORES['upvote']['given']
    Queries.modify_query("UPDATE Users SET points={points} WHERE username='{username}';".format(points=user_points, username=voter_username))
    # TODO update interaction sum for submission here

if __name__=='__main__':
    result = Queries.fetch_query("SELECT username FROM Users;")
    users = [result[i][0] for i in range(len(result))]
    for username in users:
        points = recalculate_user_points(username)
        Queries.modify_query("UPDATE Users SET points={points} WHERE username='{username}';".format(points, username))
        #Queries.fetch_query("SELECT points FROM Users WHERE username='{username}';".format(username))