from queries import Queries
from datetime import datetime as dt
import math

SCORES = {'submission':10, 'upvote':{'given':1, 'recieved':2}}

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
        points += SCORES['submission'] * math.round(math.sqrt(math.max(time_for_challenge-minuites_late, 0)+1)) # punctuality scaling for submission points
        result = Queries.fetch_query("SELECT * FROM Upvote WHERE username='{username}' AND challenge_date='{challenge_date}';".format(username, challenge_date))
        # fetches all upvotes on each submission
        points += len(result) * SCORES['upvote']['recieved']
    return points

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