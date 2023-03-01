from queries import Queries, add_vote
import math

from projectGreen.settings import MICROSOFT
#DOMAIN = 'exeter.ac.uk'
DOMAIN = MICROSOFT['valid_email_domains'][0]

# NOTE photo storage `photos\{challenge-date}\{username}.png`
# would allow database restructure to identify submission by challenge date/user

SCORES = {'submission':10, 'upvote':{'given':1, 'recieved':2}}

def username_to_email(username: str) -> str:
    return username + '@' + DOMAIN

def email_to_username(email: str) -> str:
    return email.split('@')[0]

''' OLD
def recalculate_user_points(username: str) -> int:
    email = username_to_email(username)
    points = 0
    SCORES = {'submission':10, 'upvote':1}
    for table in SCORES:
        result = Queries.fetch_query("SELECT * FROM {table} WHERE email='{email}';".format(table.capitalize(), email))
        points += len(result) * SCORES[table.lower()]
    return points
'''

def recalculate_user_points(username: str) -> int:
    '''
    Calculated the total points for the user, based on submissions and interactions
    To be used on database initialization, or in the case of a desynchronous database
    '''
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
# TODO this will be stored in database and fetched to prevent continual recalculation
# TODO incorporate "lateness" of submission

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
    target_user_friends = Queries.fetch_query("SELECT * FROM Friends WHERE email='{target_user}' OR friendEmail='{target_user}';".format(target_user))
    target_user_points = recalculate_user_points(target_user.split('@')[0])
    lamdba_user = math.log( 1 + len(target_user_friends) ) * math.sqrt(target_user_points / SCORES['submission'])
    # TODO add this to database

def upvote_user_submission(self_username: str, target_username: str):
    photo_path = Queries.fetch_query("SELECT photoPath FROM Submission WHERE email='{email}';".format(email=username_to_email(target_username)))
    upvote_callback(username_to_email(self_username), photo_path)