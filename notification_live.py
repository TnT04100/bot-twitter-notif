#!/usr/bin/env python

import tweepy
import os
import psycopg2
import requests
import json
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv


load_dotenv()

twitter_api_key = os.getenv('TWITTER_API_KEY')
twitter_api_secret = os.getenv('TWITTER_API_KEY_SECRET')
twitter_access_token = os.getenv('TWITTER_ACCESS_TOKEN')
twitter_access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
twitch_client_id=str(os.getenv('TWITCH_CLIENT_ID'))
twitch_app_access_token=str(os.getenv('TWITCH_APP_ACCESS_TOKEN'))

auth = tweepy.OAuthHandler(twitter_api_key, twitter_api_secret)
auth.set_access_token(twitter_access_token, twitter_access_token_secret)
api = tweepy.API(auth)

DATABASE_URL = os.getenv('DATABASE_URL')

headers = {
    'Client-ID': twitch_client_id,
    'Authorization': 'Bearer ' + twitch_app_access_token
}

def is_live(donnees, id_bdd, streamer_name, name):
    if len(donnees['data']) == 1:
        #Le Streamer est en live
        if is_newlive(id_bdd, streamer_name):
            title = stream_info(streamer_name)
            title = title[0]
            post_tweet(streamer_name, title, temps_heure(), temps_jour(), name)
            return True
        else:
            print("%s est dans le même live" % (streamer_name))
            return True
    else:
        #Le Streamer n'est pas en live
        return False

def is_newlive(id_bdd, streamer_name):  
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute("SELECT (%s) FROM bot_twitter" % (id_bdd))
    stream_id_bdd = cur.fetchone()
    stream_id_bdd = stream_id_bdd[0]
    stream_id = stream_info(streamer_name)
    stream_id = stream_id[1]
    if stream_id != stream_id_bdd:
        cur.execute("UPDATE bot_twitter SET %s=%d;" % ((id_bdd), (int(stream_id))),)
        conn.commit()
        conn.close()
        return True
    else:
        return False

def get_live_info(streamer_name, id_bdd, name):
    stream = requests.get('https://api.twitch.tv/helix/streams?user_login=' + streamer_name, headers=headers)
    data = stream.json()
    if is_live(data, id_bdd, streamer_name, name):
        print("%s est en live" % (streamer_name))
        return True
    else:
        print("%s n'est pas en live" % (streamer_name))
        return False

def temps_heure():
    return (datetime.now()+timedelta( hours = 1 )).strftime("%H:%M")

def temps_jour():
    return (datetime.now()).strftime("%d-%m-%Y")

def post_tweet(streamer_name, title, hour, day, name):
    print(name + " a lancé un nouveau live à "+hour+" le "+day+" : \n"+title+"\ntwitch.tv/"+streamer_name)
    #api.update_status(name + " a lancé un nouveau live à "+hour+" le "+day+" : \n"+title+"\ntwitch.tv/"+streamer_name)


def stream_info(streamer_name):
    stream = requests.get('https://api.twitch.tv/helix/streams?user_login=' + streamer_name, headers=headers)
    donnees = stream.json()
    test = json.dumps(donnees)
    test = test[10::]
    test = test[:-20]
    final = json.loads(test)
    titre = final['title']
    stream_id = final['id']
    return titre, stream_id

def dernier_tweet_lu():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur=conn.cursor()
    cur.execute("SELECT id FROM last_id_twitter")
    last_id = cur.fetchone()
    last_id = int(last_id[0])
    return(last_id)
def stock_dernier_tweet_lu(last_seen_id):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur=conn.cursor()
    cur.execute("UPDATE last_id_twitter SET id=(%d);" % (int(last_seen_id)),)
    conn.commit()
    conn.close()
def reply():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    reponse = " "
    i = 0
    tweets = api.mentions_timeline(count = 5, since_id = dernier_tweet_lu(),tweet_mode='extended')
    for tweet in reversed(tweets):
        if dernier_tweet_lu() != tweet.id:
            if ("@kcorpnotiflive #kcorp stream") in tweet.full_text.lower():
                if saken():
                    reponse+="Saken "
                    i+=1
                if kameto():
                    reponse+="Kameto "
                    i+=1
                if cabochard():
                    reponse+="Cabochard "
                    i+=1
                if hantera():
                    reponse+="Hantera "
                    i+=1
                if bumm():
                    reponse+="Bumm "
                    i+=1
                if rekkles():
                    reponse+="Rekkles "
                    i+=1
                if bren():
                    reponse+="Bren "
                    i+=1
                if wao():
                    reponse+="Wao "
                    i+=1
                if stake():
                    reponse+="Stake "
                    i+=1
                if aztral():
                    reponse+="Aztral "
                    i+=1
                if itachi():
                    reponse+="Itachi "
                    i+=1
                if double61():
                    reponse+="Double "
                    i+=1
                if canbizz():
                    reponse+="Canbizz "
                    i+=1
                if darker():
                    reponse+="Darker "
                    i+=1
                if nalkya():
                    reponse+="Nalkya "
                    i+=1
                if eversax():
                    reponse+="Eversax"
                    i+=1
                if (saken() and kamet0() and cabochard() and hantera() and bumm() and rekkles() and bren() and wao() and stake() and aztral() and itachi() and double61() and canbizz() and darker() and nalkya() and eversax())==False:  
                    reponse+="Personne"
                if i>=2:
                    api.update_status("@"+tweet.user.screen_name+reponse+" sont en Live", in_reply_to_status_id = tweet.id)
                    stock_dernier_tweet_lu(tweet.id)
                elif i<2:
                    api.update_status("@"+tweet.user.screen_name+reponse+" est en Live", in_reply_to_status_id = tweet.id)
                    stock_dernier_tweet_lu(tweet.id)

def saken():
    name = "saken_lol"
    usual_name = "Saken"
    bdd = "id_saken"
    if get_live_info(name, bdd, usual_name):
        return True
    else:
        return False
def kameto():
    name = "kamet0"
    usual_name = "Kameto"
    bdd = "id_kameto"
    if get_live_info(name, bdd, usual_name):
        return True
    else:
        return False
def rekkles():
    name = "rekkles"
    usual_name = "Rekkles"
    bdd = "id_rekkles"
    if get_live_info(name, bdd, usual_name):
        return True
    else:
        return False
def cabochard():
    name = "Cabochardlol"
    usual_name = "Cabochard"
    bdd = "id_cabochard"
    if get_live_info(name, bdd, usual_name):
        return True
    else:
        return False
def bumm():
    name = "113bumm"
    usual_name = "Bumm"
    bdd = "id_bumm"
    if get_live_info(name, bdd, usual_name):
        return True
    else:
        return False
def hantera():
    name = "hantera1"
    usual_name = "Hantera"
    bdd = "id_hantera"
    if get_live_info(name, bdd, usual_name):
        return True
    else:
        return False
def wao():
    name = "waolol1"
    usual_name = "Wao"
    bdd = "id_wao"
    if get_live_info(name, bdd, usual_name):
        return True
    else:
        return False
def nalkya():
    name = "NalkyaLoL"
    usual_name = "Nalkya"
    bdd = "id_nelkya"
    if get_live_info(name, bdd, usual_name):
        return True
    else:
        return False
def stake():
    name = "stake"
    usual_name = "Stake"
    bdd = "id_stake"
    if get_live_info(name, bdd, usual_name):
        return True
    else:
        return False
def aztral():
    name = "aztral"
    usual_name = "Aztral"
    bdd = "id_aztral"
    if get_live_info(name, bdd, usual_name):
        return True
    else:
        return False
def itachi():
    name = "itachi_rl"
    usual_name = "Itachi"
    bdd = "id_itachi"
    if get_live_info(name, bdd, usual_name):
        return True
    else:
        return False
def eversax():
    name = "Eversax"
    usual_name = "Eversax"
    bdd = "id_eversax"
    if get_live_info(name, bdd, usual_name):
        return True
    else:
        return False
def bren():
    name = "bren_tm2"
    usual_name = "Bren"
    bdd = "id_bren"
    if get_live_info(name, bdd, usual_name):
        return True
    else:
        return False
def double61():
    name = "KC_Double61"
    usual_name = "Double"
    bdd = "id_kcdouble"
    if get_live_info(name, bdd, usual_name):
        return True
    else:
        return False
def canbizz():
    name = "Canbizz_"
    usual_name = "Canbizz"
    bdd = "id_canbizz"
    if get_live_info(name, bdd, usual_name):
        return True
    else:
        return False
def darker():
    name = "DarkeR_TM"
    usual_name = "Darker"
    bdd = "id_darker"
    if get_live_info(name, bdd, usual_name):
        return True
    else:
        return False        

while True:
    saken()
    kameto()
    rekkles()
    cabochard()
    hantera()
    bumm()
    wao()
    nalkya()
    eversax()
    stake()
    itachi()
    aztral()
    double61()
    canbizz()
    darker()
    bren()
    reply()
    time.sleep(15)

