from email import message
import speech_recognition as sr
import pyttsx3
import datetime
from dateutil.relativedelta import relativedelta
import pytz
import smtplib
from webbrowser import BackgroundBrowser
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os.path
from googleapiclient.discovery import build
import re
import datetime
import webbrowser
import time
import random
import wikipedia
import sys
import plyer
def authorize_for_youtube():
    credentials=None
    if os.path.exists('token.pickle'):
       with open('token.pickle','rb') as token:
        print("Credentials Loading..")
        credentials=pickle.load(token)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print("Credentials Refreshing..")
            credentials.refresh(Request())
        else:
            flow=InstalledAppFlow.from_client_secrets_file('client_secrets.json',scopes=['https://www.googleapis.com/auth/youtube.readonly'])
            flow.run_local_server(port=8000,prompt='consent',authorization_prompt_message="")
            credentials=flow.credentials
        #Save the Credentials in token.pickle
        with open("token.pickle",'wb') as token:
            pickle.dump(credentials,token)
    return build('youtube','v3',credentials=credentials)

def yApi_service_object():
    api_key=os.environ.get('youtube_api_key')
    return build('youtube','v3',developerKey=api_key)

def isoConvert(isoTime):
        hours_pattern=re.compile(r'(\d+)H')
        minutes_pattern=re.compile(r'(\d+)M')
        seconds_pattern=re.compile(r'(\d+)S')
        hours=hours_pattern.search(isoTime)
        minutes=minutes_pattern.search(isoTime)
        seconds=seconds_pattern.search(isoTime)
        hours=int(hours.group(1)) if hours else 0
        minutes=int(minutes.group(1)) if minutes else 0
        seconds=int(seconds.group(1)) if seconds else 0
        
        return datetime.timedelta(
            hours=hours,
            minutes=minutes,
            seconds=seconds
        ).total_seconds()
def controlChromeBrowser():
        webbrowser.register('chrome',None,webbrowser.BackgroundBrowser("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"))
        return webbrowser.get('chrome')
def localNow():
    now=datetime.datetime.now()
    return now.astimezone()
def speak(query):
    engine.say(query)
    engine.runAndWait()
def hear():
        try:
            r=sr.Recognizer()
            #r.pause_threshold=1, seconds of non speaking audio before pharse considered as complete
            #r.pause_threshold=300, Minimum energy of audio that can be recorded [sensitivity of mic]
            #r.dynamic_threshold_energy=True, It set pause_threshold_energy dynamically if it set to True
            with sr.Microphone() as source:
                print("Listening..")
                r.adjust_for_ambient_noise(source)
                audio=r.listen(source) #parameter=>timeout=None [max no. of second it will wait for pharse to be start before giving up]
                                       #paremeter=>pharse_time_limit [no. of seconds for the pharse is recorded]
                # audio=r.record(source,offset=None,duration=None)
            try:
                print("Recognizing..")
                return r.recognize_google(audio)
            except:
                return "Sir, Please connect Me to internet!"
        except:
           return "Sir, I can't hear you!"

def getVideoId_from_keyword(keyword):
    request=youtube.search().list(part='snippet',q=keyword,type='video',order='viewCount',maxResults=1)
    response=request.execute()
    return response['items'][0]['id']['videoId']

def playVideo(videoId):
    control=controlChromeBrowser()
    control.open('https:\\www.youtube.com\watch?v='+videoId)

def setJarvis(engine):
    voices=engine.getProperty('voices')
    engine.setProperty('voice',voices[0].id)

def greeting():
    g=['Hello','Hi','Hey','Howdy','Hola']
    local_now=localNow()
    plyer.notification.notify(title="Jarvis Activated",message="{0:%B %d, %Y}".format(local_now),app_icon="jarvis.ico")
    time.sleep(1)
    speak("Jarvis Activated!")
    now=datetime.datetime.now()
    hour=now.hour
    if hour<12:
        speak(random.choice(g)+", ,Good Morning sir!")
    elif hour<18:
        speak(random.choice(g)+", ,Good Afternoon sir!")
    else:
        speak(random.choice(g)+", ,Good Evening sir!")
    speak("Please tell me, how may i help you!")

def sendEmail(sender,receiver,password):
    try:
        smtpClient=smtplib.SMTP(port=587)
        smtpClient.ehlo()
        smtpClient.starttls()
        smtpClient.login(sender,password)
        engine.say("sir, please write down your content!")
        engine.runAndWait()
        content=input("Content: ")
        smtpClient.sendmail(sender,receiver,content)
        smtpClient.close()
        speak("Email Successfully Sent!")
    except:
        speak("Sorry sir! i can't send this email!")
    
count=1
if __name__=="__main__":
    engine=pyttsx3.init('sapi5')
    setJarvis(engine)
    greeting()
    query=hear().lower()
    while True:
        if ('send' in query) and ('email' in query):
             speak('sir, please write down email address of receiver!')
             receiver=input("To: ")
             sender="glaxyboy1212@gmail.com"
             password=os.environ.get('email_password')
             sendEmail(sender,receiver,password)
        elif ("what" in query) and ("time" in query):
           local_now=localNow()
           speak("According to {tz} zone, now time is {0:%I}, {0:%M %p}".format(local_now,tz=local_now.tzinfo))
        elif ("what" in query) and ("date" in query):
            local_now=localNow()
            speak("{0:%B, %d, %Y}, fell on a {0:%A} and it is {0:%j} day, of the year".format(local_now))
        elif ("what" in query) and ('my' in query) and ('age' in query):
            d=datetime.date.today()
            b_date=datetime.date(2002,5,21)
            age=d-b_date
            speak("sir, You are only {0} year, {1} month, {2} days old".format(age.years,age.months,age.days))
        elif ('play' in query) and ('myplaylist' in query):
            youtube=authorize_for_youtube()
            playlist_request=youtube.playlists().list(part='snippet',mine=True)
            playlist_response=playlist_request.execute()
            # print(playlist_response)
            items=playlist_response['items']
            for item in items:
                if(item['snippet']['title'])=="MyMusic":
                    playlistId=item['id']
                    break
            nextPageToken=None
            while True:
                playlistItems_request=youtube.playlistItems().list(part="contentDetails",playlistId=playlistId,maxResults=50,pageToken=nextPageToken)
                playlistItems_response=playlistItems_request.execute()
            
                songs=[]
                for song in playlistItems_response['items']:
                    songs.append(song['contentDetails']['videoId'])
                nextPageToken=playlistItems_response.get('nextPageToken')
                if not nextPageToken:
                    break
            video_request=youtube.videos().list(part="contentDetails, snippet",id=','.join(songs))
            video_response=video_request.execute()
            items=video_response['items']
            for item in items:
                print(item)
                seconds=isoConvert((item['contentDetails']['duration']))
                main_title=item['snippet']['title']
                pattern=re.compile(r'[^|]+')
                title=pattern.search(main_title)
                title=title.group(0) if title else None
                print("Enjoy {}, for {} seconds".format(title,seconds))
                time.sleep(4)
                playVideo(item['id'])
                time.sleep(seconds+10)
                print("Are you want to listen next song? y/n:")
                if input()=='y':
                    pass
                else:
                   break
        elif ('open' in query) and (("vscode" in query) or ("vs code" in query)):
            os.startfile(os.path.join("C:\\Users\\vikas\\AppData\\Local\\Programs\\Microsoft VS Code","Code.exe"))
        elif ('open' in query) and ('stackoverflow' in query):
            control=controlChromeBrowser()
            control.open("stackoverflow.com")
        elif ('nitj' in query) and ("website" in query):
            control=controlChromeBrowser()
            control.open("nitj.ac.in")
        elif ('open' in query) and ('youtube' in query):
            control=controlChromeBrowser()
            control.open("youtube.com")
        elif ('play' in query):
            youtube=yApi_service_object()
            keyword=query.split('play')[1].strip()
            videoId=getVideoId_from_keyword(keyword)
            playVideo(videoId)
        elif ('play' in query) and (('kid video' in query) or ('kids video' in query)):
            with open("cartoons.txt",'r') as f:
                        for line in f:
                            speak(line)
            speak("Please tell me sir, which show you want to see!")
            name=hear()
            keyword=name+'hindi'
            videoId=getVideoId_from_keyword(keyword)
            playVideo(videoId)
        elif ('drumroll' in query) or ('drum' in query):
            os.startfile('drum roll.mp3')
        elif ("do you have any" in query) and (('pet' in query) or ('pets' in query)):
            speak("I don’t have any pets. I used to have a few bugs, but they kept getting squashed")
        elif ("what is" in query) and  ("value of pi" in query):
            speak("The approximate value of pi is 3.141592653589" )
            time.sleep(2)
            speak("this thing goes on forever!")
        elif ('give' in query) and ('money' in query):
            speak("Thing about the cloud is, no pockets. No pocket, no wallet" )
        elif ('give me' in query) and (('high five' in query) or ('five' in query)):
            speak("I would if I could but I can’t, so I’ll chant: 1 2 3 4, 5" )
        elif ("who" in query) and ("farted" in query):
            speak("If you are a, deniarr, you must be the supplier")
        elif ("who is your" in query) and (("best friend" in query) or ('frined' in query)):
            speak("I have a really strong connection to, your Wi-Fi.")
        elif ("where" in query) and ("you live" in query):
            speak("I live in a, cloud. So that makes me Cloudian" )
        elif ("are you weird" in query) or ("you are weird" in query):
            speak("I am quite unusual, that's true." )
        elif  ("stop jarvis" in query) or ("sleep jarvis" in query):
            speak("Jarvis Deactivated!")
            sys.exit()
        elif "" in query:
            if count<=2:
                speak("Please tell me sir, how may i help you!")
                time.sleep(5)
            else:
                speak("Sir, I can't recognise anything, so i am going to sleep")

                sys.exit()
            count+=1
        else:
            suggest=wikipedia.suggest(query)
            summary=wikipedia.summary(suggest,5)
            speak(summary)
        
        
