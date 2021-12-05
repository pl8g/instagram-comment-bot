import pprint
import sys(), os
import time
import json
import random
from InstagramAPI import InstagramAPI
from contextlib import contextmanager
from colorama import Fore,Back
from colorama import init
init(autoreset = True)

sys.stdout.write('\033[A\033[K')

def usernameInput():
    username = input("Username: \n")
    return username

def passwordInput():
    password = input("Password: \n")
    return password

refreshReady = False
commentsReady = False
delay = 0
commentinput = ''
commentList = []
previousComments = {}

@contextmanager
def hide():
  with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:  
            yield
        finally:
            sys.stdout = old_stdout

def timelineFeed():
        tz = -time.timezone
        data = json.dumps({'_uuid': api.uuid,
                           '_uid': api.username_id,
                           '_csrftoken': api.token,
                           'is_prefetch': '0',
                           'battery_level': '100',
                           'is_charging': '1',
                           'will_sound_on': '1',
                           'is_on_screen': 'true',
                           'timezone_offset': tz,
                           'experiment': 'ig_android_profile_contextual_feed'})
        return api.SendRequest('feed/timeline/', data)

def getReady():
    global refreshReady
    global commentsReady
    global delay
    global commentinput
    global commentList
    while commentsReady == False:
        print('Please enter your comment or comments, seperated by ' + Fore.RED + 'a colon.\n' + Fore.RESET
            + 'Example - ' + Back.WHITE + Fore.BLACK + 'comment 1:comment 2:comment 3')
        commentinput = input()
        commentList = commentinput.split(':')
        checkEmpty = 0
        for i in range(len(commentList)):
            if all('' == s or s.isspace() for s in commentList[i]):
                print(Back.LIGHTWHITE_EX + Fore.RED + '\n One or more item(s) in list are empty!')
                commentList = ''
                checkEmpty += 1
                break
        if checkEmpty == 0:
            commentsReady = True
            break

    while refreshReady == False:
        delay = input("\nPlease enter how many seconds you would like to wait between each refresh. A longer wait means a lesser chance of being action blocked, press enter to start program. \n")
        try:
            val = int(delay)
            refreshReady = True
            print("Autorefresh set to " + str(delay) +  " seconds. Press CTRL+C to choose new preferences or close the tab to stop.")
            return val
        except ValueError:
            try:
                val = float(delay)
                refreshReady = True
                print("Autorefresh set to " + str(delay) +  " seconds. Press CTRL+C to choose new preferences or close the tab to stop.")
                return val
            except ValueError:
                print(Back.LIGHTWHITE_EX + Fore.RED + "Inputted value is not a number!")

def stopLoop():
    global refreshReady
    global commentsReady
    refreshReady = False
    commentsReady = False

print(Back.WHITE + Fore.BLACK + 'Instagram top comment bot, contact me at @simpifies if you have any questions\n')
print(Fore.RED + 'if you paid for this bot, you have been scammed!')
print(Fore.WHITE + 'if you dont want to get action blocked, use http://stcb.rf.gd\n')
username = usernameInput()
password = passwordInput()
api = InstagramAPI(username, password)

while api.isLoggedIn == False:
    with hide():
        api.login()
    try:
        if api.LastJson['two_factor_required']:
            print(Fore.RED + "Instagram login has failed: ")
            print(Back.WHITE + Fore.YELLOW + "Two factor authentication required!")
            authID = api.LastJson['two_factor_info']['two_factor_identifier']
            authcode = input("Please imput SMS code here: ")
            api.finishTwoFactorAuth(authcode, authID)
    except:
        pass
    try: 
        while 'challenge_required' in api.LastJson['message']:
            print(Fore.RED + 'Instagram Login has failed: ')
            print(Back.White + Fore.YELLOW + 'Challenge required error!')
            print('Do one of these three things to sign in:')
            print(Fore.GREEN + '1 - Open the Instagram app and click "This was me" on the prompt')
            print(Fore.GREEN + '2 - Go to the following link and sign in')
            CHALLENGE = api.LastJson['challenge']['url'] 
            print(CHALLENGE)
            print(Fore.GREEN + '3 - Get code from email (must have verified email linked to account)')
            print('\nIf you choose to do either of the first two, complete it and then press enter.')
            select = input('If you choose to do the third option, type the number "3" and press enter\n')
            if select == 3:
                api.get_id(username)
                api.completeCheckpoint1()
                AUTHCODE = input('Enter code recieved from email: ')
                api.completeCheckpoint2(AUTHCODE)
            with hide():
                api.login
            if 'challenge_required' in api.LastJson['message']:
                print(Fore.RED +'Challenge has not been resolved!')
                print(Fore.RED +'Please try again')
                time.sleep(2)
    except:
        pass
    if api.isLoggedIn == False:
        print(Back.WHITE + Fore.RED + "Instagram login has failed.")
        username = usernameInput()
        password = passwordInput()
        api = InstagramAPI(username, password)

print('\n' + Fore.CYAN + 'Logged in!')

while api.isLoggedIn == True:
    getReady()
    while refreshReady == True and commentsReady == True:
        try:
            timelineFeed()
            with open('logData.txt', 'r') as logfile:
                logs = logfile.read()
            result = api.LastJson
            formatted_json = pprint.pformat(result)
            timeline = result['items']
            i = 0
            total = len(timeline)
            while i <= total - 1:
                try:
                    text = random.choice(commentList)
                    media_id = timeline[i]['id']
                    username = timeline[i]['user']['username']
                    post_timestamp = timeline[i]['taken_at']
                    now_timestamp = time.time()
                    difference = float(now_timestamp) - float(post_timestamp)
                    if media_id in logs:
                        status = Back.GREEN + Fore.BLACK + "[Success]"
                        msg = '[Already commented.]'
                    elif difference > 60:
                        status = Back.LIGHTWHITE_EX + Fore.BLACK + '[Expired]'
                        msg = '[More than 60 seconds]'
                    elif not timeline[i]['comment_count'] == 0:
                        status = Back.YELLOW + Fore.BLACK + '[-Failed-]'
                        msg = '[ Not fist comment ]'
                    else:
                        status = Back.CYAN + Fore.BLACK + '[  Run  ]'
                        msg = '[Making comment.....]'
                        comment = api.comment(media_id, text)
                        previousComments[media_id] = text
                        if comment:
                            with open('logData.txt', 'a+') as savelog:
                                savelog.seek(0)
                                data = savelog.read(100)
                                if len(data) > 0:
                                    savelog.write("\n")
                                savelog.write(media_id)
                        else:
                            with open('logData.txt', 'a+') as savelog:
                                savelog.seek(0)
                                data = savelog.read(100)
                                if len(data) > 0:
                                    savelog.write("\n")
                                savelog.write(media_id)
                            try:
                                if 'feedback_required' in api.LastJson['message']:
                                    msg = '[Action blocked]'
                                    status = Back.RED + Fore.BLACK + "[-FAILED-]"
                                else:
                                    msg = '[Unknown Error (Comments may be off)]'
                                    status = Back.YELLOW + Fore.BLACK + "[-FAILED-]"
                            except TypeError:
                                msg = '[Unknown Error!]'
                                status = Back.RED + Fore.BLACK + "[-FAILED-]"
                    if status == Back.CYAN + Fore.BLACK + '[  Run  ]' or status == Back.GREEN + Fore.BLACK + "[Success]":
                        print('({}) {}'.format(i, status) + Back.RESET + Fore.RESET + ' {} | {} | User: {} | Post age: '.format(msg, previousComments[media_id], username) + Back.YELLOW + Fore.BLACK + str(round(difference)) + Back.RESET)
                    elif status == Back.RED + Fore.BLACK + "[-FAILED-]":
                        print('({}) {}'.format(i, status) + Back.RESET + Fore.RESET + ' {} | {} | User: {} | Post age: '.format(msg, previousComments[media_id], username) + Back.YELLOW + Fore.BLACK + str(round(difference)) + Back.RESET)
                        sys.exit()
                    elif status == Back.YELLOW + Fore.BLACK + '[-Failed-]':
                        print('({}) {}'.format(i, status) + Back.RESET + Fore.RESET + ' {} | User: {} | Post age: '.format(msg, username) + Back.YELLOW + Fore.BLACK + str(round(difference)) + Back.RESET)
                    else:
                        print('({}) {}'.format(i, status) + Back.RESET + Fore.RESET + ' {} | --none-- | User: {} | Post age: '.format(msg, username) + Back.YELLOW + Fore.BLACK + str(round(difference)) + Back.RESET)
                except KeyError:
                    print('({}) '.format(i) + Back.YELLOW + Fore.BLACK + "[Couldn't get post]")
                i += 1
            time.sleep(float(delay))      
            for x in range(i):
                sys.stdout.write('\033[A\033[K')
        except KeyboardInterrupt:
            print(Back.GREEN + Fore.BLACK + "\n Input recieved. Stopping.                                                                                                         ")
            stopLoop()
