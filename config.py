import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN") #Bot token load.
DB_URL = os.getenv("DB_URL") #Database url load.
MAX_BET = 200 #Maximum bet for a game.
CHECK_IN = {'min': 50, 'max': 100} #Minimum and Maximum check in points.
RUNNER = [1226891544334700667, 756407110128107540] #Role ids of admins to run the bots admin commands.
GAME_COOLDOWN = 10 #set in minutes.

#Embed color selector for easy handling of colors.
def Color(status=None):
    if status is True:
        return 0x66FF00 #green color.
    elif status is False:
        return 0xFF6666 #red color.
    else:
        return 0x060f42 #main embed color.