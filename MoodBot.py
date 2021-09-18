import telebot

TOKEN = '2029183496:AAHysBcZpDA8tLeaDwaadBiJNp_M6SIJEOg'

bot = telebot.TeleBot(TOKEN)

def extractUserDetails(message):
    username = message.json['from']['username']
    print(username)

def extractUserMood(message):
    print("Extracting Mood!")
    return message.json['text']

def sendUserMood():
    userMood = "User Mood!"
    print(userMood)
    return userMood

def sendHelpMessage():
    print("Helping!")
    return "Helping!"

@bot.message_handler(commands=['start'])
def send_welcome(message):
  extractUserDetails(message)
  bot.reply_to(message, "Howdy, how are you doing?")

@bot.message_handler(commands=['message'])
def send_enter_message(message):
  extractUserMood(message)
  bot.reply_to(message, sendUserMood())

@bot.message_handler(commands=['mood'])
def send_welcome(message):
	bot.reply_to(message, sendUserMood())

@bot.message_handler(commands=['help'])
def send_help_message(message):
	bot.reply_to(message, sendHelpMessage())

@bot.message_handler(func=lambda message: True)
def echo_all(message):
	bot.reply_to(message, "Invalid Command!")

def main():
    bot.polling()
    
if __name__ == '__main__':
    main()