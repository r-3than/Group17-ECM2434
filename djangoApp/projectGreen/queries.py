import sqlite3

databasePath = "db.sqlite3"

def addUser(email, name, isSuperuser, points):
	con = sqlite3.connect(databasePath)
	cur = con.cursor()
	username = email.split('@')
	text = ("INSERT INTO Users VALUES ('"+ username[0] + "','" + email + "','" + name + "','" + isSuperuser + "','" + points + "');")
	cur.execute(text)
	con.commit()
	con.close()

def getEmail(username):
	con = sqlite3.connect(databasePath)
	cur = con.cursor()
	text = ("SELECT email FROM Users WHERE username = '" + username + "';")
	cur.execute(text)
	result = cur.fetchone()
	con.close()
	return result[0]

def getName(username):
	con = sqlite3.connect(databasePath)
	cur = con.cursor()
	text = ("SELECT name FROM Users WHERE username = '" + username + "';")
	cur.execute(text)
	result = cur.fetchone()
	con.close()
	return result[0]

def getAllEmails():
	con = sqlite3.connect(databasePath)
	cur = con.cursor()
	text = ("SELECT email FROM Users;")
	cur.execute(text)
	result = cur.fetchall()
	con.close()

	emails = []
	for i in range(0, len(result)):
		emails.append(result[i][0])
	return emails

def deleteUser(username):
	con = sqlite3.connect(databasePath)
	cur = con.cursor()
	text = ("DELETE FROM Users WHERE username = '" + username + "';")
	cur.execute(text)
	con.commit()
	con.close()

def addFriend(selfUsername, friendUsername):
	con = sqlite3.connect(databasePath)
	cur = con.cursor()
	username = email.split('@')
	text = ("INSERT INTO Friends VALUES ('"+ selfUsername + "','" + friendUsername + "');")
	cur.execute(text)
	con.commit()
	con.close()

def deleteFriend(selfUsername, friendUsername):
	con = sqlite3.connect(databasePath)
	cur = con.cursor()
	text = ("DELETE FROM Friends WHERE selfUsername = '" + selfUsername + "' AND friendUsername='" + friendUsername + "';")
	cur.execute(text)
	con.commit()
	con.close()

def addChallenge(challengeId, description):
	con = sqlite3.connect(databasePath)
	cur = con.cursor()
	text = ("INSERT INTO Challenges VALUES ('"+ challengeId + "','" + description + "');")
	cur.execute(text)
	con.commit()
	con.close()

def deleteChallenge(challengeId):
	con = sqlite3.connect(databasePath)
	cur = con.cursor()
	text = ("DELETE FROM Challenges WHERE challengeId = '" + challengeId + "';")
	cur.execute(text)
	con.commit()
	con.close()

def addActiveChallenge(challengeDate, challengeId, timeFrameMinutes, isExpired):
	con = sqlite3.connect(databasePath)
	cur = con.cursor()
	text = ("INSERT INTO ActiveChallenges VALUES ('"+ challengeDate + "','" + challengeId + "','" + timeFrameMinutes + "','" + isExpired + "');")
	cur.execute(text)
	con.commit()
	con.close()

def deleteActiveChallenge(challengeDate):
	con = sqlite3.connect(databasePath)
	cur = con.cursor()
	text = ("DELETE FROM ActiveChallenges WHERE challengeDate = '" + challengeDate + "';")
	cur.execute(text)
	con.commit()
	con.close()

def addSubmission(username, challengeDate, photo, miutesLate, sumOfInteractions):
	con = sqlite3.connect(databasePath)
	cur = con.cursor()
	text = ("INSERT INTO Submission VALUES ('"+ username + "','" + challengeDate + "','" + photo + "','" + miutesLate + "','" + sumOfInteractions + "');")
	cur.execute(text)
	con.commit()
	con.close()

def deleteSubmission(username, challengeDate):
	con = sqlite3.connect(databasePath)
	cur = con.cursor()
	text = ("DELETE FROM Submission WHERE username = '" + username + "' AND challengeDate = '" + challengeDate + "';")
	cur.execute(text)
	con.commit()
	con.close()

def addVote(submissionUsername, submissionDate, voterUsername):
	con = sqlite3.connect(databasePath)
	cur = con.cursor()
	text = ("INSERT INTO Upvote VALUES ('"+ submissionUsername + "','" + submissionDate + "','" + voterUsername + "');")
	cur.execute(text)
	con.commit()
	con.close()

def removeVote(submissionUsername, submissionDate, voterUsername):
	con = sqlite3.connect(databasePath)
	cur = con.cursor()
	text = ("DELETE FROM Upvote WHERE submissionUsername = '" + emsubmissionUsernameail + "' AND submissionDate = '" + submissionDate + "' AND voterUsername = '" + voterUsername + "';")
	cur.execute(text)
	con.commit()
	con.close()