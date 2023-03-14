'''
DEPRECATED (for security reasons)
These are residual functions from the initial pure SQL database - models.py is now being used.
The Queries class should still be usable with the correct input queries for the new database structure.
'''

import sqlite3

DATABASE_PATH = "db.sqlite3"

class Queries:
	def fetch_query(sql: str) -> list:
		'''
		For SELECT queries
		'''
		connection = sqlite3.connect(DATABASE_PATH)
		cursor = connection.cursor()
		text = (sql)
		cursor.execute(text)
		result = cursor.fetchone()
		connection.close()
		return result
	
	def modify_query(sql: str):
		'''
		For INSERT INTO and DELETE FROM queries
		'''
		connection = sqlite3.connect(DATABASE_PATH)
		cursor = connection.cursor()
		text = (sql)
		cursor.execute(text)
		connection.commit()
		connection.close()


# The following functions are deprecated - more specifically, the queries are insecure.
def add_user(email, name, superuser):
	username = email.split('@')
	query = "INSERT INTO Users VALUES ('"+ email + "','" + username[0] + "','" + name + "','" + superuser + "');"
	Queries.modify_query(query)

def get_username(email):
	query = "SELECT username FROM Users WHERE email = '" + email + "';"
	result = Queries.fetch_query(query)
	return result[0]

def get_name(email):
	query = "SELECT name FROM Users WHERE email = '" + email + "';"
	result = Queries.fetch_query(query)
	return result[0]

def is_superuser(email):
	query = "SELECT superuser FROM Users WHERE email = '" + email + "';"
	result = Queries.fetch_query(query)
	return True if result[0]==1 else False

def get_all_emails():
	query = "SELECT email FROM Users;"
	result = Queries.fetch_query(query)

	emails = []
	for i in range(len(result)):
		emails.append(result[i][0])
	return emails

def delete_user(email):
	query = "DELETE FROM Users WHERE email='" + email + "';"
	Queries.modify_query(query)

def add_friend(email, friendEmail):
	username = email.split('@')
	query = "INSERT INTO Friends VALUES ('"+ email + "','" + friendEmail + "');"
	Queries.modify_query(query)

def delete_friend(email, FriendEmail):
	query = "DELETE FROM Friends WHERE email='" + email + "' AND friend_email='" + FriendEmail + "';"
	Queries.modify_query(query)

def add_challenge(challengeId, description):
	query = "INSERT INTO Challenges VALUES ('"+ challengeId + "','" + description + "');"
	Queries.modify_query(query)

def delete_challenge(challengeId):
	query = "DELETE FROM Challenges WHERE challengeId='" + challengeId + "';"
	Queries.modify_query(query)

def add_active_challenge(challengeDate, challengeId, expired):
	query = "INSERT INTO ActiveChallenges VALUES ('"+ challengeDate + "','" + challengeId + "','" + expired + "');"
	Queries.modify_query(query)

def delete_active_challenge(challengeDate):
	query = "DELETE FROM ActiveChallenges WHERE challengeDate='" + challengeDate + "';"
	Queries.modify_query(query)

def add_submission(photoPath, email, challengeDate):
	query = "INSERT INTO Submission VALUES ('"+ photoPath + "','" + email + "','" + challengeDate + "');"
	Queries.modify_query(query)

def delete_submission(photoPath):
	query = "DELETE FROM Submission WHERE photoPath='" + photoPath + "';"
	Queries.modify_query(query)

def add_vote(email, photoPath):
	query = "INSERT INTO Upvote VALUES ('"+ email + "','" + photoPath + "');"
	Queries.modify_query(query)

def remove_vote(email, photoPath):
	query = "DELETE FROM Upvote WHERE email='" + email + "' AND photoPath='" + photoPath + "';"
	Queries.modify_query(query)
