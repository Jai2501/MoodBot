import datetime
import MoodModel

# Extracting User Details
def addUser(message, client):
    firstName = message.chat.first_name 
    lastName = message.chat.last_name 
    userName = message.chat.username 
    chatId = message.chat.id
    isResponding = False
    lastResponse = None
    history = []

    userDetailsToPutInDatabase = {
        '_id': chatId,
        'userName': userName,
        'firstName': firstName,
        'lastName': lastName,
        'isResponsing': isResponding,
        'lastResponse': None,        #date obj
        'history': history      
    }

    client.MoodDiaryUsers.Users.insert_one(userDetailsToPutInDatabase)
    print("User Saved Successfully! ", userName)

def fetchUser(message, client):
    # query db ny chat id
    db = client.MoodDiaryUsers.Users
    chatId = message.chat.id
    result = db.find_one({'_id': chatId})
    return result
#user_trial = client.MoodDiaryUsers.Users.find_one({'chatId':"1234"})
#return None

def respondedForToday(message, client):
    user = fetchUser(message, client)
    print(user['userName'])
    messageTime = user['lastResponse']
    now = datetime.datetime.now()
    
    if messageTime is not None:
        difference = now - messageTime
        return difference.days == 0
        
    return False
    
def addMessage(message, client):
    body = message.text
    timestamp = datetime.datetime.utcnow()
    mood = getUserMood(message)

    response = {
        'body': body, 
        'timestamp': timestamp,
        'mood': mood
    }
    
    # Push Message Data to Response Collection
    newResponseId = client.MoodDiaryUsers.Responses.insert_one(response)
    newResponseId = newResponseId.inserted_id

    # Fetch User Details from Users Collection
    user = fetchUser(message, client)
    
    # Updating the user - append messageId to history, isResponding = false, lastResponse = timestamp
    # 'isResponding': False, 
    client.MoodDiaryUsers.Users.update({'_id': user['_id']}, {'$push': {'history': newResponseId}, '$set': {'isResponding': False, 'lastResponse': timestamp}})

    return True

# Extracting User Mood from Model
def getUserMood(message):
    print("Extracting Mood using the model!")
    text = message.text
    print("Message is: ", text[9:])
    print("Detected Mood", MoodModel.get_feelings(text[9:]))
    return MoodModel.get_feelings(text[9:])
    
# Extracting User Mood from Database
def getLatestMood(message, client):
    print("Extracting Mood from the Database")
    userDetails = client.MoodDiaryUsers.Responses.find_one({'_id': message.chat.id})
    
    if (userDetails['history'] is None or (len(userDetails['history']) == 0)):
        return "Sorry No Mood Data Available"

    lastResponseId = userDetails['history'][len(userDetails['history']) - 1]

    return client.MoodDiaryUsers.Responses.find_one({'_id': lastResponseId})['mood']

# Checks if a user exists
def userExists(message, client):
    print("User Details: ", client.MoodDiaryUsers.Users.find_one({'_id': message.chat.id}))

    return not client.MoodDiaryUsers.Users.find_one({'_id': message.chat.id}) is None
    
    # return message.json['from']['username'] in db

def getHistory(message, client):
    def recordToTxt(record):
        time = record['timestamp'].strftime("%d %B %Y")
        mood = "You were feeling " + "<b>{}</b>".format(record['mood'])
        body = "Message: " + record['body'][9:] + "\n\n------------------------------------"
        return "{} \n\n{} \n\n{}".format(time, mood, body)

    if not userExists(message, client):
        return "Please /start the bot first"

    user = fetchUser(message, client)
    userHistory = user['history']

    records = map(lambda docId : client.MoodDiaryUsers.Responses.find_one({'_id': docId}), userHistory)
    recordStrings = map(recordToTxt, records)
    recordStrings = "\n\n".join(recordStrings)

    return recordStrings

