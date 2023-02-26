import sqlite3

databasePath = "db.sqlite3"

def addUser(email, name, superuser):
	con = sqlite3.connect(databasePath)
	cur = con.cursor()
	username = email.split('@')
	text = ("INSERT INTO Users VALUES ('"+ email + "','" + username[0] + "','" + name + "','" + superuser + "');")
	cur.execute(text)
	con.commit()
	con.close()

def getUsername(email):
	con = sqlite3.connect(databasePath)
	cur = con.cursor()
	text = ("SELECT username FROM Users WHERE email = '" + email + "';")
	cur.execute(text)
	result = cur.fetchone()
	con.close()
	return result[0]

def getName(email):
	con = sqlite3.connect(databasePath)
	cur = con.cursor()
	text = ("SELECT name FROM Users WHERE email = '" + email + "';")
	cur.execute(text)
	result = cur.fetchone()
	con.close()
	return result[0]

def isSuperuser(email):
	con = sqlite3.connect(databasePath)
	cur = con.cursor()
	text = ("SELECT superuser FROM Users WHERE email = '" + email + "';")
	cur.execute(text)
	result = cur.fetchone()
	con.close()

	isSuperuser = False
	if result[0] == 1:
		isSuperuser = True 
	return isSuperuser

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

def deleteUser(email):
	con = sqlite3.connect(databasePath)
	cur = con.cursor()
	text = ("DELETE FROM Users WHERE email='" + email + "';")
	cur.execute(text)
	con.commit()
	con.close()

def addFriend(email, friendEmail):
	con = sqlite3.connect(databasePath)
	cur = con.cursor()
	username = email.split('@')
	text = ("INSERT INTO Friends VALUES ('"+ email + "','" + friendEmail + "');")
	cur.execute(text)
	con.commit()
	con.close()

def deleteFriend(email, FriendEmail):
	con = sqlite3.connect(databasePath)
	cur = con.cursor()
	text = ("DELETE FROM Friends WHERE email='" + email + "' AND friend_email='" + FriendEmail + "';")
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
	text = ("DELETE FROM Challenges WHERE challengeId='" + challengeId + "';")
	cur.execute(text)
	con.commit()
	con.close()

def addActiveChallenge(challengeDate, challengeId, expired):
	con = sqlite3.connect(databasePath)
	cur = con.cursor()
	text = ("INSERT INTO ActiveChallenges VALUES ('"+ challengeDate + "','" + challengeId + "','" + expired + "');")
	cur.execute(text)
	con.commit()
	con.close()

def deleteActiveChallenge(challengeDate):
	con = sqlite3.connect(databasePath)
	cur = con.cursor()
	text = ("DELETE FROM ActiveChallenges WHERE challengeDate='" + challengeDate + "';")
	cur.execute(text)
	con.commit()
	con.close()

def addSubmission(photoPath, email, challengeDate):
	con = sqlite3.connect(databasePath)
	cur = con.cursor()
	text = ("INSERT INTO Submission VALUES ('"+ photoPath + "','" + email + "','" + challengeDate + "');")
	cur.execute(text)
	con.commit()
	con.close()

def deleteSubmission(photoPath):
	con = sqlite3.connect(databasePath)
	cur = con.cursor()
	text = ("DELETE FROM Submission WHERE photoPath='" + photoPath + "';")
	cur.execute(text)
	con.commit()
	con.close()

def addVote(email, photoPath):
	con = sqlite3.connect(databasePath)
	cur = con.cursor()
	text = ("INSERT INTO Upvote VALUES ('"+ email + "','" + photoPath + "');")
	cur.execute(text)
	con.commit()
	con.close()

def removeVote(email, photoPath):
	con = sqlite3.connect(databasePath)
	cur = con.cursor()
	text = ("DELETE FROM Upvote WHERE email='" + email + "' AND photoPath='" + photoPath + "';")
	cur.execute(text)
	con.commit()
	con.close()