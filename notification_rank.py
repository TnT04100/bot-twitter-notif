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

def tweet(cabo, bumm, saken, rekkles, hantera, wao):
    date = datetime.now().strftime("%d-%m-%Y")
    reponse_cabo = ""
    reponse_bumm= ""
    reponse_saken = ""
    reponse_rekkles = ""
    reponse_hantera = ""
    reponse_wao = ""
    if cabo[0] > 0:
        reponse_cabo = "Cabochard: +%dlp (%s)\n" % cabo[0], cabo[1]
    elif cabo[0] < 0:
        reponse_cabo = "Cabochard: -%dlp (%s)\n" % cabo[0], cabo[1]
    else:
        reponse_cabo = "Cabochard: 0lp (%s)\n" % cabo[1]
    if bumm[0] > 0:
        reponse_bumm = "Bumm: +%dlp (%s)\n" % bumm[0], bumm[1]
    elif bumm[0] < 0:
        reponse_bumm = "Bumm: -%dlp (%s)\n" % bumm[0], bumm[1]
    else:
        reponse_bumm = "Bumm: 0lp (%s)\n" % bumm[1]
    if saken[0] > 0:
        reponse_saken = "Saken: +%dlp (%s)\n" % saken[0], saken[1]
    elif saken[0] < 0:
        reponse_saken = "Saken: -%dlp (%s)\n" % saken[0], saken[1]
    else:
        reponse_saken = "Saken: 0lp (%s)\n" % saken[1]
    if rekkles[0] > 0:
        reponse_rekkles = "Rekkles: +%dlp (%s)\n" % rekkles[0], rekkles[1]
    elif rekkles[0] < 0:
        reponse_rekkles = "Rekkles: -%dlp (%s)\n" % rekkles[0], rekkles[1]
    else:
        reponse_rekkles = "Rekkles: 0lp (%s)\n" % rekkles[1]
    if hantera[0] > 0:
        reponse_hantera = "Hantera: +%dlp (%s)\n" % (hantera[0], hantera[1])
    elif hantera[0] < 0:
        reponse_hantera = "Hantera: -%dlp (%s)\n" % (hantera[0], hantera[1])
    else:
        reponse_hantera = "Hantera: 0lp (%s)\n" % hantera[1]
    if wao[0] > 0:
        reponse_wao = "Wao: +%dlp (%s)\n" % (wao[0], wao[1])
    elif wao[0] < 0:
        reponse_wao = "Wao: -%dlp (%s)\n" % (wao[0], wao[1])
    else:
        reponse_wao = "Wao: 0lp (%s)\n" % wao[1]
    print(reponse_wao+reponse_hantera+reponse_rekkles+reponse_saken+reponse_bumm+reponse_cabo)
    api.update_status(date + "\n" + reponse_cabo + reponse_bumm + reponse_saken + reponse_rekkles + reponse_hantera + reponse_wao)



def cabochard():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur=conn.cursor()
    cur.execute("SELECT id FROM kcorp WHERE name='Cabochard';")
    player_id = cur.fetchone()
    my_ranked_stats = watcher.league.by_summoner(my_region, player_id)
    test = my_ranked_stats[0]
    test = json.dumps(test)
    test = json.loads(test)
    tier = test['tier']
    rank = test['rank']
    leaguePoints = test['leaguePoints']
    cur.execute("SELECT daily_lp FROM kcorp WHERE name='Cabochard';")
    lp = cur.fetchone()
    diff = int(leaguePoints) - lp[0]
    cur.execute("UPDATE kcorp SET daily_lp=(%d) WHERE name='Cabochard';" % int(leaguePoints))
    conn.commit()
    conn.close()
    return(diff, tier)

def bumm():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur=conn.cursor()
    cur.execute("SELECT id FROM kcorp WHERE name='Bumm';")
    player_id = cur.fetchone()
    my_ranked_stats = watcher.league.by_summoner(my_region, player_id)
    test = my_ranked_stats[0]
    test = json.dumps(test)
    test = json.loads(test)
    tier = test['tier']
    rank = test['rank']
    leaguePoints = test['leaguePoints']
    cur.execute("SELECT daily_lp FROM kcorp WHERE name='Bumm';")
    lp = cur.fetchone()
    diff = int(leaguePoints) - lp[0] 
    cur.execute("UPDATE kcorp SET daily_lp=(%d) WHERE name='Bumm';" % int(leaguePoints))
    conn.commit()
    conn.close()
    return(diff, tier)

def saken():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur=conn.cursor()
    cur.execute("SELECT id FROM kcorp WHERE name='Saken';")
    player_id = cur.fetchone()
    my_ranked_stats = watcher.league.by_summoner(my_region, player_id)
    test = my_ranked_stats[0]
    test = json.dumps(test)
    test = json.loads(test)
    tier = test['tier']
    rank = test['rank']
    leaguePoints = test['leaguePoints']
    cur.execute("SELECT daily_lp FROM kcorp WHERE name='Saken';")
    lp = cur.fetchone()
    diff = int(leaguePoints) - lp[0]
    cur.execute("UPDATE kcorp SET daily_lp=(%d) WHERE name='Saken';" % int(leaguePoints))
    conn.commit()
    conn.close()
    return(diff, tier)

def rekkles():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur=conn.cursor()
    cur.execute("SELECT id FROM kcorp WHERE name='Rekkles';")
    player_id = cur.fetchone()
    my_ranked_stats = watcher.league.by_summoner(my_region, player_id)
    test = my_ranked_stats[0]
    test = json.dumps(test)
    test = json.loads(test)
    tier = test['tier']
    rank = test['rank']
    leaguePoints = test['leaguePoints']
    cur.execute("SELECT daily_lp FROM kcorp WHERE name='Rekkles';")
    lp = cur.fetchone()
    diff = int(leaguePoints) - lp[0]
    cur.execute("UPDATE kcorp SET daily_lp=(%d) WHERE name='Rekkles';" % int(leaguePoints))
    conn.commit()
    conn.close()
    return(diff, tier)

def hantera():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur=conn.cursor()
    cur.execute("SELECT id FROM kcorp WHERE name='Hantera';")
    player_id = cur.fetchone()
    my_ranked_stats = watcher.league.by_summoner(my_region, player_id)
    test = my_ranked_stats[0]
    test = json.dumps(test)
    test = json.loads(test)
    tier = test['tier']
    rank = test['rank']
    leaguePoints = test['leaguePoints']
    cur.execute("SELECT daily_lp FROM kcorp WHERE name='Hantera';")
    lp = cur.fetchone()
    diff = int(leaguePoints) - lp[0]
    cur.execute("UPDATE kcorp SET daily_lp=(%d) WHERE name='Hantera';" % int(leaguePoints))
    conn.commit()
    conn.close()
    return(diff, tier)

def wao():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur=conn.cursor()
    cur.execute("SELECT id FROM kcorp WHERE name='Wao';")
    player_id = cur.fetchone()
    my_ranked_stats = watcher.league.by_summoner(my_region, player_id)
    test = my_ranked_stats[0]
    test = json.dumps(test)
    test = json.loads(test)
    tier = test['tier']
    rank = test['rank']
    leaguePoints = test['leaguePoints']
    cur.execute("SELECT daily_lp FROM kcorp WHERE name='Wao';")
    lp = cur.fetchone()
    diff = int(leaguePoints) - lp[0]
    cur.execute("UPDATE kcorp SET daily_lp=(%d) WHERE name='Wao';" % int(leaguePoints))
    conn.commit()
    conn.close()
    return(diff, tier)

cabochard()
bumm()
saken()
rekkles()
hantera()
wao()
tweet(cabochard(),bumm(),saken(),rekkles(),hantera(),wao())

