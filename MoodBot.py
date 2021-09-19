from backend import addMessage, addUser, getHistory, respondedForToday, userExists, getLatestMood
import telebot
from pprint import pprint # pprint for a prettier print
from pymongo import MongoClient
from datetime import datetime
import config

# The DB Url
mongoDBUrl = "mongodb+srv://MoodBot:MoodBot%40HackTheNorth@mooddiary.dcals.mongodb.net/MoodBot?retryWrites=true&w=majority"
client = MongoClient(mongoDBUrl)
db=client.admin
serverStatusResult=db.command("serverStatus")
pprint("Connected to the server")

user_trial = client.MoodDiaryUsers.Users.find_one({'chatId':"1234"})
print(user_trial)

bot = telebot.TeleBot(config.bot['token'], parse_mode="HTML")
isAwaitingMessage = False

# def brodcastMessage(message):
#     for user in db:
#         chatId = user.chatId
#         bot.send_message(chat_id, message)

# Returning Help Message
def sendHelpMessage():
    print("Helping!")
    return "Helping!"

# Handling /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not userExists(message, client):
        addUser(message, client)
    bot.reply_to(message, "Howdy, how are you doing?")

# Handling /message command
@bot.message_handler(commands=['message'])
def send_enter_message(message):
    if not userExists(message, client):
        bot.reply_to(message, "Please enter /start first")
    elif respondedForToday(message, client):
        bot.reply_to(message, "You have already sent a response for today. See you tomorrow!")
    else:
        addMessage(message, client)
        bot.reply_to(message, "You response for the day has been recorded!")

# Handling /help command
@bot.message_handler(commands=['help'])
def send_help_message(message):
	bot.reply_to(message, sendHelpMessage())

# @bot.message_handler(commands=['mood'])
# def send_mood_message(message):
# 	bot.reply_to(message, getLatestMood(message, client))

@bot.message_handler(commands=['view'])
def send_view_message(message):
    records = getHistory(message, client)
    bot.reply_to(message, records)

# Handling unknown commands
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    global isAwaitingMessage
    if isAwaitingMessage:
        isAwaitingMessage = False
    else:
	    bot.reply_to(message, "Invalid Command!")

# Main Method
def main():
    bot.polling()

    #send a daily reminder to all users
    while(True):
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")        
        if current_time=='00:00:00':
            print("the start of a new day")
            # brodcastMessage("Good morning")
    
if __name__ == '__main__':
    main()

