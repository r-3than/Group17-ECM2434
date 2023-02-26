import sqlite3

DATABASE_PATH = "db.sqlite3"

class Queries:
	def fetch_query(sql):
		connection = sqlite3.connect(DATABASE_PATH)
		cursor = connection.cursor()
		text = (sql)
		cursor.execute(text)
		result = cursor.fetchone()
		connection.close()
		return result
	
	def modify_query(sql):
		connection = sqlite3.connect(DATABASE_PATH)
		cursor = connection.cursor()
		text = (sql)
		cursor.execute(text)
		connection.commit()
		connection.close()


def addUser(email, name, superuser):
	username = email.split('@')
	query = "INSERT INTO Users VALUES ('"+ email + "','" + username[0] + "','" + name + "','" + superuser + "');"
	Queries.modify_query(query)

def getUsername(email):
	query = "SELECT username FROM Users WHERE email = '" + email + "';"
	result = Queries.fetch_query(query)
	return result[0]

def getName(email):
	query = "SELECT name FROM Users WHERE email = '" + email + "';"
	result = Queries.fetch_query(query)
	return result[0]

def isSuperuser(email):
	query = "SELECT superuser FROM Users WHERE email = '" + email + "';"
	result = Queries.fetch_query(query)
	'''
	isSuperuser = False
	if result[0] == 1:
		isSuperuser = True 
	return isSuperuser
	'''
	return True if result[0]==1 else False # inline

def getAllEmails():
	query = "SELECT email FROM Users;"
	result = Queries.fetch_query(query)

	emails = []
	for i in range(len(result)):
		emails.append(result[i][0])
	return emails

def deleteUser(email):
	query = "DELETE FROM Users WHERE email='" + email + "';"
	Queries.modify_query(query)

def addFriend(email, friendEmail):
	username = email.split('@')
	query = "INSERT INTO Friends VALUES ('"+ email + "','" + friendEmail + "');"
	Queries.modify_query(query)

def deleteFriend(email, FriendEmail):
	query = "DELETE FROM Friends WHERE email='" + email + "' AND friend_email='" + FriendEmail + "';"
	Queries.modify_query(query)

def addChallenge(challengeId, description):
	query = "INSERT INTO Challenges VALUES ('"+ challengeId + "','" + description + "');"
	Queries.modify_query(query)

def deleteChallenge(challengeId):
	query = "DELETE FROM Challenges WHERE challengeId='" + challengeId + "';"
	Queries.modify_query(query)

def addActiveChallenge(challengeDate, challengeId, expired):
	query = "INSERT INTO ActiveChallenges VALUES ('"+ challengeDate + "','" + challengeId + "','" + expired + "');"
	Queries.modify_query(query)

def deleteActiveChallenge(challengeDate):
	query = "DELETE FROM ActiveChallenges WHERE challengeDate='" + challengeDate + "';"
	Queries.modify_query(query)

def addSubmission(photoPath, email, challengeDate):
	query = "INSERT INTO Submission VALUES ('"+ photoPath + "','" + email + "','" + challengeDate + "');"
	Queries.modify_query(query)

def deleteSubmission(photoPath):
	query = "DELETE FROM Submission WHERE photoPath='" + photoPath + "';"
	Queries.modify_query(query)

def addVote(email, photoPath):
	query = "INSERT INTO Upvote VALUES ('"+ email + "','" + photoPath + "');"
	Queries.modify_query(query)

def removeVote(email, photoPath):
	query = "DELETE FROM Upvote WHERE email='" + email + "' AND photoPath='" + photoPath + "';"
	Queries.modify_query(query)