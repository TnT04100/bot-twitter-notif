#!/usr/bin/env python

from riotwatcher import LolWatcher
import tweepy
import os
import psycopg2
import requests
import json
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv


load_dotenv()

api_key=str(os.getenv('RIOT_API_KEY'))
watcher = LolWatcher(api_key)
my_region = 'euw1'
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
	booleen = False
	if len(donnees['data']) == 1:
		#Le Streamer est en live
		if is_newlive(id_bdd, streamer_name):
			title = stream_info(streamer_name)
			title = title[0]
			post_tweet(streamer_name, title, temps_heure(), temps_jour(), name, id_bdd, booleen)
			return True
		else:
			print("%s est dans le même live" % (streamer_name))
			conn = psycopg2.connect(DATABASE_URL, sslmode='require')
			cur = conn.cursor()
			cur.execute("SELECT game_name FROM live WHERE name = '%s'" % (id_bdd))
			game_name_bdd = cur.fetchone()
			game_name_bdd = game_name_bdd[0]
			game_name = stream_info(streamer_name)
			game_name = game_name[2]
			if game_name != game_name_bdd:
				booleen = True
				cur.execute("UPDATE live SET game_name = '%s' WHERE name =  '%s' " % ((game_name), (id_bdd)),)
				conn.commit()
				conn.close()
				title = stream_info(streamer_name)
				title = title[0]
				post_tweet(streamer_name, title, temps_heure(), temps_jour(), name, id_bdd, booleen)
				return True
			else:
        		#Le Streamer n'est pas en live
				return False

def is_newlive(id_bdd, streamer_name):  
	conn = psycopg2.connect(DATABASE_URL, sslmode='require')
	cur = conn.cursor()
	cur.execute("SELECT id FROM live WHERE name = '%s'" % (id_bdd))
	stream_id_bdd = cur.fetchone()
	stream_id_bdd = stream_id_bdd[0]
	stream_id = stream_info(streamer_name)
	stream_id = stream_id[1]
	game_name = stream_info(streamer_name)
	game_name = game_name[2]
	if (int(stream_id) != stream_id_bdd):
		cur.execute("UPDATE live SET id=%d WHERE name='%s'" % (int((stream_id)), (id_bdd)),)
		cur.execute("UPDATE live SET game_name = '%s' WHERE name = '%s'" % ((game_name), (id_bdd)),)
		conn.commit()
		conn.close()
		return True
	else:
		return False

def get_live_info(streamer_name, id_bdd, name):
	stream = requests.get('https://api.twitch.tv/helix/streams?user_login=' + streamer_name, headers=headers)
	data = stream.json()
	if is_live(data, id_bdd, streamer_name, name):
		return True
	else:
		return False

def temps_heure():
	return (datetime.now()+timedelta(hours = 1)).strftime("%H:%M")

def temps_jour():
	return (datetime.now()).strftime("%d-%m-%Y")

def post_tweet(streamer_name, title, hour, day, name, id_bdd, booleen):
	conn = psycopg2.connect(DATABASE_URL, sslmode='require')
	cur = conn.cursor()
	if booleen == False:
		print(name + " a lancé un nouveau live à "+hour+" le "+day+" : \n"+title+"\ntwitch.tv/"+streamer_name)
		tweet = api.update_status(name + " a lancé un nouveau live à "+hour+" le "+day+" : \n"+title+"\ntwitch.tv/"+streamer_name)
		id_tweet = tweet.id
		cur.execute("UPDATE live SET tweet_id = %d WHERE name = '%s'" % ((id_tweet), (id_bdd)), )
		conn.commit()
		conn.close()
	elif booleen == True:
		cur.execute("SELECT tweet_id FROM live WHERE name = '%s'" % (id_bdd))
		tweet_id = cur.fetchone()
		tweet_id = tweet_id[0]
		name = name[2::]
		cur.execute("SELECT game_name FROM live WHERE name = '%s'" % (id_bdd))
		game_name = cur.fetchone()
		game_name = game_name[0]
		texte = name + " a changé de catégorie en " +game_name
		print(texte)
		tweet2 = api.update_status(status=texte, 
		                  in_reply_to_status_id=tweet_id, 
		                 auto_populate_reply_metadata=True)
		id_tweet2 = tweet2.id
		cur.execute("UPDATE live SET tweet_id = %d WHERE name = '%s'" % ((id_tweet2), (id_bdd)), )
		conn.commit()
		conn.close()


def stream_info(streamer_name):
    stream = requests.get('https://api.twitch.tv/helix/streams?user_login=' + streamer_name, headers=headers).json()['data']
    final = stream[0]
    titre = final['title']
    stream_id = final['id']
    game_name = final['game_name']
    return titre, stream_id, game_name

def dernier_tweet_lu():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur=conn.cursor()
    cur.execute("SELECT tweet_id FROM live WHERE name = 'id_tweetreply'")
    last_id = cur.fetchone()
    last_id = int(last_id[0])
    return(last_id)
def stock_dernier_tweet_lu(last_seen_id):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur=conn.cursor()
    cur.execute("UPDATE live SET id_tweetreply=(%d) WHERE name = 'id_tweetreply';" % (int(last_seen_id)),)
    conn.commit()
    conn.close()
def reply():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    reponse = " "
    i = 0
    tweets = api.mentions_timeline(count = 5, since_id = dernier_tweet_lu(),tweet_mode='extended')
    for tweet in reversed(tweets):
        if dernier_tweet_lu() != tweet.id:
            if ("kcorpnotiflive #kcorp stream") in tweet.full_text.lower():
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
                if noly():
                    reponse+="Noly "
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
                    api.update_status(""+tweet.user.screen_name+reponse+" sont en Live", in_reply_to_status_id = tweet.id)
                    stock_dernier_tweet_lu(tweet.id)
                elif i<2:
                    api.update_status(""+tweet.user.screen_name+reponse+" est en Live", in_reply_to_status_id = tweet.id)
                    stock_dernier_tweet_lu(tweet.id)

def saken():
    name = "saken_lol"
    usual_name = ".@Saken_lol"
    bdd = "id_saken"
    if get_live_info(name, bdd, usual_name):
        return True
    else:
        return False
def kameto():
    name = "kamet0"
    usual_name = ".@Kammeto"
    bdd = "id_kameto"
    if get_live_info(name, bdd, usual_name):
        return True
    else:
        return False
def kaori():
    name = "kaori123"
    usual_name = ".@KaoriLoL"
    bdd = "id_kaori"
    if get_live_info(name, bdd, usual_name):
        return True
    else:
        return False
def cabochard():
    name = "Cabochardlol"
    usual_name = ".@CabochardLoL" 
    bdd = "id_cabochard"
    if get_live_info(name, bdd, usual_name):
        return True
    else:
        return False
def skeanz():
    name = "skeanz"
    usual_name = ".@Skeanz_lol"
    bdd = "id_skeanz"
    if get_live_info(name, bdd, usual_name):
        return True
    else:
        return False
def whiteinn():
    name = "hantera1"
    usual_name = ".@Whitein15"
    bdd = "id_whiteinn"
    if get_live_info(name, bdd, usual_name):
        return True
    else:
        return False
def wao():
    name = "waolol1"
    usual_name = ".@Waolol"
    bdd = "id_wao"
    if get_live_info(name, bdd, usual_name):
        return True
    else:
        return False
def nalkya():
    name = "NalkyaLoL"
    usual_name = ".@NalkyaLoL"
    bdd = "id_nalkya"
    if get_live_info(name, bdd, usual_name):
        return True
    else:
        return False
def nerroh():
    name = "nerroh1"
    usual_name = ".@NerrohLoL"
    bdd = "id_nerroh"
    if get_live_info(name, bdd, usual_name):
        return True
    else:
        return False
def vatira():
    name = "vatira_"
    usual_name = ".@Vatira5"
    bdd = "id_vatira"
    if get_live_info(name, bdd, usual_name):
        return True
    else:
        return False
def exotiik():
    name = "exotiikrl"
    usual_name = ".@exotiikrl"
    bdd = "id_exotiik"
    if get_live_info(name, bdd, usual_name):
        return True
    else:
        return False
def itachi():
    name = "itachi_rl"
    usual_name = ".@itachi_rl"
    bdd = "id_itachi"
    if get_live_info(name, bdd, usual_name):
        return True
    else:
        return False
def eversax():
    name = "Eversax"
    usual_name = ".@Eversax"
    bdd = "id_eversax"
    if get_live_info(name, bdd, usual_name):
        return True
    else:
        return False
def bren():
    name = "bren_tm2"
    usual_name = ".@Bren_TM2"
    bdd = "id_bren"
    if get_live_info(name, bdd, usual_name):
        return True
    else:
        return False
def double61():
    name = "KC_Double61"
    usual_name = ".@TrainerDouble"
    bdd = "id_kcdouble"
    if get_live_info(name, bdd, usual_name):
        return True
    else:
        return False
def canbizz():
    name = "Canbizz_"
    usual_name = ".@Canbizz_"
    bdd = "id_canbizz"
    if get_live_info(name, bdd, usual_name):
        return True
    else:
        return False
def darker():
    name = "DarkeR_TM"
    usual_name = ".@DarkeR_TM"
    bdd = "id_darker"
    if get_live_info(name, bdd, usual_name):
        return True
    else:
        return False

def zeish():
    name = "ZE1SH"
    usual_name = ".@ZE1SHH"
    bdd = "id_zeish"
    if get_live_info(name, bdd, usual_name):
        return True
    else:
        return False

def pm():
    name = "pmleek"
    usual_name = ".@pmleek"
    bdd = "id_pm"
    if get_live_info(name, bdd, usual_name):
        return True
    else:
        return False

def nivera():
    name = "nivera"
    usual_name = ".@Nivera__"
    bdd = "id_nivera"
    if get_live_info(name, bdd, usual_name):
        return True
    else:
        return False

def newzera():
    name = "newzeraaaa"
    usual_name = ".@Newzeraaa"
    bdd = "id_newzera"
    if get_live_info(name, bdd, usual_name):
        return True
    else:
        return False

def shin():
    name = "shinsznn"
    usual_name = ".@shinVALORANT"
    bdd = "id_shin"
    if get_live_info(name, bdd, usual_name):
        return True
    else:
        return False

def scream():
	name = "scream"
	usual_name = ".@ScreaM_"
	bdd = "id_scream"
	if get_live_info(name, bdd, usual_name):
		return True
	else:
		return False

def xms51():
	name = "xms51"
	usual_name = ".@xms51"
	bdd = "id_xms51"
	if get_live_info(name, bdd, usual_name):
		return True
	else:
		return False


while True:
	saken()
	kameto()
	kaori()
	cabochard()
	#whiteinn()
	skeanz()
	wao()
	nalkya()
	eversax()
	vatira()
	itachi()
	exotiik()
	double61()
	canbizz()
	darker()
	bren()
	pm()
	zeish()
	xms51()
	scream()
	nivera()
	shin()
	newzera()
	#reply()
	time.sleep(15)

